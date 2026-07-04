from __future__ import annotations

import io
import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.domain.entities.candidate import Candidate, ProcessingStatus
from src.infrastructure.database.repositories.candidate_repository_impl import CandidateRepositoryImpl
from src.infrastructure.database.repositories.job_repository_impl import JobRepositoryImpl
from src.infrastructure.database.session import get_db
from src.infrastructure.storage.s3_client import upload_resume, generate_presigned_url
from src.infrastructure.queue.sqs_client import publish_resume_processing_job
from src.presentation.dependencies import CurrentUser
from src.presentation.schemas.candidate import UploadResumeResponse, ProcessingStatusResponse

router = APIRouter()
log = structlog.get_logger()
settings = get_settings()

DbSession = Annotated[AsyncSession, Depends(get_db)]

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}


@router.post("/upload", response_model=UploadResumeResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_resume_endpoint(
    current_user: CurrentUser,
    db: DbSession,
    file: UploadFile = File(...),
    job_id: str = Form(...),
) -> UploadResumeResponse:
    if not current_user.can_upload_resumes():
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Validate file
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF and DOCX files are allowed.",
        )

    file_bytes = await file.read()
    if len(file_bytes) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.max_upload_size_mb}MB.",
        )
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="File is empty")

    # Validate job exists
    job_repo = JobRepositoryImpl(db)
    job = await job_repo.get_by_id(uuid.UUID(job_id))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    candidate_id = uuid.uuid4()

    # Upload to S3
    try:
        s3_key = await upload_resume(
            file_bytes=file_bytes,
            job_id=job_id,
            candidate_id=str(candidate_id),
            filename=file.filename or f"resume_{candidate_id}",
            content_type=file.content_type,
        )
    except Exception as e:
        log.error("s3_upload_failed", error=str(e), candidate_id=str(candidate_id))
        raise HTTPException(status_code=500, detail="Failed to upload file. Please try again.")

    # Create candidate record
    candidate = Candidate(
        id=candidate_id,
        job_id=uuid.UUID(job_id),
        resume_s3_key=s3_key,
        processing_status=ProcessingStatus.PENDING,
    )
    candidate_repo = CandidateRepositoryImpl(db)
    await candidate_repo.create(candidate)

    # Queue processing job
    try:
        await publish_resume_processing_job(
            candidate_id=str(candidate_id),
            job_id=job_id,
            s3_key=s3_key,
            content_type=file.content_type,
        )
    except Exception as e:
        log.warning("sqs_publish_failed_processing_inline", error=str(e))
        # For local dev without SQS, trigger inline processing
        from src.worker.resume_processor import process_resume_inline
        import asyncio
        asyncio.create_task(
            process_resume_inline(
                candidate_id=str(candidate_id),
                job_id=job_id,
                file_bytes=file_bytes,
                content_type=file.content_type,
            )
        )

    log.info("resume_uploaded", candidate_id=str(candidate_id), job_id=job_id)
    return UploadResumeResponse(
        candidate_id=candidate_id,
        status="pending",
        message="Resume uploaded successfully. Processing has started.",
    )


@router.get("/{candidate_id}/status", response_model=ProcessingStatusResponse)
async def get_processing_status(
    candidate_id: uuid.UUID, current_user: CurrentUser, db: DbSession
) -> ProcessingStatusResponse:
    repo = CandidateRepositoryImpl(db)
    candidate = await repo.get_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    progress_map = {
        ProcessingStatus.PENDING: 5,
        ProcessingStatus.PROCESSING: 50,
        ProcessingStatus.PROCESSED: 100,
        ProcessingStatus.FAILED: 0,
    }

    return ProcessingStatusResponse(
        candidate_id=candidate.id,
        status=candidate.processing_status.value,
        progress_pct=progress_map[candidate.processing_status],
        error=candidate.processing_error,
    )


@router.get("/{candidate_id}/download-url")
async def get_resume_download_url(
    candidate_id: uuid.UUID, current_user: CurrentUser, db: DbSession
) -> dict:
    repo = CandidateRepositoryImpl(db)
    candidate = await repo.get_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    try:
        url = await generate_presigned_url(candidate.resume_s3_key)
        return {"url": url, "expires_in": 3600}
    except Exception as e:
        log.error("presigned_url_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate download URL")
