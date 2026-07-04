from __future__ import annotations

import json
import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.infrastructure.ai.openai_client import chat_completion_stream, get_embedding
from src.infrastructure.database.repositories.candidate_repository_impl import CandidateRepositoryImpl
from src.infrastructure.database.session import get_db
from src.infrastructure.vector_db.pinecone_client import query_vectors
from src.presentation.dependencies import CurrentUser

router = APIRouter()
log = structlog.get_logger()
settings = get_settings()

DbSession = Annotated[AsyncSession, Depends(get_db)]

COPILOT_SYSTEM_PROMPT = """You are an AI Hiring Copilot assistant for recruiters at a professional recruitment platform.

Your role is to help recruiters:
- Find and evaluate candidates based on semantic search results provided to you
- Summarize candidate strengths and weaknesses
- Compare candidates side by side
- Explain match scores and skill gaps
- Suggest interview strategies
- Answer questions about hiring best practices

Guidelines:
- Be concise, professional, and data-driven
- Always base your responses on the candidate data provided in context
- If no candidate data is provided, explain you need to run a search first
- Format candidate lists with names, scores, and key highlights
- Be empathetic about candidates — they are real people
- Never fabricate scores or qualifications not in the provided data
"""


class ChatMessage(BaseModel):
    session_id: str | None = None
    message: str
    job_id: str | None = None


@router.post("/message")
async def chat_with_copilot(
    body: ChatMessage,
    current_user: CurrentUser,
    db: DbSession,
) -> StreamingResponse:
    async def generate() -> AsyncGenerator[str, None]:
        try:
            # Step 1: Embed the user's query and search for relevant candidates
            query_vector = await get_embedding(body.message)
            pinecone_filter: dict = {}
            if body.job_id:
                pinecone_filter["job_id"] = body.job_id

            matches = await query_vectors(
                query_vector=query_vector,
                namespace=settings.pinecone_namespace_resumes,
                top_k=8,
                filter=pinecone_filter if pinecone_filter else None,
            )

            # Step 2: Build context from retrieved candidates
            context_parts = []
            candidate_ids = []
            repo = CandidateRepositoryImpl(db)

            for match in matches[:6]:
                candidate_id_str = match["metadata"].get("candidate_id")
                if not candidate_id_str:
                    continue
                candidate = await repo.get_by_id(uuid.UUID(candidate_id_str))
                if not candidate:
                    continue

                candidate_ids.append(str(candidate.id))
                score = match["metadata"].get("overall_score", "N/A")
                skills = ", ".join([s.name for s in candidate.skills[:6]])
                context_parts.append(
                    f"Candidate: {candidate.name or 'Unknown'} | "
                    f"Score: {score} | "
                    f"Title: {candidate.current_title or 'N/A'} | "
                    f"Experience: {candidate.experience_years or 'N/A'} years | "
                    f"Skills: {skills} | "
                    f"ID: {candidate.id}"
                )

            context = "\n".join(context_parts) if context_parts else "No matching candidates found in the database."
            user_message = f"Query: {body.message}\n\nRelevant candidates:\n{context}"

            # Step 3: Stream LLM response
            full_response = ""
            async for token in chat_completion_stream(COPILOT_SYSTEM_PROMPT, user_message):
                full_response += token
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

            # Step 4: Send candidate IDs for frontend to hydrate
            if candidate_ids:
                yield f"data: {json.dumps({'type': 'candidates', 'data': candidate_ids})}\n\n"

            session_id = body.session_id or str(uuid.uuid4())
            yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"

            log.info("copilot_response_complete", user_id=str(current_user.id), candidates_found=len(candidate_ids))

        except Exception as e:
            log.error("copilot_error", error=str(e))
            yield f"data: {json.dumps({'type': 'error', 'message': 'Failed to generate response. Please try again.'})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
