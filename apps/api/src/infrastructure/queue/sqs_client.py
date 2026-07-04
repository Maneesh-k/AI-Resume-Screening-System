from __future__ import annotations

import json

import boto3
import structlog

from src.config import get_settings

log = structlog.get_logger()
settings = get_settings()

_sqs_client = None


def get_sqs_client():
    global _sqs_client
    if _sqs_client is None:
        _sqs_client = boto3.client(
            "sqs",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None,
        )
    return _sqs_client


async def publish_resume_processing_job(
    candidate_id: str,
    job_id: str,
    s3_key: str,
    content_type: str,
) -> str:
    """Publish a resume processing message to SQS."""
    import asyncio

    if not settings.aws_sqs_queue_url:
        log.warning("sqs_queue_url_not_configured_skipping")
        return ""

    payload = {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "s3_key": s3_key,
        "content_type": content_type,
    }

    response = await asyncio.to_thread(
        get_sqs_client().send_message,
        QueueUrl=settings.aws_sqs_queue_url,
        MessageBody=json.dumps(payload),
        MessageAttributes={
            "candidate_id": {"DataType": "String", "StringValue": candidate_id},
        },
    )

    message_id = response.get("MessageId", "")
    log.info("sqs_message_published", message_id=message_id, candidate_id=candidate_id)
    return message_id
