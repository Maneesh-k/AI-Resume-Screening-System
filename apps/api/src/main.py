from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from src.config import get_settings
from src.infrastructure.database.session import engine, init_db
from src.infrastructure.cache.redis_client import RedisClient
from src.presentation.api.v1 import router as api_v1_router
from src.presentation.middleware.logging_middleware import LoggingMiddleware

log = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown hooks."""
    log.info("starting_up", environment=settings.environment)
    await init_db()
    await RedisClient.initialize(settings.redis_url)
    log.info("startup_complete")
    yield
    log.info("shutting_down")
    await RedisClient.close()
    await engine.dispose()
    log.info("shutdown_complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Hiring Copilot",
        description="AI-powered recruitment and resume screening platform",
        version="1.0.0",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        lifespan=lifespan,
    )

    # ── Middleware (order matters — outermost first) ───────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(LoggingMiddleware)

    # ── Routers ───────────────────────────────────────────────
    app.include_router(api_v1_router, prefix="/api/v1")

    # ── Exception handlers ────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        log.error("unhandled_exception", exc=str(exc), path=request.url.path)
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}},
        )

    # ── Request timing middleware ─────────────────────────────
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next: object) -> Response:
        start = time.monotonic()
        response: Response = await call_next(request)  # type: ignore[operator]
        duration = time.monotonic() - start
        response.headers["X-Process-Time"] = f"{duration:.4f}"
        return response

    return app


app = create_app()
