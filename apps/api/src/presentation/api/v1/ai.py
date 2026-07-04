from __future__ import annotations

import json
import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.infrastructure.ai.resume_parser import generate_summary, generate_interview_questions, score_candidate
from src.infrastructure.cache.redis_client import cache_get, cache_set
from src.infrastructure.database.repositories.candidate_repository_impl import CandidateRepositoryImpl
from src.infrastructure.database.repositories.job_repository_impl import JobRepositoryImpl
from src.infrastructure.database.session import get_db
from src.presentation.dependencies import CurrentUser
from src.presentation.schemas.candidate import (
    InterviewQuestionResponse,
    SkillGapResponse,
    ScoreBreakdownResponse,
)

router = APIRouter()
log = structlog.get_logger()
settings = get_settings()

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.post("/score")
async def score_candidate_endpoint(
    current_user: CurrentUser,
    db: DbSession,
    candidate_id: uuid.UUID = ...,
    job_id: uuid.UUID = ...,
) -> ScoreBreakdownResponse:
    cache_key = f"score:{candidate_id}:{job_id}"
    cached = await cache_get(cache_key)
    if cached:
        return ScoreBreakdownResponse(**cached)

    candidate_repo = CandidateRepositoryImpl(db)
    job_repo = JobRepositoryImpl(db)

    candidate = await candidate_repo.get_by_id(candidate_id)
    job = await job_repo.get_by_id(job_id)

    if not candidate or not job:
        raise HTTPException(status_code=404, detail="Candidate or job not found")
    if not candidate.resume_text:
        raise HTTPException(status_code=422, detail="Resume not yet processed")

    result = await score_candidate(
        resume_text=candidate.resume_text,
        job_description=job.description,
        required_skills=job.required_skills,
    )

    response = ScoreBreakdownResponse(
        overall_score=result.get("overall_score", 0),
        skill_score=result.get("skill_score"),
        experience_score=result.get("experience_score"),
        domain_score=result.get("domain_score"),
        education_score=result.get("education_score"),
        certification_score=result.get("certification_score"),
        ai_confidence=result.get("ai_confidence"),
        skill_gaps=result.get("skill_gaps", []),
        score_justification=result.get("score_justification"),
        recommendation=result.get("recommendation"),
        strengths=result.get("strengths", []),
        concerns=result.get("concerns", []),
    )

    await cache_set(cache_key, response.model_dump(), settings.redis_cache_ttl_ai)
    return response


@router.post("/summary")
async def generate_summary_endpoint(
    current_user: CurrentUser,
    db: DbSession,
    candidate_id: uuid.UUID = ...,
    job_id: uuid.UUID = ...,
) -> StreamingResponse:
    cache_key = f"summary:{candidate_id}:{job_id}"
    cached = await cache_get(cache_key)

    candidate_repo = CandidateRepositoryImpl(db)
    job_repo = JobRepositoryImpl(db)
    candidate = await candidate_repo.get_by_id(candidate_id)
    job = await job_repo.get_by_id(job_id)

    if not candidate or not job:
        raise HTTPException(status_code=404, detail="Not found")
    if not candidate.resume_text:
        raise HTTPException(status_code=422, detail="Resume not yet processed")

    async def stream_summary() -> AsyncGenerator[str, None]:
        if cached:
            yield f"data: {json.dumps({'type': 'summary', 'content': cached['summary']})}\n\n"
            yield "data: {\"type\": \"done\"}\n\n"
            return

        summary = await generate_summary(
            resume_text=candidate.resume_text or "",
            job_title=job.title,
            job_description=job.description,
        )
        await cache_set(cache_key, {"summary": summary}, settings.redis_cache_ttl_ai)
        yield f"data: {json.dumps({'type': 'summary', 'content': summary})}\n\n"
        yield "data: {\"type\": \"done\"}\n\n"

    return StreamingResponse(stream_summary(), media_type="text/event-stream")


@router.post("/questions", response_model=list[InterviewQuestionResponse])
async def generate_questions_endpoint(
    current_user: CurrentUser,
    db: DbSession,
    candidate_id: uuid.UUID = ...,
    job_id: uuid.UUID = ...,
) -> list[InterviewQuestionResponse]:
    cache_key = f"questions:{candidate_id}:{job_id}"
    cached = await cache_get(cache_key)
    if cached:
        return [InterviewQuestionResponse(**q) for q in cached]

    candidate_repo = CandidateRepositoryImpl(db)
    job_repo = JobRepositoryImpl(db)
    candidate = await candidate_repo.get_by_id(candidate_id)
    job = await job_repo.get_by_id(job_id)

    if not candidate or not job:
        raise HTTPException(status_code=404, detail="Not found")
    if not candidate.resume_text:
        raise HTTPException(status_code=422, detail="Resume not yet processed")

    questions = await generate_interview_questions(
        resume_text=candidate.resume_text,
        job_title=job.title,
        job_description=job.description,
    )

    await cache_set(cache_key, questions, settings.redis_cache_ttl_ai)
    return [InterviewQuestionResponse(**q) for q in questions]


@router.post("/skill-gap", response_model=SkillGapResponse)
async def skill_gap_endpoint(
    current_user: CurrentUser,
    db: DbSession,
    candidate_id: uuid.UUID = ...,
    job_id: uuid.UUID = ...,
) -> SkillGapResponse:
    candidate_repo = CandidateRepositoryImpl(db)
    job_repo = JobRepositoryImpl(db)
    candidate = await candidate_repo.get_by_id(candidate_id)
    job = await job_repo.get_by_id(job_id)

    if not candidate or not job:
        raise HTTPException(status_code=404, detail="Not found")

    candidate_skill_names = {s.name.lower() for s in candidate.skills}
    required = [s for s in job.required_skills]
    missing = [s for s in required if s.lower() not in candidate_skill_names]
    matching = [s for s in required if s.lower() in candidate_skill_names]
    match_pct = (len(matching) / len(required) * 100) if required else 0.0

    return SkillGapResponse(
        required_skills=required,
        candidate_skills=[s.name for s in candidate.skills],
        missing_skills=missing,
        matching_skills=matching,
        match_percentage=round(match_pct, 1),
    )
