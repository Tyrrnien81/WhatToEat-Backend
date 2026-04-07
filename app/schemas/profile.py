from __future__ import annotations
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


# ── Sub-schemas ────────────────────────────────────────────────────────────────

class MealLogItemResponse(BaseModel):
    id: int
    food_id: Optional[int] = None
    food_name: str
    quantity: Optional[float] = None
    calories: Optional[float] = None
    g_protein: Optional[float] = None
    g_carbs: Optional[float] = None
    g_fat: Optional[float] = None
    source: str
    logged_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MealLogItemCreateRequest(BaseModel):
    food_id: Optional[int] = None
    food_name: str
    quantity: Optional[float] = 1
    calories: Optional[float] = None
    g_protein: Optional[float] = None
    g_carbs: Optional[float] = None
    g_fat: Optional[float] = None
    source: str = "manual"


# ── Profile ────────────────────────────────────────────────────────────────────

class ProfileResponse(BaseModel):
    id: str
    email: Optional[str] = None
    name: Optional[str] = None

    @classmethod
    def from_orm(cls, profile) -> ProfileResponse:
        return cls(
            id=str(profile.id),
            email=profile.email,
            name=profile.name,
        )


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


# ── Food Log ───────────────────────────────────────────────────────────────────

class FoodLogResponse(BaseModel):
    id: int
    date: date
    meal_type: str
    created_at: Optional[datetime] = None
    items: list[MealLogItemResponse] = []

    @classmethod
    def from_log_and_items(cls, log, items) -> FoodLogResponse:
        return cls(
            id=log.id,
            date=log.date,
            meal_type=log.meal_type,
            created_at=log.created_at,
            items=[MealLogItemResponse.model_validate(i) for i in items],
        )


class FoodLogCreateRequest(BaseModel):
    date: date
    meal_type: str
    items: list[MealLogItemCreateRequest] = []