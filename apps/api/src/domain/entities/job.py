from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID


class JobStatus(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"


@dataclass
class Job:
    id: UUID
    title: str
    description: str
    created_by: UUID
    department: str | None = None
    required_skills: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    experience_min: int | None = None
    experience_max: int | None = None
    location: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    currency: str = "USD"
    status: JobStatus = JobStatus.OPEN
    pinecone_vector_id: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def all_skills(self) -> list[str]:
        return list(set(self.required_skills + self.preferred_skills))

    def close(self) -> None:
        self.status = JobStatus.CLOSED
        self.updated_at = datetime.utcnow()

    def reopen(self) -> None:
        self.status = JobStatus.OPEN
        self.updated_at = datetime.utcnow()
