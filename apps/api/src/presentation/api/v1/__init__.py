from __future__ import annotations

from fastapi import APIRouter

from src.presentation.api.v1 import auth, jobs, resumes, candidates, ai, search, chat, health

router = APIRouter()

router.include_router(health.router, tags=["Health"])
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
router.include_router(resumes.router, prefix="/resumes", tags=["Resumes"])
router.include_router(candidates.router, prefix="/candidates", tags=["Candidates"])
router.include_router(ai.router, prefix="/ai", tags=["AI"])
router.include_router(search.router, prefix="/search", tags=["Search"])
router.include_router(chat.router, prefix="/chat", tags=["Copilot Chat"])
