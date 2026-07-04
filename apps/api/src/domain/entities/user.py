from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID


class UserRole(str, Enum):
    ADMIN = "admin"
    RECRUITER = "recruiter"
    HIRING_MANAGER = "hiring_manager"


@dataclass
class User:
    id: UUID
    email: str
    name: str
    role: UserRole
    hashed_password: str
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def can_create_jobs(self) -> bool:
        return self.role in (UserRole.ADMIN, UserRole.RECRUITER)

    def can_upload_resumes(self) -> bool:
        return self.role in (UserRole.ADMIN, UserRole.RECRUITER)

    def can_manage_users(self) -> bool:
        return self.role == UserRole.ADMIN

    def can_view_candidates(self) -> bool:
        return self.is_active
