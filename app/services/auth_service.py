from __future__ import annotations

import uuid

import httpx
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import Profile
from app.schemas.auth import UserResponse


async def get_me(user_id: uuid.UUID, db: AsyncSession) -> UserResponse:
    result = await db.execute(select(Profile).where(Profile.id == user_id))
    profile = result.scalar_one_or_none()

    if not profile:
        return UserResponse(id=str(user_id))

    return UserResponse(
        id=str(profile.id),
        email=profile.email,
        name=profile.name,
        avatar_url=profile.avatar_url,
    )


async def upsert_profile(
    user_id: uuid.UUID,
    email: str | None,
    name: str | None,
    db: AsyncSession,
) -> UserResponse:
    result = await db.execute(select(Profile).where(Profile.id == user_id))
    profile = result.scalar_one_or_none()

    if not profile:
        profile = Profile(id=user_id, email=email, name=name)
        db.add(profile)
    else:
        if email is not None:
            profile.email = email
        if name is not None:
            profile.name = name

    await db.commit()
    await db.refresh(profile)

    return UserResponse(
        id=str(profile.id),
        email=profile.email,
        name=profile.name,
        avatar_url=profile.avatar_url,
    )


async def logout(user_id: uuid.UUID, token: str) -> dict:
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(status_code=500, detail="Supabase admin credentials not configured")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.SUPABASE_URL}/auth/v1/logout",
            headers={
                "Authorization": f"Bearer {token}",
                "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
            },
            json={"scope": "global"},
            timeout=10,
        )

    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail="Failed to revoke Supabase session")

    return {"message": "Logged out successfully"}
