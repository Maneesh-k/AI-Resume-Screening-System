"""
Seed script — creates demo users in the database.

Usage:
    cd apps/api
    python scripts/seed.py

Demo credentials:
    Admin       → admin@hiringcopilot.ai     / Admin@1234
    Recruiter   → recruiter@hiringcopilot.ai / Recruit@1234
    HM          → hiring@hiringcopilot.ai    / Hiring@1234
"""
from __future__ import annotations

import asyncio
import uuid

import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.config import get_settings
from src.infrastructure.database.models import UserModel  # noqa: F401

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


DEMO_USERS = [
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
        "name": "Admin User",
        "email": "admin@hiringcopilot.ai",
        "password": "Admin@1234",
        "role": "admin",
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000002"),
        "name": "Sarah Recruiter",
        "email": "recruiter@hiringcopilot.ai",
        "password": "Recruit@1234",
        "role": "recruiter",
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000003"),
        "name": "Mike Hiring",
        "email": "hiring@hiringcopilot.ai",
        "password": "Hiring@1234",
        "role": "hiring_manager",
    },
]


async def seed() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        async with session.begin():
            for u in DEMO_USERS:
                existing = await session.get(UserModel, u["id"])
                if existing:
                    print(f"  skip  {u['email']} (already exists)")
                    continue
                model = UserModel(
                    id=u["id"],
                    name=u["name"],
                    email=u["email"],
                    hashed_password=hash_password(u["password"]),
                    role=u["role"],
                    is_active=True,
                )
                session.add(model)
                print(f"  added {u['email']}  ({u['role']})")

    await engine.dispose()
    print("\nSeed complete.")
    print("\n--- Login credentials ---")
    for u in DEMO_USERS:
        print(f"  {u['role']:<15}  {u['email']}  /  {u['password']}")


if __name__ == "__main__":
    asyncio.run(seed())
