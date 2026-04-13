from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Profile ───────────────────────────────────────────────────────────────────

class ProfileResponse(BaseModel):
    id: str
    email: Optional[str] = None
    name: Optional[str] = None
    birthday: Optional[str] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    goalWeight: Optional[float] = None
    dietType: Optional[str] = None
    avatarUrl: Optional[str] = None
    createdAt: Optional[datetime] = None


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    birthday: Optional[str] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    goalWeight: Optional[float] = Field(None, alias="goalWeight")
    dietType: Optional[str] = Field(None, alias="dietType")


# ── Food Log ─────────────────────────────────────────────────────────────────

class FoodLogEntryResponse(BaseModel):
    id: int
    name: str
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    source: str
    loggedAt: Optional[datetime] = None


class FoodLogListResponse(BaseModel):
    entries: list[FoodLogEntryResponse]
    total: int
    page: int
    limit: int


class FoodLogCreateRequest(BaseModel):
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    date: Optional[str] = None


# ── Avatar ────────────────────────────────────────────────────────────────────

class AvatarUploadResponse(BaseModel):
    message: str
    avatarUrl: str


# ── Change Password ──────────────────────────────────────────────────────────

class ChangePasswordRequest(BaseModel):
    currentPassword: str
    newPassword: str


# ── Food Log Summary ─────────────────────────────────────────────────────────

class WeightEntry(BaseModel):
    date: str
    weight: float


class FoodLogSummaryResponse(BaseModel):
    range: str
    averageDailyCalories: float
    averageDailyProtein: float
    averageDailyCarbs: float
    averageDailyFat: float
    totalMealsLogged: int
    currentStreak: int
    longestStreak: int
    weightHistory: list[WeightEntry] = []
