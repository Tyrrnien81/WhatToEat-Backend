from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


VALID_GENDERS = {"male", "female", "other", "prefer"}
VALID_DIET_TYPES = {"balanced", "high_protein", "vegan", "vegetarian"}
VALID_ALLERGENS = {
    "none", "soy", "peanuts", "treenuts", "halal", "kosher",
    "dairy", "gluten", "shellfish", "fish", "egg", "other",
}
VALID_DINING_HALLS = {
    "gordon", "fourlakes", "liz", "rheta", "carson", "lowell",
}

DIET_TYPE_ALIASES = {
    "highprotein": "high_protein",
}


class QuestionnaireSubmitRequest(BaseModel):
    birthday: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    gender: str
    height: float
    height_unit: Literal["cm", "ft"] = "cm"
    weight: float
    weight_unit: Literal["kg", "lb"] = "kg"
    goal_weight: float
    diet_type: str
    dislikes: list[str] = []
    allergens: list[str] = []
    favorite_dining_halls: list[str] = Field(default=[], max_length=3)

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        if v not in VALID_GENDERS:
            raise ValueError(f"gender must be one of {sorted(VALID_GENDERS)}")
        return v

    @field_validator("diet_type")
    @classmethod
    def validate_diet_type(cls, v: str) -> str:
        normalized = DIET_TYPE_ALIASES.get(v, v)
        if normalized not in VALID_DIET_TYPES:
            raise ValueError(f"diet_type must be one of {sorted(VALID_DIET_TYPES)}")
        return normalized

    @field_validator("allergens")
    @classmethod
    def validate_allergens(cls, v: list[str]) -> list[str]:
        for a in v:
            if a not in VALID_ALLERGENS:
                raise ValueError(f"unknown allergen '{a}'; valid: {sorted(VALID_ALLERGENS)}")
        if "none" in v:
            return []
        return v

    @field_validator("favorite_dining_halls")
    @classmethod
    def validate_halls(cls, v: list[str]) -> list[str]:
        for h in v:
            if h not in VALID_DINING_HALLS:
                raise ValueError(f"unknown dining hall '{h}'; valid: {sorted(VALID_DINING_HALLS)}")
        return v


class PreferencesUpdateRequest(BaseModel):
    birthday: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    gender: Optional[str] = None
    height: Optional[float] = None
    height_unit: Literal["cm", "ft"] = "cm"
    weight: Optional[float] = None
    weight_unit: Literal["kg", "lb"] = "kg"
    goal_weight: Optional[float] = None
    diet_type: Optional[str] = None
    dislikes: Optional[list[str]] = None
    allergens: Optional[list[str]] = None
    favorite_dining_halls: Optional[list[str]] = Field(None, max_length=3)

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_GENDERS:
            raise ValueError(f"gender must be one of {sorted(VALID_GENDERS)}")
        return v

    @field_validator("diet_type")
    @classmethod
    def validate_diet_type(cls, v: str | None) -> str | None:
        if v is None:
            return v
        normalized = DIET_TYPE_ALIASES.get(v, v)
        if normalized not in VALID_DIET_TYPES:
            raise ValueError(f"diet_type must be one of {sorted(VALID_DIET_TYPES)}")
        return normalized

    @field_validator("allergens")
    @classmethod
    def validate_allergens(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        for a in v:
            if a not in VALID_ALLERGENS:
                raise ValueError(f"unknown allergen '{a}'")
        if "none" in v:
            return []
        return v

    @field_validator("favorite_dining_halls")
    @classmethod
    def validate_halls(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        for h in v:
            if h not in VALID_DINING_HALLS:
                raise ValueError(f"unknown dining hall '{h}'")
        return v


class PreferencesResponse(BaseModel):
    birthday: Optional[str] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    goal_weight: Optional[float] = None
    diet_type: Optional[str] = None
    dislikes: list[str] = []
    allergens: list[str] = []
    favorite_dining_halls: list[str] = []
    target_calories: Optional[int] = None
    target_protein_g: Optional[int] = None
    target_carbs_g: Optional[int] = None
    target_fat_g: Optional[int] = None
