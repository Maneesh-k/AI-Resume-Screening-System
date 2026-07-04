from __future__ import annotations

import uuid

import structlog

from src.config import get_settings
from src.domain.entities.candidate import (
    Candidate,
    CandidateEducation,
    CandidateExperience,
    CandidateScore,
    CandidateSkill,
    ProcessingStatus,
)
from src.infrastructure.ai.openai_client import get_embedding
from src.infrastructure.ai.resume_parser import (
    extract_text,
    generate_summary,
    parse_resume,
    score_candidate,
)
from src.infrastructure.database.repositories.candidate_repository_impl import CandidateRepositoryImpl
from src.infrastructure.database.repositories.job_repository_impl import JobRepositoryImpl
from src.infrastructure.database.session import AsyncSessionLocal
from src.infrastructure.storage.s3_client import download_file
from src.infrastructure.vector_db.pinecone_client import upsert_vector

log = structlog.get_logger()
settings = get_settings()


async def process_resume_inline(
    candidate_id: str,
    job_id: str,
    file_bytes: bytes,
    content_type: str,
) -> None:
    """Process a resume inline (used when SQS is not configured, e.g. local dev)."""
    async with AsyncSessionLocal() as session:
        candidate_repo = CandidateRepositoryImpl(session)
        job_repo = JobRepositoryImpl(session)

        candidate = await candidate_repo.get_by_id(uuid.UUID(candidate_id))
        job = await job_repo.get_by_id(uuid.UUID(job_id))

        if not candidate or not job:
            log.error("process_resume_not_found", candidate_id=candidate_id)
            return

        await _process(candidate, job, file_bytes, content_type, candidate_repo, session)


async def process_resume_from_sqs(message: dict) -> None:
    """Process a resume from an SQS message payload."""
    candidate_id = message["candidate_id"]
    job_id = message["job_id"]
    s3_key = message["s3_key"]
    content_type = message["content_type"]

    async with AsyncSessionLocal() as session:
        candidate_repo = CandidateRepositoryImpl(session)
        job_repo = JobRepositoryImpl(session)

        candidate = await candidate_repo.get_by_id(uuid.UUID(candidate_id))
        job = await job_repo.get_by_id(uuid.UUID(job_id))

        if not candidate or not job:
            log.error("process_resume_not_found", candidate_id=candidate_id)
            return

        file_bytes = await download_file(s3_key)
        await _process(candidate, job, file_bytes, content_type, candidate_repo, session)


async def _process(candidate, job, file_bytes, content_type, candidate_repo, session) -> None:
    log.info("resume_processing_started", candidate_id=str(candidate.id))

    # Mark as processing
    candidate.mark_processing()
    await candidate_repo.update(candidate)
    await session.commit()

    try:
        # Step 1: Extract text
        import asyncio
        resume_text = await asyncio.to_thread(extract_text, file_bytes, content_type)
        if not resume_text or len(resume_text.strip()) < 50:
            raise ValueError("Could not extract meaningful text from resume")

        # Step 2: Parse structured data
        parsed = await parse_resume(resume_text)

        # Step 3: Populate candidate from parsed data
        candidate.resume_text = resume_text
        candidate.parsed_data = parsed
        candidate.name = parsed.get("candidate_name")
        candidate.email = parsed.get("email")
        candidate.phone = parsed.get("phone")
        candidate.experience_years = parsed.get("experience_years")
        candidate.current_title = parsed.get("current_title")
        candidate.current_company = parsed.get("current_company")
        candidate.certifications = parsed.get("certifications", [])

        candidate.skills = [
            CandidateSkill(name=s)
            for s in parsed.get("skills", [])
            if isinstance(s, str) and s.strip()
        ]

        candidate.experience = [
            CandidateExperience(
                company=e.get("company"),
                title=e.get("title"),
                start_date=e.get("start_date"),
                end_date=e.get("end_date"),
                is_current=e.get("is_current", False),
                description=e.get("description"),
            )
            for e in parsed.get("experience", [])
        ]

        candidate.education = [
            CandidateEducation(
                institution=e.get("institution"),
                degree=e.get("degree"),
                field=e.get("field"),
                graduation_year=e.get("graduation_year"),
            )
            for e in parsed.get("education", [])
        ]

        # Step 4: Generate embedding
        embedding_text = f"{resume_text[:5000]}\nSkills: {', '.join(candidate.skill_names)}"
        embedding = await get_embedding(embedding_text)

        # Step 5: Score candidate against job
        score_data = await score_candidate(
            resume_text=resume_text,
            job_description=job.description,
            required_skills=job.required_skills,
        )

        # Step 6: Generate AI summary
        ai_summary = await generate_summary(
            resume_text=resume_text,
            job_title=job.title,
            job_description=job.description,
        )

        # Step 7: Store in Pinecone
        vector_id = f"resume_{candidate.id}"
        await upsert_vector(
            vector_id=vector_id,
            vector=embedding,
            metadata={
                "type": "resume",
                "candidate_id": str(candidate.id),
                "job_id": str(candidate.job_id),
                "name": candidate.name or "",
                "experience_years": candidate.experience_years or 0,
                "skills": candidate.skill_names[:20],
                "overall_score": score_data.get("overall_score", 0),
            },
            namespace=settings.pinecone_namespace_resumes,
        )
        candidate.pinecone_vector_id = vector_id

        # Step 8: Save score to DB
        score = CandidateScore(
            job_id=candidate.job_id,
            overall_score=score_data.get("overall_score", 0),
            skill_score=score_data.get("skill_score"),
            experience_score=score_data.get("experience_score"),
            domain_score=score_data.get("domain_score"),
            education_score=score_data.get("education_score"),
            certification_score=score_data.get("certification_score"),
            ai_confidence=score_data.get("ai_confidence"),
            ai_summary=ai_summary,
            skill_gaps=score_data.get("skill_gaps", []),
            score_justification=score_data.get("score_justification"),
            recommendation=score_data.get("recommendation"),
            model_version=settings.openai_llm_model,
        )
        await candidate_repo.upsert_score(candidate.id, score)

        # Step 9: Mark as processed
        candidate.mark_processed()
        await candidate_repo.update(candidate)
        await session.commit()

        log.info(
            "resume_processing_complete",
            candidate_id=str(candidate.id),
            overall_score=score.overall_score,
        )

    except Exception as e:
        log.error("resume_processing_failed", candidate_id=str(candidate.id), error=str(e))
        candidate.mark_failed(str(e))
        await candidate_repo.update(candidate)
        await session.commit()


async def main() -> None:
    """SQS consumer loop."""
    import asyncio
    import json

    import boto3

    from src.infrastructure.cache.redis_client import RedisClient

    settings_obj = get_settings()
    await RedisClient.initialize(settings_obj.redis_url)

    sqs = boto3.client("sqs", region_name=settings_obj.aws_region)
    log.info("worker_started", queue=settings_obj.aws_sqs_queue_url)

    while True:
        try:
            response = sqs.receive_message(
                QueueUrl=settings_obj.aws_sqs_queue_url,
                MaxNumberOfMessages=5,
                WaitTimeSeconds=20,
                VisibilityTimeout=300,
            )
            messages = response.get("Messages", [])

            for msg in messages:
                try:
                    payload = json.loads(msg["Body"])
                    await process_resume_from_sqs(payload)
                    sqs.delete_message(
                        QueueUrl=settings_obj.aws_sqs_queue_url,
                        ReceiptHandle=msg["ReceiptHandle"],
                    )
                except Exception as e:
                    log.error("worker_message_failed", error=str(e))

        except Exception as e:
            log.error("worker_loop_error", error=str(e))
            await asyncio.sleep(5)
