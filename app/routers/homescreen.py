import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.homescreen import (
    CombosListResponse,
    DailyGoalsResponse,
    MenuSummaryResponse,
    LogMealRequest,
    LogMealResponse,
)
from app.services import homescreen_service

router = APIRouter(tags=["homescreen"])


@router.get("/recommendations/combo", response_model=CombosListResponse)
async def get_combos(
    date_param: str | None = Query(None, alias="date"),
    mealType: str | None = Query(None),
    user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    target_date = date.fromisoformat(date_param) if date_param else date.today()
    return await homescreen_service.get_combos(user_id, target_date, mealType, db)


@router.get("/goals/daily", response_model=DailyGoalsResponse)
async def get_daily_goals(
    date_param: str | None = Query(None, alias="date"),
    user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    target_date = date.fromisoformat(date_param) if date_param else date.today()
    return await homescreen_service.get_daily_goals(user_id, target_date, db)


@router.get("/menus/summary", response_model=MenuSummaryResponse)
async def get_menu_summary(
    date_param: str | None = Query(None, alias="date"),
    user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    target_date = date.fromisoformat(date_param) if date_param else date.today()
    return await homescreen_service.get_menu_summary(user_id, target_date, db)


@router.post("/meals/log", response_model=LogMealResponse, status_code=201)
async def log_meal(
    body: LogMealRequest,
    user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = [item.model_dump() for item in body.items]
    return await homescreen_service.log_meal(user_id, body.date, body.mealType, items, db)
