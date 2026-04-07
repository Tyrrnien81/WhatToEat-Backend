from __future__ import annotations

from pydantic import BaseModel


# --- Shared ---

class FoodItemResponse(BaseModel):
    id: int
    name: str
    calories: float | None = None
    protein: float | None = None
    carbs: float | None = None
    fat: float | None = None
    station: str | None = None
    servingSizeAmount: str | None = None
    servingSizeUnit: str | None = None


class ComboResponse(BaseModel):
    id: str
    name: str
    label: str | None = None
    items: list[FoodItemResponse]
    totalCalories: float
    totalProtein: float
    totalCarbs: float
    totalFat: float
    diningHall: str
    logged: bool = False


class CombosListResponse(BaseModel):
    combos: list[ComboResponse]


# --- Goals ---

class MacroProgress(BaseModel):
    goal: int
    consumed: float


class DailyGoalsResponse(BaseModel):
    date: str
    calories: MacroProgress
    protein: MacroProgress
    carbs: MacroProgress
    fat: MacroProgress


# --- Menu Summary ---

class SummaryFoodItem(BaseModel):
    id: int
    name: str
    calories: float | None = None
    protein: float | None = None
    carbs: float | None = None
    fat: float | None = None
    station: str | None = None
    icons: list[str] = []


class DiningHallSummary(BaseModel):
    id: int
    name: str
    recommendedItems: list[SummaryFoodItem]


class MenuSummaryResponse(BaseModel):
    date: str
    diningHalls: list[DiningHallSummary]


# --- Log Meal ---

class LogMealItemRequest(BaseModel):
    foodId: int | None = None
    foodName: str
    quantity: float = 1.0
    calories: float | None = None
    protein: float | None = None
    carbs: float | None = None
    fat: float | None = None
    source: str = "menu"


class LogMealRequest(BaseModel):
    date: str
    mealType: str
    items: list[LogMealItemRequest]


class LogMealResponse(BaseModel):
    mealLogId: int
    message: str


# --- Favorites ---

class SaveFavoriteRequest(BaseModel):
    comboId: str


class SaveFavoriteResponse(BaseModel):
    id: str
    message: str


class DeleteFavoriteResponse(BaseModel):
    message: str


# --- Add-ons ---

class AddonFoodItem(BaseModel):
    id: int
    name: str
    calories: float | None = None
    protein: float | None = None
    carbs: float | None = None
    fat: float | None = None
    station: str | None = None
    icons: list[str] = []


class AddonsResponse(BaseModel):
    mealType: str
    suggestions: list[AddonFoodItem]
    quickAddons: list[AddonFoodItem]
