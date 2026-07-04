from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CandidateSkillResponse(BaseModel):
    name: str
    proficiency: str | None = None
    years: float | None = None


class CandidateExperienceResponse(BaseModel):
    company: str | None = None
    title: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    is_current: bool = False
    description: str | None = None


class CandidateEducationResponse(BaseModel):
    institution: str | None = None
    degree: str | None = None
    field: str | None = None
    graduation_year: int | None = None


class ScoreBreakdownResponse(BaseModel):
    overall_score: float
    skill_score: float | None = None
    experience_score: float | None = None
    domain_score: float | None = None
    education_score: float | None = None
    certification_score: float | None = None
    ai_confidence: float | None = None
    ai_summary: str | None = None
    skill_gaps: list[str] = []
    score_justification: str | None = None
    recommendation: str | None = None
    strengths: list[str] = []
    concerns: list[str] = []


class CandidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    experience_years: float | None = None
    current_title: str | None = None
    current_company: str | None = None
    skills: list[CandidateSkillResponse] = []
    experience: list[CandidateExperienceResponse] = []
    education: list[CandidateEducationResponse] = []
    certifications: list[str] = []
    processing_status: str
    score: ScoreBreakdownResponse | None = None
    resume_url: str | None = None
    created_at: datetime


class RankedCandidateResponse(BaseModel):
    rank: int
    candidate: CandidateResponse
    overall_score: float
    recommendation: str | None = None
    skill_gaps: list[str] = []
    ai_summary: str | None = None


class UploadResumeResponse(BaseModel):
    candidate_id: UUID
    status: str
    message: str


class ProcessingStatusResponse(BaseModel):
    candidate_id: UUID
    status: str
    progress_pct: int = 0
    error: str | None = None


class InterviewQuestionResponse(BaseModel):
    type: str
    question: str
    rationale: str | None = None
    difficulty: str | None = None


class SkillGapResponse(BaseModel):
    required_skills: list[str]
    candidate_skills: list[str]
    missing_skills: list[str]
    matching_skills: list[str]
    match_percentage: float
