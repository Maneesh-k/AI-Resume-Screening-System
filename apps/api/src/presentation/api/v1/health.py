from __future__ import annotations

from fastapi import APIRouter

from src.config import get_settings
from src.presentation.schemas.common import HealthResponse

router = APIRouter()
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version="1.0.0",
        environment=settings.environment,
    )
