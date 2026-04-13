from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user_id
from app.schemas.profile import (
    AvatarUploadResponse,
    ChangePasswordRequest,
    FoodLogCreateRequest,
    FoodLogListResponse,
    FoodLogSummaryResponse,
    ProfileResponse,
    ProfileUpdateRequest,
)
from app.services import profile_service

router = APIRouter(prefix="/users/me", tags=["profile"])


@router.get("", response_model=ProfileResponse)
async def get_my_profile(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await profile_service.get_profile(user_id, db)


@router.patch("")
async def update_my_profile(
    payload: ProfileUpdateRequest,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await profile_service.update_profile(user_id, payload, db)


@router.delete("")
async def delete_my_account(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await profile_service.delete_account(user_id, db)


@router.get("/food-log", response_model=FoodLogListResponse)
async def get_food_log(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    date: str | None = Query(None, description="Filter by date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    return await profile_service.get_food_log(user_id, date, page, limit, db)


@router.post("/food-log", status_code=201)
async def create_food_log_entry(
    payload: FoodLogCreateRequest,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await profile_service.create_food_log_entry(user_id, payload, db)


@router.delete("/food-log/{entry_id}")
async def delete_food_log_entry(
    entry_id: int,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await profile_service.delete_food_log_entry(user_id, entry_id, db)


@router.get("/food-log/summary", response_model=FoodLogSummaryResponse)
async def get_food_log_summary(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    range: str = Query("week", pattern="^(week|month|all)$"),
):
    return await profile_service.get_food_log_summary(user_id, range, db)


@router.post("/avatar", response_model=AvatarUploadResponse)
async def upload_avatar(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    avatar: UploadFile = File(...),
):
    return await profile_service.upload_avatar(user_id, avatar, db)


@router.post("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    user_id=Depends(get_current_user_id),
):
    return await profile_service.change_password(
        user_id, payload.currentPassword, payload.newPassword
    )
