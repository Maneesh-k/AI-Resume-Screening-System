from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateJobRequest(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=50)
    department: str | None = Field(default=None, max_length=255)
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    experience_min: int | None = Field(default=None, ge=0, le=50)
    experience_max: int | None = Field(default=None, ge=0, le=50)
    location: str | None = Field(default=None, max_length=255)
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    currency: str = Field(default="USD", max_length=10)


class UpdateJobRequest(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = Field(default=None, min_length=50)
    department: str | None = None
    required_skills: list[str] | None = None
    preferred_skills: list[str] | None = None
    experience_min: int | None = None
    experience_max: int | None = None
    location: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    status: str | None = Field(default=None, pattern="^(open|closed|draft)$")


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    department: str | None
    description: str
    required_skills: list[str]
    preferred_skills: list[str]
    experience_min: int | None
    experience_max: int | None
    location: str | None
    salary_min: int | None
    salary_max: int | None
    currency: str
    status: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    candidate_count: int = 0
