from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.domain.entities.user import User, UserRole
from src.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from src.infrastructure.database.session import get_db
from src.presentation.dependencies import CurrentUser
from src.presentation.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)

router = APIRouter()
log = structlog.get_logger()
settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DbSession = Annotated[AsyncSession, Depends(get_db)]


def create_access_token(user_id: str) -> tuple[str, int]:
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload = {"sub": user_id, "exp": expire, "type": "access"}
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, settings.jwt_access_token_expire_minutes * 60


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: DbSession) -> AuthResponse:
    repo = UserRepositoryImpl(db)
    existing = await repo.get_by_email(body.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        id=uuid.uuid4(),
        email=body.email,
        name=body.name,
        role=UserRole(body.role),
        hashed_password=pwd_context.hash(body.password),
    )
    created = await repo.create(user)

    token, expires_in = create_access_token(str(created.id))
    log.info("user_registered", user_id=str(created.id), role=created.role)

    return AuthResponse(
        access_token=token,
        expires_in=expires_in,
        user=UserResponse(
            id=str(created.id),
            email=created.email,
            name=created.name,
            role=created.role.value,
            is_active=created.is_active,
        ),
    )


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest, db: DbSession) -> AuthResponse:
    repo = UserRepositoryImpl(db)
    user = await repo.get_by_email(body.email)

    if not user or not pwd_context.verify(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    token, expires_in = create_access_token(str(user.id))
    log.info("user_logged_in", user_id=str(user.id))

    return AuthResponse(
        access_token=token,
        expires_in=expires_in,
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
            role=user.role.value,
            is_active=user.is_active,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser) -> UserResponse:
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        role=current_user.role.value,
        is_active=current_user.is_active,
    )
