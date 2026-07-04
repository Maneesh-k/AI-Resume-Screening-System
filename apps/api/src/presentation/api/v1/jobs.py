from __future__ import annotations

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.job import Job, JobStatus
from src.infrastructure.ai.openai_client import get_embedding
from src.infrastructure.database.repositories.job_repository_impl import JobRepositoryImpl
from src.infrastructure.database.repositories.candidate_repository_impl import CandidateRepositoryImpl
from src.infrastructure.database.session import get_db
from src.infrastructure.vector_db.pinecone_client import upsert_vector, delete_vector
from src.config import get_settings
from src.presentation.dependencies import CurrentUser
from src.presentation.schemas.common import PaginatedResponse
from src.presentation.schemas.job import CreateJobRequest, JobResponse, UpdateJobRequest
from src.presentation.schemas.candidate import RankedCandidateResponse, CandidateResponse, ScoreBreakdownResponse, CandidateSkillResponse, CandidateExperienceResponse, CandidateEducationResponse

router = APIRouter()
log = structlog.get_logger()
settings = get_settings()

DbSession = Annotated[AsyncSession, Depends(get_db)]


def _job_to_response(job: Job, candidate_count: int = 0) -> JobResponse:
    return JobResponse(
        id=job.id,
        title=job.title,
        department=job.department,
        description=job.description,
        required_skills=job.required_skills,
        preferred_skills=job.preferred_skills,
        experience_min=job.experience_min,
        experience_max=job.experience_max,
        location=job.location,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        currency=job.currency,
        status=job.status.value,
        created_by=job.created_by,
        created_at=job.created_at,
        updated_at=job.updated_at,
        candidate_count=candidate_count,
    )


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(body: CreateJobRequest, current_user: CurrentUser, db: DbSession) -> JobResponse:
    if not current_user.can_create_jobs():
        raise HTTPException(status_code=403, detail="Insufficient permissions to create jobs")

    job = Job(
        id=uuid.uuid4(),
        title=body.title,
        description=body.description,
        created_by=current_user.id,
        department=body.department,
        required_skills=body.required_skills,
        preferred_skills=body.preferred_skills,
        experience_min=body.experience_min,
        experience_max=body.experience_max,
        location=body.location,
        salary_min=body.salary_min,
        salary_max=body.salary_max,
        currency=body.currency,
    )

    repo = JobRepositoryImpl(db)
    created = await repo.create(job)

    # Generate and store JD embedding in Pinecone (non-blocking)
    try:
        jd_text = f"{body.title}\n{body.description}\nSkills: {', '.join(body.required_skills)}"
        embedding = await get_embedding(jd_text)
        vector_id = f"job_{created.id}"
        await upsert_vector(
            vector_id=vector_id,
            vector=embedding,
            metadata={
                "type": "job",
                "job_id": str(created.id),
                "title": created.title,
                "status": "open",
            },
            namespace=settings.pinecone_namespace_jobs,
        )
        created.pinecone_vector_id = vector_id
        await repo.update(created)
    except Exception as e:
        log.warning("job_embedding_failed", job_id=str(created.id), error=str(e))

    log.info("job_created", job_id=str(created.id), user_id=str(current_user.id))
    return _job_to_response(created)


@router.get("", response_model=PaginatedResponse[JobResponse])
async def list_jobs(
    current_user: CurrentUser,
    db: DbSession,
    status: str | None = Query(default=None, pattern="^(open|closed|draft)$"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> PaginatedResponse[JobResponse]:
    repo = JobRepositoryImpl(db)
    offset = (page - 1) * limit
    job_status = JobStatus(status) if status else None
    jobs, total = await repo.list(status=job_status, offset=offset, limit=limit)
    items = [_job_to_response(j) for j in jobs]
    return PaginatedResponse.create(items=items, total=total, offset=offset, limit=limit)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: uuid.UUID, current_user: CurrentUser, db: DbSession) -> JobResponse:
    repo = JobRepositoryImpl(db)
    job = await repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_to_response(job)


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: uuid.UUID, body: UpdateJobRequest, current_user: CurrentUser, db: DbSession
) -> JobResponse:
    repo = JobRepositoryImpl(db)
    job = await repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.created_by != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this job")

    if body.title is not None:
        job.title = body.title
    if body.description is not None:
        job.description = body.description
    if body.department is not None:
        job.department = body.department
    if body.required_skills is not None:
        job.required_skills = body.required_skills
    if body.preferred_skills is not None:
        job.preferred_skills = body.preferred_skills
    if body.experience_min is not None:
        job.experience_min = body.experience_min
    if body.experience_max is not None:
        job.experience_max = body.experience_max
    if body.location is not None:
        job.location = body.location
    if body.salary_min is not None:
        job.salary_min = body.salary_min
    if body.salary_max is not None:
        job.salary_max = body.salary_max
    if body.status is not None:
        job.status = JobStatus(body.status)

    updated = await repo.update(job)
    return _job_to_response(updated)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: uuid.UUID, current_user: CurrentUser, db: DbSession) -> None:
    repo = JobRepositoryImpl(db)
    job = await repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.created_by != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    await repo.delete(job_id)

    if job.pinecone_vector_id:
        try:
            await delete_vector(job.pinecone_vector_id, settings.pinecone_namespace_jobs)
        except Exception:
            pass

    log.info("job_deleted", job_id=str(job_id))


@router.get("/{job_id}/candidates", response_model=list[RankedCandidateResponse])
async def get_ranked_candidates(
    job_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[RankedCandidateResponse]:
    job_repo = JobRepositoryImpl(db)
    job = await job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    candidate_repo = CandidateRepositoryImpl(db)
    ranked = await candidate_repo.list_ranked_by_job(job_id, limit=limit, offset=offset)

    result = []
    for i, (candidate, score) in enumerate(ranked):
        candidate_response = CandidateResponse(
            id=candidate.id,
            job_id=candidate.job_id,
            name=candidate.name,
            email=candidate.email,
            phone=candidate.phone,
            experience_years=candidate.experience_years,
            current_title=candidate.current_title,
            current_company=candidate.current_company,
            skills=[CandidateSkillResponse(name=s.name, proficiency=s.proficiency, years=s.years) for s in candidate.skills],
            experience=[CandidateExperienceResponse(company=e.company, title=e.title, start_date=e.start_date, end_date=e.end_date, is_current=e.is_current) for e in candidate.experience],
            education=[CandidateEducationResponse(institution=ed.institution, degree=ed.degree, field=ed.field, graduation_year=ed.graduation_year) for ed in candidate.education],
            certifications=candidate.certifications,
            processing_status=candidate.processing_status.value,
            score=ScoreBreakdownResponse(
                overall_score=score.overall_score,
                skill_score=score.skill_score,
                experience_score=score.experience_score,
                domain_score=score.domain_score,
                education_score=score.education_score,
                certification_score=score.certification_score,
                ai_confidence=score.ai_confidence,
                ai_summary=score.ai_summary,
                skill_gaps=score.skill_gaps,
                score_justification=score.score_justification,
                recommendation=score.recommendation,
            ),
            created_at=candidate.created_at,
        )
        result.append(
            RankedCandidateResponse(
                rank=offset + i + 1,
                candidate=candidate_response,
                overall_score=score.overall_score,
                recommendation=score.recommendation,
                skill_gaps=score.skill_gaps,
                ai_summary=score.ai_summary,
            )
        )
    return result
