from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.repositories.candidate_repository_impl import CandidateRepositoryImpl
from src.infrastructure.database.session import get_db
from src.presentation.dependencies import CurrentUser
from src.presentation.schemas.candidate import CandidateResponse, ScoreBreakdownResponse, CandidateSkillResponse, CandidateExperienceResponse, CandidateEducationResponse

router = APIRouter()
DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: uuid.UUID, current_user: CurrentUser, db: DbSession
) -> CandidateResponse:
    repo = CandidateRepositoryImpl(db)
    candidate = await repo.get_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    score = await repo.get_score(candidate_id, candidate.job_id)
    score_response = None
    if score:
        score_response = ScoreBreakdownResponse(
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
        )

    return CandidateResponse(
        id=candidate.id,
        job_id=candidate.job_id,
        name=candidate.name,
        email=candidate.email,
        phone=candidate.phone,
        experience_years=candidate.experience_years,
        current_title=candidate.current_title,
        current_company=candidate.current_company,
        skills=[CandidateSkillResponse(name=s.name, proficiency=s.proficiency, years=s.years) for s in candidate.skills],
        experience=[CandidateExperienceResponse(company=e.company, title=e.title, start_date=e.start_date, end_date=e.end_date, is_current=e.is_current, description=e.description) for e in candidate.experience],
        education=[CandidateEducationResponse(institution=ed.institution, degree=ed.degree, field=ed.field, graduation_year=ed.graduation_year) for ed in candidate.education],
        certifications=candidate.certifications,
        processing_status=candidate.processing_status.value,
        score=score_response,
        created_at=candidate.created_at,
    )


@router.delete("/{candidate_id}", status_code=204)
async def delete_candidate(
    candidate_id: uuid.UUID, current_user: CurrentUser, db: DbSession
) -> None:
    repo = CandidateRepositoryImpl(db)
    candidate = await repo.get_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    await repo.delete(candidate_id)
