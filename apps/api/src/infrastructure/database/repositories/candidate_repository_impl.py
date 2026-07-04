from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.candidate import (
    Candidate,
    CandidateEducation,
    CandidateExperience,
    CandidateScore,
    CandidateSkill,
    ProcessingStatus,
)
from src.domain.repositories.candidate_repository import CandidateRepository
from src.infrastructure.database.models.candidate import (
    CandidateEducationModel,
    CandidateExperienceModel,
    CandidateModel,
    CandidateScoreModel,
    CandidateSkillModel,
)


class CandidateRepositoryImpl(CandidateRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: CandidateModel) -> Candidate:
        skills = [
            CandidateSkill(name=s.skill_name, proficiency=s.proficiency, years=s.years)
            for s in (model.skills or [])
        ]
        experience = [
            CandidateExperience(
                company=e.company,
                title=e.title,
                start_date=e.start_date,
                end_date=e.end_date,
                is_current=e.is_current,
                description=e.description,
                duration_months=e.duration_months,
            )
            for e in (model.experiences or [])
        ]
        education = [
            CandidateEducation(
                institution=ed.institution,
                degree=ed.degree,
                field=ed.field,
                graduation_year=ed.graduation_year,
                gpa=ed.gpa,
            )
            for ed in (model.educations or [])
        ]
        return Candidate(
            id=model.id,
            job_id=model.job_id,
            resume_s3_key=model.resume_s3_key,
            processing_status=ProcessingStatus(model.processing_status),
            name=model.name,
            email=model.email,
            phone=model.phone,
            resume_text=model.resume_text,
            parsed_data=model.parsed_data,
            experience_years=model.experience_years,
            current_title=model.current_title,
            current_company=model.current_company,
            skills=skills,
            experience=experience,
            education=education,
            certifications=model.certifications or [],
            pinecone_vector_id=model.pinecone_vector_id,
            processing_error=model.processing_error,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _score_to_entity(self, model: CandidateScoreModel) -> CandidateScore:
        return CandidateScore(
            job_id=model.job_id,
            overall_score=model.overall_score,
            skill_score=model.skill_score,
            experience_score=model.experience_score,
            domain_score=model.domain_score,
            education_score=model.education_score,
            certification_score=model.certification_score,
            ai_confidence=model.ai_confidence,
            ai_summary=model.ai_summary,
            skill_gaps=model.skill_gaps or [],
            score_justification=model.score_justification,
            recommendation=model.recommendation,
            model_version=model.model_version,
            scored_at=model.scored_at,
        )

    async def get_by_id(self, candidate_id: UUID) -> Candidate | None:
        result = await self._session.execute(
            select(CandidateModel)
            .options(
                selectinload(CandidateModel.skills),
                selectinload(CandidateModel.experiences),
                selectinload(CandidateModel.educations),
            )
            .where(CandidateModel.id == candidate_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_job(
        self,
        job_id: UUID,
        *,
        status: ProcessingStatus | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Candidate], int]:
        from sqlalchemy import func

        query = select(CandidateModel).where(CandidateModel.job_id == job_id)
        if status:
            query = query.where(CandidateModel.processing_status == status.value)

        count_result = await self._session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar_one()

        query = (
            query.options(
                selectinload(CandidateModel.skills),
                selectinload(CandidateModel.experiences),
                selectinload(CandidateModel.educations),
            )
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models], total

    async def create(self, candidate: Candidate) -> Candidate:
        model = CandidateModel(
            id=candidate.id,
            job_id=candidate.job_id,
            resume_s3_key=candidate.resume_s3_key,
            processing_status=candidate.processing_status.value,
            name=candidate.name,
            email=candidate.email,
            phone=candidate.phone,
            certifications=candidate.certifications,
        )
        self._session.add(model)
        await self._session.flush()
        return candidate

    async def update(self, candidate: Candidate) -> Candidate:
        result = await self._session.execute(
            select(CandidateModel).where(CandidateModel.id == candidate.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Candidate {candidate.id} not found")

        model.name = candidate.name
        model.email = candidate.email
        model.phone = candidate.phone
        model.resume_text = candidate.resume_text
        model.parsed_data = candidate.parsed_data
        model.experience_years = candidate.experience_years
        model.current_title = candidate.current_title
        model.current_company = candidate.current_company
        model.certifications = candidate.certifications
        model.processing_status = candidate.processing_status.value
        model.processing_error = candidate.processing_error
        model.pinecone_vector_id = candidate.pinecone_vector_id

        # Sync skills
        await self._session.execute(
            delete(CandidateSkillModel).where(CandidateSkillModel.candidate_id == candidate.id)
        )
        for skill in candidate.skills:
            self._session.add(CandidateSkillModel(
                candidate_id=candidate.id,
                skill_name=skill.name,
                proficiency=skill.proficiency,
                years=skill.years,
            ))

        # Sync experience
        await self._session.execute(
            delete(CandidateExperienceModel).where(CandidateExperienceModel.candidate_id == candidate.id)
        )
        for exp in candidate.experience:
            self._session.add(CandidateExperienceModel(
                candidate_id=candidate.id,
                company=exp.company,
                title=exp.title,
                start_date=exp.start_date,
                end_date=exp.end_date,
                is_current=exp.is_current,
                description=exp.description,
                duration_months=exp.duration_months,
            ))

        # Sync education
        await self._session.execute(
            delete(CandidateEducationModel).where(CandidateEducationModel.candidate_id == candidate.id)
        )
        for edu in candidate.education:
            self._session.add(CandidateEducationModel(
                candidate_id=candidate.id,
                institution=edu.institution,
                degree=edu.degree,
                field=edu.field,
                graduation_year=edu.graduation_year,
                gpa=edu.gpa,
            ))

        await self._session.flush()
        return candidate

    async def delete(self, candidate_id: UUID) -> None:
        result = await self._session.execute(
            select(CandidateModel).where(CandidateModel.id == candidate_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)

    async def get_score(self, candidate_id: UUID, job_id: UUID) -> CandidateScore | None:
        result = await self._session.execute(
            select(CandidateScoreModel)
            .where(
                CandidateScoreModel.candidate_id == candidate_id,
                CandidateScoreModel.job_id == job_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._score_to_entity(model) if model else None

    async def upsert_score(self, candidate_id: UUID, score: CandidateScore) -> CandidateScore:
        existing = await self._session.execute(
            select(CandidateScoreModel).where(
                CandidateScoreModel.candidate_id == candidate_id,
                CandidateScoreModel.job_id == score.job_id,
            )
        )
        model = existing.scalar_one_or_none()

        if model:
            model.overall_score = score.overall_score
            model.skill_score = score.skill_score
            model.experience_score = score.experience_score
            model.domain_score = score.domain_score
            model.education_score = score.education_score
            model.certification_score = score.certification_score
            model.ai_confidence = score.ai_confidence
            model.ai_summary = score.ai_summary
            model.skill_gaps = score.skill_gaps
            model.score_justification = score.score_justification
            model.recommendation = score.recommendation
            model.model_version = score.model_version
        else:
            model = CandidateScoreModel(
                candidate_id=candidate_id,
                job_id=score.job_id,
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
                model_version=score.model_version,
            )
            self._session.add(model)

        await self._session.flush()
        return score

    async def list_ranked_by_job(
        self, job_id: UUID, *, limit: int = 50, offset: int = 0
    ) -> list[tuple[Candidate, CandidateScore]]:
        result = await self._session.execute(
            select(CandidateModel, CandidateScoreModel)
            .join(
                CandidateScoreModel,
                (CandidateScoreModel.candidate_id == CandidateModel.id)
                & (CandidateScoreModel.job_id == job_id),
            )
            .options(
                selectinload(CandidateModel.skills),
                selectinload(CandidateModel.experiences),
                selectinload(CandidateModel.educations),
            )
            .where(CandidateModel.job_id == job_id)
            .where(CandidateModel.processing_status == "processed")
            .order_by(CandidateScoreModel.overall_score.desc())
            .offset(offset)
            .limit(limit)
        )
        rows = result.all()
        return [(self._to_entity(c), self._score_to_entity(s)) for c, s in rows]
