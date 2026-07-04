from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.candidate import Candidate, CandidateScore, ProcessingStatus


class CandidateRepository(ABC):
    @abstractmethod
    async def get_by_id(self, candidate_id: UUID) -> Candidate | None: ...

    @abstractmethod
    async def list_by_job(
        self,
        job_id: UUID,
        *,
        status: ProcessingStatus | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Candidate], int]: ...

    @abstractmethod
    async def create(self, candidate: Candidate) -> Candidate: ...

    @abstractmethod
    async def update(self, candidate: Candidate) -> Candidate: ...

    @abstractmethod
    async def delete(self, candidate_id: UUID) -> None: ...

    @abstractmethod
    async def get_score(self, candidate_id: UUID, job_id: UUID) -> CandidateScore | None: ...

    @abstractmethod
    async def upsert_score(self, candidate_id: UUID, score: CandidateScore) -> CandidateScore: ...

    @abstractmethod
    async def list_ranked_by_job(
        self,
        job_id: UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[tuple[Candidate, CandidateScore]]: ...
