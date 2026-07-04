from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


@dataclass
class CandidateExperience:
    company: str
    title: str
    start_date: str | None = None
    end_date: str | None = None
    is_current: bool = False
    description: str | None = None
    duration_months: int | None = None


@dataclass
class CandidateEducation:
    institution: str
    degree: str | None = None
    field: str | None = None
    graduation_year: int | None = None
    gpa: float | None = None


@dataclass
class CandidateSkill:
    name: str
    proficiency: str | None = None  # beginner | intermediate | expert
    years: float | None = None


@dataclass
class CandidateScore:
    job_id: UUID
    overall_score: float
    skill_score: float | None = None
    experience_score: float | None = None
    domain_score: float | None = None
    education_score: float | None = None
    certification_score: float | None = None
    ai_confidence: float | None = None
    ai_summary: str | None = None
    skill_gaps: list[str] = field(default_factory=list)
    score_justification: str | None = None
    recommendation: str | None = None
    model_version: str | None = None
    scored_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Candidate:
    id: UUID
    job_id: UUID
    resume_s3_key: str
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    resume_text: str | None = None
    parsed_data: dict | None = None  # raw LLM output
    experience_years: float | None = None
    current_title: str | None = None
    current_company: str | None = None
    skills: list[CandidateSkill] = field(default_factory=list)
    experience: list[CandidateExperience] = field(default_factory=list)
    education: list[CandidateEducation] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    pinecone_vector_id: str | None = None
    processing_error: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def mark_processing(self) -> None:
        self.processing_status = ProcessingStatus.PROCESSING
        self.updated_at = datetime.utcnow()

    def mark_processed(self) -> None:
        self.processing_status = ProcessingStatus.PROCESSED
        self.updated_at = datetime.utcnow()

    def mark_failed(self, error: str) -> None:
        self.processing_status = ProcessingStatus.FAILED
        self.processing_error = error
        self.updated_at = datetime.utcnow()

    @property
    def skill_names(self) -> list[str]:
        return [s.name for s in self.skills]
