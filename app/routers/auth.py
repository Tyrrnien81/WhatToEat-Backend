from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user_id
from app.models.user import Profile
from app.schemas.auth import UserResponse, UpsertProfileRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=UserResponse)
async def me_route(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Profile).where(Profile.id == user_id))
    profile = result.scalar_one_or_none()

    if not profile:
        return {
            "id": str(user_id),
            "email": None,
            "name": None,
        }

    return {
        "id": str(profile.id),
        "email": profile.email,
        "name": profile.name,
    }


@router.post("/profile", response_model=UserResponse)
async def upsert_profile_route(
    payload: UpsertProfileRequest,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Profile).where(Profile.id == user_id))
    profile = result.scalar_one_or_none()

    if not profile:
        profile = Profile(
            id=user_id,
            email=payload.email,
            name=payload.name,
        )
        db.add(profile)
    else:
        if payload.email is not None:
            profile.email = payload.email
        if payload.name is not None:
            profile.name = payload.name

    await db.commit()
    await db.refresh(profile)

    return {
        "id": str(profile.id),
        "email": profile.email,
        "name": profile.name,
    }