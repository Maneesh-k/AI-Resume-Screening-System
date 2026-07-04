from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.job import Job, JobStatus


class JobRepository(ABC):
    @abstractmethod
    async def get_by_id(self, job_id: UUID) -> Job | None: ...

    @abstractmethod
    async def list(
        self,
        *,
        created_by: UUID | None = None,
        status: JobStatus | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Job], int]: ...

    @abstractmethod
    async def create(self, job: Job) -> Job: ...

    @abstractmethod
    async def update(self, job: Job) -> Job: ...

    @abstractmethod
    async def delete(self, job_id: UUID) -> None: ...
