from __future__ import annotations

import uuid
from datetime import date

from fastapi import HTTPException
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tracking import UserPreference
from app.models.user import Profile, User
from app.schemas.questionnaire import (
    PreferencesResponse,
    PreferencesUpdateRequest,
    QuestionnaireSubmitRequest,
)


# ── Unit conversion ──────────────────────────────────────────────────────────

def _convert_height_to_cm(height: float, unit: str) -> float:
    """Convert height to cm. If unit is 'ft', height is total inches."""
    if unit == "ft":
        return round(height * 2.54, 1)
    return round(height, 1)


def _convert_weight_to_kg(weight: float, unit: str) -> float:
    if unit == "lb":
        return round(weight * 0.453592, 1)
    return round(weight, 1)


# ── Nutrition target calculation (Mifflin-St Jeor) ───────────────────────────

def _calculate_targets(
    gender: str | None,
    height_cm: float | None,
    weight_kg: float | None,
    birthday: str | None,
    diet_type: str | None,
) -> dict:
    if not all([gender, height_cm, weight_kg, birthday]):
        return {}

    try:
        born = date.fromisoformat(birthday)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return {}

    age = (date.today() - born).days / 365.25
    if age <= 0:
        return {}

    if gender == "female":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161  # type: ignore[operator]
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5  # type: ignore[operator]

    # Moderate activity multiplier
    tdee = bmr * 1.55

    calories = round(tdee)

    # Macro splits by diet type
    splits = {
        "balanced":     (0.25, 0.45, 0.30),
        "high_protein": (0.40, 0.35, 0.25),
        "vegan":        (0.15, 0.55, 0.30),
        "vegetarian":   (0.20, 0.50, 0.30),
    }
    protein_pct, carbs_pct, fat_pct = splits.get(diet_type or "balanced", (0.25, 0.45, 0.30))

    return {
        "target_calories": calories,
        "target_protein_g": round(calories * protein_pct / 4),
        "target_carbs_g": round(calories * carbs_pct / 4),
        "target_fat_g": round(calories * fat_pct / 9),
    }


async def _auth_user_info(user_id: uuid.UUID, db: AsyncSession) -> tuple[bool, str | None]:
    """Returns (exists_in_auth_users, email). `auth.users` is the Supabase-managed source of truth."""
    try:
        row = (
            await db.execute(
                text(
                    "SELECT email FROM auth.users WHERE id = CAST(:uid AS uuid)"
                ),
                {"uid": str(user_id)},
            )
        ).first()
    except Exception:
        return False, None
    if row is None:
        return False, None
    return True, row[0]


async def _ensure_user_and_profile_for_questionnaire(
    user_id: uuid.UUID, db: AsyncSession
) -> None:
    """Guarantee a `public.users` row for ``user_id`` so `user_preferences.user_id` FK holds.

    Supabase stores the user in `auth.users`; our `public.users` / `public.profiles` are mirrors.
    This runs for both Supabase-authenticated users (JWT ``sub``) and dev ``?user_id=`` callers.
    Email is taken from ``auth.users`` when available, else a deterministic dev placeholder.
    """
    existing_user = (
        await db.execute(select(User).where(User.id == user_id))
    ).scalar_one_or_none()
    auth_ok, auth_email = await _auth_user_info(user_id, db)

    if existing_user is None:
        email = auth_email or f"user-{user_id}@whattoeat.local"
        name = (auth_email.split("@")[0] if auth_email else "WhatToEat User")
        db.add(User(id=user_id, email=email, name=name))
        await db.flush()
        existing_user = (
            await db.execute(select(User).where(User.id == user_id))
        ).scalar_one()

    # Mirror into `public.profiles` only if `auth.users` has this id — profiles.id FKs to auth.users.
    if auth_ok:
        existing_profile = (
            await db.execute(select(Profile).where(Profile.id == user_id))
        ).scalar_one_or_none()
        if existing_profile is None:
            db.add(
                Profile(
                    id=user_id,
                    email=existing_user.email,
                    name=existing_user.name,
                )
            )
            await db.flush()


# ── POST /questionnaire ─────────────────────────────────────────────────────

async def submit_questionnaire(
    user_id: uuid.UUID,
    payload: QuestionnaireSubmitRequest,
    db: AsyncSession,
) -> dict:
    await _ensure_user_and_profile_for_questionnaire(user_id, db)

    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == user_id)
    )
    existing = result.scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Questionnaire already submitted — use PATCH /users/me/preferences to update",
        )

    height_cm = _convert_height_to_cm(payload.height, payload.height_unit)
    weight_kg = _convert_weight_to_kg(payload.weight, payload.weight_unit)
    goal_weight_kg = _convert_weight_to_kg(payload.goal_weight, payload.weight_unit)

    targets = _calculate_targets(
        payload.gender, height_cm, weight_kg, payload.birthday, payload.diet_type,
    )

    pref = UserPreference(
        user_id=user_id,
        birthday=date.fromisoformat(payload.birthday),
        gender=payload.gender,
        height=height_cm,
        weight=weight_kg,
        goal_weight=goal_weight_kg,
        diet_type=payload.diet_type,
        dislikes=payload.dislikes,
        allergens=payload.allergens,
        favorite_dining_halls=payload.favorite_dining_halls,
        **targets,
    )
    db.add(pref)
    await db.commit()

    return {"message": "Questionnaire saved successfully"}


# ── GET /users/me/preferences ───────────────────────────────────────────────

async def get_preferences(
    user_id: uuid.UUID,
    db: AsyncSession,
) -> PreferencesResponse:
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == user_id)
    )
    pref = result.scalar_one_or_none()
    if pref is None:
        raise HTTPException(
            status_code=404,
            detail="Preferences not yet set — complete the questionnaire first",
        )

    return PreferencesResponse(
        birthday=str(pref.birthday) if pref.birthday else None,
        gender=pref.gender,
        height=float(pref.height) if pref.height is not None else None,
        weight=float(pref.weight) if pref.weight is not None else None,
        goal_weight=float(pref.goal_weight) if pref.goal_weight is not None else None,
        diet_type=pref.diet_type,
        dislikes=pref.dislikes or [],
        allergens=pref.allergens or [],
        favorite_dining_halls=pref.favorite_dining_halls or [],
        target_calories=pref.target_calories,
        target_protein_g=pref.target_protein_g,
        target_carbs_g=pref.target_carbs_g,
        target_fat_g=pref.target_fat_g,
    )


# ── PATCH /users/me/preferences ─────────────────────────────────────────────

async def update_preferences(
    user_id: uuid.UUID,
    payload: PreferencesUpdateRequest,
    db: AsyncSession,
) -> dict:
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == user_id)
    )
    pref = result.scalar_one_or_none()
    if pref is None:
        raise HTTPException(
            status_code=404,
            detail="Preferences not yet set — complete the questionnaire first",
        )

    if payload.birthday is not None:
        pref.birthday = date.fromisoformat(payload.birthday)
    if payload.gender is not None:
        pref.gender = payload.gender
    if payload.height is not None:
        pref.height = _convert_height_to_cm(payload.height, payload.height_unit)
    if payload.weight is not None:
        pref.weight = _convert_weight_to_kg(payload.weight, payload.weight_unit)
    if payload.goal_weight is not None:
        pref.goal_weight = _convert_weight_to_kg(payload.goal_weight, payload.weight_unit)
    if payload.diet_type is not None:
        pref.diet_type = payload.diet_type
    if payload.dislikes is not None:
        pref.dislikes = payload.dislikes
    if payload.allergens is not None:
        pref.allergens = payload.allergens
    if payload.favorite_dining_halls is not None:
        pref.favorite_dining_halls = payload.favorite_dining_halls

    # Recalculate targets when body metrics or diet change
    recalc_fields = {payload.weight, payload.height, payload.goal_weight, payload.diet_type}
    if any(v is not None for v in recalc_fields):
        targets = _calculate_targets(
            pref.gender,
            float(pref.height) if pref.height is not None else None,
            float(pref.weight) if pref.weight is not None else None,
            str(pref.birthday) if pref.birthday else None,
            pref.diet_type,
        )
        for k, v in targets.items():
            setattr(pref, k, v)

    await db.commit()
    return {"message": "Preferences updated successfully"}
