from __future__ import annotations

import uuid
from pathlib import PurePosixPath

import boto3
import structlog
from botocore.exceptions import ClientError

from src.config import get_settings

log = structlog.get_logger()
settings = get_settings()

_s3_client = None


def get_s3_client():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client(
            "s3",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None,
        )
    return _s3_client


async def upload_resume(
    file_bytes: bytes,
    job_id: str,
    candidate_id: str,
    filename: str,
    content_type: str,
) -> str:
    """Upload resume to S3. Returns the S3 object key."""
    ext = PurePosixPath(filename).suffix.lower()
    key = f"resumes/{job_id}/{candidate_id}/{uuid.uuid4()}{ext}"

    import asyncio
    await asyncio.to_thread(
        get_s3_client().put_object,
        Bucket=settings.aws_s3_bucket_name,
        Key=key,
        Body=file_bytes,
        ContentType=content_type,
        ServerSideEncryption="AES256",
    )

    log.info("s3_upload_complete", key=key, candidate_id=candidate_id)
    return key


async def generate_presigned_url(s3_key: str, expiry_seconds: int = 3600) -> str:
    """Generate a pre-signed URL for downloading a resume."""
    import asyncio
    url = await asyncio.to_thread(
        get_s3_client().generate_presigned_url,
        "get_object",
        Params={"Bucket": settings.aws_s3_bucket_name, "Key": s3_key},
        ExpiresIn=expiry_seconds,
    )
    return url


async def download_file(s3_key: str) -> bytes:
    """Download file bytes from S3."""
    import asyncio
    response = await asyncio.to_thread(
        get_s3_client().get_object,
        Bucket=settings.aws_s3_bucket_name,
        Key=s3_key,
    )
    return response["Body"].read()
