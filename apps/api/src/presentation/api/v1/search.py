from __future__ import annotations

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.infrastructure.ai.openai_client import get_embedding
from src.infrastructure.database.repositories.candidate_repository_impl import CandidateRepositoryImpl
from src.infrastructure.database.session import get_db
from src.infrastructure.vector_db.pinecone_client import query_vectors
from src.presentation.dependencies import CurrentUser

router = APIRouter()
log = structlog.get_logger()
settings = get_settings()

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("/candidates")
async def semantic_search_candidates(
    current_user: CurrentUser,
    db: DbSession,
    q: str = Query(min_length=3, description="Search query"),
    job_id: uuid.UUID | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=50),
) -> dict:
    query_vector = await get_embedding(q)

    pinecone_filter: dict = {}
    if job_id:
        pinecone_filter["job_id"] = str(job_id)

    matches = await query_vectors(
        query_vector=query_vector,
        namespace=settings.pinecone_namespace_resumes,
        top_k=limit,
        filter=pinecone_filter if pinecone_filter else None,
    )

    if not matches:
        return {"query": q, "results": []}

    repo = CandidateRepositoryImpl(db)
    results = []
    for match in matches:
        candidate_id_str = match["metadata"].get("candidate_id")
        if not candidate_id_str:
            continue
        candidate = await repo.get_by_id(uuid.UUID(candidate_id_str))
        if not candidate:
            continue
        results.append({
            "candidate_id": str(candidate.id),
            "name": candidate.name,
            "similarity_score": round(match["score"], 4),
            "overall_score": match["metadata"].get("overall_score"),
            "current_title": candidate.current_title,
            "experience_years": candidate.experience_years,
            "skills": [s.name for s in candidate.skills[:8]],
        })

    log.info("semantic_search", query=q, results_count=len(results))
    return {"query": q, "results": results}
