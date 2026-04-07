from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user_id
from app.models.user import Profile
from app.models.meal_log import MealLog, MealLogItem
from app.schemas.profile import (
    ProfileResponse,
    ProfileUpdateRequest,
    FoodLogResponse,
    FoodLogCreateRequest,
)

router = APIRouter(prefix="/users/me", tags=["profile"])


# GET /users/me
@router.get("", response_model=ProfileResponse)
async def get_my_profile(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Profile).where(Profile.id == user_id))
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    return ProfileResponse.from_orm(profile)


# PATCH /users/me
@router.patch("", response_model=ProfileResponse)
async def update_my_profile(
    payload: ProfileUpdateRequest,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Profile).where(Profile.id == user_id))
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    if payload.name is not None:
        profile.name = payload.name
    if payload.email is not None:
        profile.email = payload.email

    await db.commit()
    await db.refresh(profile)

    return ProfileResponse.from_orm(profile)


# GET /users/me/food-log
@router.get("/food-log", response_model=list[FoodLogResponse])
async def get_food_log(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MealLog).where(MealLog.user_id == user_id).order_by(MealLog.date.desc())
    )
    logs = result.scalars().all()

    if not logs:
        return []

    log_ids = [log.id for log in logs]
    items_result = await db.execute(
        select(MealLogItem).where(MealLogItem.meal_log_id.in_(log_ids))
    )
    items = items_result.scalars().all()

    items_by_log = {}
    for item in items:
        items_by_log.setdefault(item.meal_log_id, []).append(item)

    return [
        FoodLogResponse.from_log_and_items(log, items_by_log.get(log.id, []))
        for log in logs
    ]


# POST /users/me/food-log
@router.post("/food-log", response_model=FoodLogResponse, status_code=status.HTTP_201_CREATED)
async def create_food_log(
    payload: FoodLogCreateRequest,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    meal_log = MealLog(
        user_id=user_id,
        date=payload.date,
        meal_type=payload.meal_type,
    )
    db.add(meal_log)
    await db.flush()

    items = []
    for item_data in payload.items:
        item = MealLogItem(
            meal_log_id=meal_log.id,
            food_id=item_data.food_id,
            food_name=item_data.food_name,
            quantity=item_data.quantity,
            calories=item_data.calories,
            g_protein=item_data.g_protein,
            g_carbs=item_data.g_carbs,
            g_fat=item_data.g_fat,
            source=item_data.source,
        )
        db.add(item)
        items.append(item)

    await db.commit()
    await db.refresh(meal_log)

    return FoodLogResponse.from_log_and_items(meal_log, items)