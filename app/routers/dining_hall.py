import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.dining_hall import (
    DiningHallListResponse,
    DiningHallDetailResponse,
    DiningHallStationsResponse,
    DiningHallMenusResponse,
    FullDiningHallsResponse,
)
from app.services import dining_hall_service

router = APIRouter(prefix="/dining-halls", tags=["dining-halls"])


@router.get("", response_model=DiningHallListResponse)
async def list_dining_halls(
    db: AsyncSession = Depends(get_db),
):
    return await dining_hall_service.get_dining_halls(db)


@router.get("/full", response_model=FullDiningHallsResponse)
async def get_dining_halls_full(
    date_param: str | None = Query(None, alias="date"),
    user_id: uuid.UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    target_date = date.fromisoformat(date_param) if date_param else date.today()
    return await dining_hall_service.get_dining_halls_full(target_date, user_id, db)


@router.get("/{hall_id}", response_model=DiningHallDetailResponse)
async def get_dining_hall(
    hall_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await dining_hall_service.get_dining_hall_detail(hall_id, db)


@router.get("/{hall_id}/stations", response_model=DiningHallStationsResponse)
async def get_stations(
    hall_id: int,
    date_param: str | None = Query(None, alias="date"),
    mealType: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    target_date = date.fromisoformat(date_param) if date_param else date.today()
    return await dining_hall_service.get_dining_hall_stations(hall_id, target_date, mealType, db)


@router.get("/{hall_id}/menus", response_model=DiningHallMenusResponse)
async def get_menus(
    hall_id: int,
    date_param: str | None = Query(None, alias="date"),
    mealType: str | None = Query(None),
    meal: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    target_date = date.fromisoformat(date_param) if date_param else date.today()
    # Accept both 'meal' and 'mealType' query params (frontend compat)
    resolved_meal_type = mealType or meal
    return await dining_hall_service.get_dining_hall_menus(hall_id, target_date, resolved_meal_type, db)
