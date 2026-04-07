from __future__ import annotations

from pydantic import BaseModel


# --- List ---

class DiningHallListItem(BaseModel):
    id: int
    name: str
    externalRestaurantId: int


class DiningHallListResponse(BaseModel):
    diningHalls: list[DiningHallListItem]


# --- Detail ---

class DiningHallDetailResponse(BaseModel):
    id: int
    name: str
    externalRestaurantId: int
    availableMealTypes: list[str]
    availableDates: list[str]


# --- Stations ---

class StationItem(BaseModel):
    station: str
    itemCount: int


class DiningHallStationsResponse(BaseModel):
    hallId: int
    date: str
    mealType: str | None
    stations: list[StationItem]


# --- Menus ---

class MenuItem(BaseModel):
    id: int
    name: str
    calories: float | None = None
    protein: float | None = None
    carbs: float | None = None
    fat: float | None = None
    station: str | None = None
    category: str | None = None
    icons: list[str] = []
    servingSizeAmount: str | None = None
    servingSizeUnit: str | None = None


class StationMenuGroup(BaseModel):
    station: str
    items: list[MenuItem]


class DiningHallMenusResponse(BaseModel):
    hallId: int
    hallName: str
    date: str
    mealType: str | None
    stationMenus: list[StationMenuGroup]


# --- Full (frontend-compatible nested response) ---

class FullMenuItem(BaseModel):
    name: str
    id: int | None = None
    calories: float | None = None
    protein: float | None = None
    carbs: float | None = None
    fat: float | None = None
    favorited: bool = False


class FullMenuCategory(BaseModel):
    category: str
    items: list[FullMenuItem]


class FullMealMenu(BaseModel):
    count: int
    categories: list[FullMenuCategory]


class FullDiningHallDay(BaseModel):
    status: str
    hours: str
    closedNote: str | None = None
    aiPickLabel: str | None = None
    aiPickName: str | None = None
    menus: dict[str, FullMealMenu]


class FullDiningHall(BaseModel):
    id: str
    name: str
    emoji: str
    emojiBg: str
    mapsUrl: str
    days: dict[str, FullDiningHallDay]


class FullDiningHallsResponse(BaseModel):
    diningHalls: list[FullDiningHall]
