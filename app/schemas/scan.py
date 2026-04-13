from __future__ import annotations

from pydantic import BaseModel, Field


class ScanItemResponse(BaseModel):
    name: str
    confidence: float = Field(ge=0.0, le=1.0)
    calories: float = Field(ge=0)
    protein: float = Field(ge=0)
    carbs: float = Field(ge=0)
    fat: float = Field(ge=0)


class ScanSummaryResponse(BaseModel):
    kcal: float = Field(ge=0)
    protein: float = Field(ge=0)
    carbs: float = Field(ge=0)
    fat: float = Field(ge=0)


class ScanResponse(BaseModel):
    scanId: str
    items: list[ScanItemResponse]
    summary: ScanSummaryResponse


class ScanLogItemRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    calories: float = Field(ge=0)
    protein: float = Field(ge=0)
    carbs: float = Field(ge=0)
    fat: float = Field(ge=0)


class ScanLogRequest(BaseModel):
    scanId: str | None = None
    items: list[ScanLogItemRequest] = Field(min_length=1)
    mealType: str | None = None
    date: str | None = None


class ScanLogResponse(BaseModel):
    message: str
    loggedCount: int = Field(ge=0)
    mealLogId: int
