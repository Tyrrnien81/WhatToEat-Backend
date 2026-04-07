import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.homescreen import (
    CombosListResponse,
    DailyGoalsResponse,
    MenuSummaryResponse,
    LogMealRequest,
    LogMealResponse,
    SaveFavoriteRequest,
    SaveFavoriteResponse,
    DeleteFavoriteResponse,
    AddonsResponse,
)
from app.services import homescreen_service

router = APIRouter(tags=["homescreen"])


@router.get("/recommendations/combo", response_model=CombosListResponse)
async def get_combos(
    date_param: str | None = Query(None, alias="date"),
    mealType: str | None = Query(None),
    user_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    target_date = date.fromisoformat(date_param) if date_param else date.today()
    return await homescreen_service.get_combos(user_id, target_date, mealType, db)


@router.get("/goals/daily", response_model=DailyGoalsResponse)
async def get_daily_goals(
    date_param: str | None = Query(None, alias="date"),
    user_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    target_date = date.fromisoformat(date_param) if date_param else date.today()
    return await homescreen_service.get_daily_goals(user_id, target_date, db)


@router.get("/menus/summary", response_model=MenuSummaryResponse)
async def get_menu_summary(
    date_param: str | None = Query(None, alias="date"),
    mealType: str | None = Query(None),
    user_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    target_date = date.fromisoformat(date_param) if date_param else date.today()
    return await homescreen_service.get_menu_summary(user_id, target_date, db, mealType)


@router.post("/meals/log", response_model=LogMealResponse, status_code=201)
async def log_meal(
    body: LogMealRequest,
    user_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    items = [item.model_dump() for item in body.items]
    return await homescreen_service.log_meal(user_id, body.date, body.mealType, items, db)


@router.post("/favorites", response_model=SaveFavoriteResponse, status_code=201)
async def save_favorite(
    body: SaveFavoriteRequest,
    user_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    # First get the combo data to snapshot
    target_date = date.today()
    combos_result = await homescreen_service.get_combos(user_id, target_date, None, db)
    # Find the matching combo to snapshot
    snapshot = {}
    for combo in combos_result.get("combos", []):
        if combo["id"] == body.comboId:
            snapshot = combo
            break
    return await homescreen_service.save_favorite(user_id, body.comboId, snapshot, db)


@router.delete("/favorites/{favorite_id}", response_model=DeleteFavoriteResponse)
async def delete_favorite(
    favorite_id: uuid.UUID,
    user_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    return await homescreen_service.delete_favorite(user_id, favorite_id, db)


@router.get("/recommendations/addons", response_model=AddonsResponse)
async def get_addons(
    date_param: str | None = Query(None, alias="date"),
    mealType: str | None = Query(None),
    user_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    target_date = date.fromisoformat(date_param) if date_param else date.today()
    return await homescreen_service.get_addons(user_id, target_date, mealType, db)
