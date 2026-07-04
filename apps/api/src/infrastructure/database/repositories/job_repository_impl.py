from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.job import Job, JobStatus
from src.domain.repositories.job_repository import JobRepository
from src.infrastructure.database.models.job import JobModel


class JobRepositoryImpl(JobRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: JobModel) -> Job:
        return Job(
            id=model.id,
            title=model.title,
            description=model.description,
            created_by=model.created_by,
            department=model.department,
            required_skills=model.required_skills or [],
            preferred_skills=model.preferred_skills or [],
            experience_min=model.experience_min,
            experience_max=model.experience_max,
            location=model.location,
            salary_min=model.salary_min,
            salary_max=model.salary_max,
            currency=model.currency,
            status=JobStatus(model.status),
            pinecone_vector_id=model.pinecone_vector_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, job_id: UUID) -> Job | None:
        result = await self._session.execute(select(JobModel).where(JobModel.id == job_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list(
        self,
        *,
        created_by: UUID | None = None,
        status: JobStatus | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Job], int]:
        query = select(JobModel)
        if created_by:
            query = query.where(JobModel.created_by == created_by)
        if status:
            query = query.where(JobModel.status == status.value)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(JobModel.created_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(query)
        models = result.scalars().all()

        return [self._to_entity(m) for m in models], total

    async def create(self, job: Job) -> Job:
        model = JobModel(
            id=job.id,
            title=job.title,
            description=job.description,
            created_by=job.created_by,
            department=job.department,
            required_skills=job.required_skills,
            preferred_skills=job.preferred_skills,
            experience_min=job.experience_min,
            experience_max=job.experience_max,
            location=job.location,
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            currency=job.currency,
            status=job.status.value,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, job: Job) -> Job:
        result = await self._session.execute(select(JobModel).where(JobModel.id == job.id))
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Job {job.id} not found")
        model.title = job.title
        model.description = job.description
        model.department = job.department
        model.required_skills = job.required_skills
        model.preferred_skills = job.preferred_skills
        model.experience_min = job.experience_min
        model.experience_max = job.experience_max
        model.location = job.location
        model.salary_min = job.salary_min
        model.salary_max = job.salary_max
        model.currency = job.currency
        model.status = job.status.value
        model.pinecone_vector_id = job.pinecone_vector_id
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, job_id: UUID) -> None:
        result = await self._session.execute(select(JobModel).where(JobModel.id == job_id))
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
