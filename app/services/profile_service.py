from __future__ import annotations

import os
import uuid
import shutil
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.community import (
    CommunityPost,
    CommunityPostLike,
    CommunityReply,
    CommunityReplyLike,
)
from app.models.tracking import Favorite, MealLog, MealLogItem, UserPreference
from app.models.user import Profile
from app.schemas.profile import (
    FoodLogCreateRequest,
    FoodLogEntryResponse,
    FoodLogListResponse,
    FoodLogSummaryResponse,
    ProfileResponse,
    ProfileUpdateRequest,
    WeightEntry,
)

_ALLOWED_AVATAR_EXTENSIONS = {".jpg", ".jpeg", ".png"}
_UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads/avatars"))


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_profile_or_404(
    user_id: uuid.UUID, db: AsyncSession
) -> Profile:
    result = await db.execute(select(Profile).where(Profile.id == user_id))
    profile = result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


async def _get_preference(
    user_id: uuid.UUID, db: AsyncSession
) -> UserPreference | None:
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def _get_or_create_preference(
    user_id: uuid.UUID, db: AsyncSession
) -> UserPreference:
    pref = await _get_preference(user_id, db)
    if pref is None:
        pref = UserPreference(user_id=user_id)
        db.add(pref)
        await db.flush()
    return pref


def _build_profile_response(
    profile: Profile, pref: UserPreference | None
) -> ProfileResponse:
    return ProfileResponse(
        id=str(profile.id),
        email=profile.email,
        name=profile.name,
        birthday=str(pref.birthday) if pref and pref.birthday else None,
        gender=pref.gender if pref else None,
        height=float(pref.height) if pref and pref.height is not None else None,
        weight=float(pref.weight) if pref and pref.weight is not None else None,
        goalWeight=float(pref.goal_weight) if pref and pref.goal_weight is not None else None,
        dietType=pref.diet_type if pref else None,
        avatarUrl=profile.avatar_url,
        createdAt=profile.created_at,
    )


# ── GET /users/me ────────────────────────────────────────────────────────────

async def get_profile(user_id: uuid.UUID, db: AsyncSession) -> ProfileResponse:
    profile = await _get_profile_or_404(user_id, db)
    pref = await _get_preference(user_id, db)
    return _build_profile_response(profile, pref)


# ── PATCH /users/me ──────────────────────────────────────────────────────────

async def update_profile(
    user_id: uuid.UUID, payload: ProfileUpdateRequest, db: AsyncSession
) -> dict:
    profile = await _get_profile_or_404(user_id, db)

    if payload.name is not None:
        profile.name = payload.name

    pref_fields = {
        "birthday": payload.birthday,
        "gender": payload.gender,
        "height": payload.height,
        "weight": payload.weight,
        "goal_weight": payload.goalWeight,
        "diet_type": payload.dietType,
    }
    has_pref_update = any(v is not None for v in pref_fields.values())

    if has_pref_update:
        pref = await _get_or_create_preference(user_id, db)
        for field, value in pref_fields.items():
            if value is not None:
                setattr(pref, field, value)

    await db.commit()
    return {"message": "Profile updated successfully"}


# ── DELETE /users/me ─────────────────────────────────────────────────────────

async def delete_account(user_id: uuid.UUID, db: AsyncSession) -> dict:
    await _get_profile_or_404(user_id, db)

    # Gather community post/reply IDs owned by user
    post_ids_result = await db.execute(
        select(CommunityPost.id).where(CommunityPost.user_id == user_id)
    )
    post_ids = [r[0] for r in post_ids_result.all()]

    reply_ids_result = await db.execute(
        select(CommunityReply.id).where(CommunityReply.user_id == user_id)
    )
    reply_ids = [r[0] for r in reply_ids_result.all()]

    # Delete in FK-safe order
    if reply_ids:
        await db.execute(
            delete(CommunityReplyLike).where(CommunityReplyLike.reply_id.in_(reply_ids))
        )
    await db.execute(
        delete(CommunityReplyLike).where(CommunityReplyLike.user_id == user_id)
    )

    if reply_ids:
        # Delete child replies first (nested replies)
        await db.execute(
            delete(CommunityReply).where(CommunityReply.parent_reply_id.in_(reply_ids))
        )
    await db.execute(
        delete(CommunityReply).where(CommunityReply.user_id == user_id)
    )

    if post_ids:
        await db.execute(
            delete(CommunityPostLike).where(CommunityPostLike.post_id.in_(post_ids))
        )
    await db.execute(
        delete(CommunityPostLike).where(CommunityPostLike.user_id == user_id)
    )

    await db.execute(
        delete(CommunityPost).where(CommunityPost.user_id == user_id)
    )

    # Meal log items → meal logs
    log_ids_result = await db.execute(
        select(MealLog.id).where(MealLog.user_id == user_id)
    )
    log_ids = [r[0] for r in log_ids_result.all()]
    if log_ids:
        await db.execute(
            delete(MealLogItem).where(MealLogItem.meal_log_id.in_(log_ids))
        )
    await db.execute(delete(MealLog).where(MealLog.user_id == user_id))

    await db.execute(delete(Favorite).where(Favorite.user_id == user_id))
    await db.execute(delete(UserPreference).where(UserPreference.user_id == user_id))
    await db.execute(delete(Profile).where(Profile.id == user_id))

    await db.commit()
    return {"message": "Account deleted successfully"}


# ── GET /users/me/food-log ───────────────────────────────────────────────────

async def get_food_log(
    user_id: uuid.UUID,
    filter_date: str | None,
    page: int,
    limit: int,
    db: AsyncSession,
) -> FoodLogListResponse:
    base = (
        select(MealLogItem)
        .join(MealLog, MealLogItem.meal_log_id == MealLog.id)
        .where(MealLog.user_id == user_id)
    )

    if filter_date:
        try:
            d = date.fromisoformat(filter_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="date must be YYYY-MM-DD")
        base = base.where(MealLog.date == d)

    count_result = await db.execute(
        select(func.count()).select_from(base.subquery())
    )
    total = count_result.scalar() or 0

    offset = (page - 1) * limit
    items_result = await db.execute(
        base.order_by(MealLogItem.logged_at.desc()).offset(offset).limit(limit)
    )
    items = items_result.scalars().all()

    entries = [
        FoodLogEntryResponse(
            id=item.id,
            name=item.food_name,
            calories=float(item.calories) if item.calories is not None else None,
            protein=float(item.g_protein) if item.g_protein is not None else None,
            carbs=float(item.g_carbs) if item.g_carbs is not None else None,
            fat=float(item.g_fat) if item.g_fat is not None else None,
            source=item.source,
            loggedAt=item.logged_at,
        )
        for item in items
    ]

    return FoodLogListResponse(entries=entries, total=total, page=page, limit=limit)


# ── POST /users/me/food-log ─────────────────────────────────────────────────

async def create_food_log_entry(
    user_id: uuid.UUID, payload: FoodLogCreateRequest, db: AsyncSession
) -> dict:
    try:
        target_date = date.fromisoformat(payload.date) if payload.date else date.today()
    except ValueError:
        raise HTTPException(status_code=400, detail="date must be YYYY-MM-DD")

    # Find or create a meal log for this date
    result = await db.execute(
        select(MealLog).where(
            MealLog.user_id == user_id,
            MealLog.date == target_date,
        ).limit(1)
    )
    meal_log = result.scalar_one_or_none()

    if meal_log is None:
        meal_log = MealLog(user_id=user_id, date=target_date, meal_type="Manual")
        db.add(meal_log)
        await db.flush()

    item = MealLogItem(
        meal_log_id=meal_log.id,
        food_name=payload.name,
        quantity=1.0,
        calories=payload.calories,
        g_protein=payload.protein,
        g_carbs=payload.carbs,
        g_fat=payload.fat,
        source="manual",
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)

    return {"id": str(item.id), "message": "Food log entry added successfully"}


# ── DELETE /users/me/food-log/:entryId ───────────────────────────────────────

async def delete_food_log_entry(
    user_id: uuid.UUID, entry_id: int, db: AsyncSession
) -> dict:
    result = await db.execute(
        select(MealLogItem)
        .join(MealLog, MealLogItem.meal_log_id == MealLog.id)
        .where(MealLogItem.id == entry_id, MealLog.user_id == user_id)
    )
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Entry not found or does not belong to the current user",
        )

    meal_log_id = item.meal_log_id
    await db.delete(item)

    # Clean up empty meal log
    remaining = await db.execute(
        select(func.count()).where(MealLogItem.meal_log_id == meal_log_id)
    )
    if (remaining.scalar() or 0) == 0:
        await db.execute(delete(MealLog).where(MealLog.id == meal_log_id))

    await db.commit()
    return {"message": "Food log entry deleted successfully"}


# ── GET /users/me/food-log/summary ──────────────────────────────────────────

async def get_food_log_summary(
    user_id: uuid.UUID, range_str: str, db: AsyncSession
) -> FoodLogSummaryResponse:
    today = date.today()

    if range_str == "week":
        start_date = today - timedelta(days=7)
    elif range_str == "month":
        start_date = today - timedelta(days=30)
    else:
        start_date = None

    base = (
        select(
            MealLog.date,
            func.sum(MealLogItem.calories).label("kcal"),
            func.sum(MealLogItem.g_protein).label("protein"),
            func.sum(MealLogItem.g_carbs).label("carbs"),
            func.sum(MealLogItem.g_fat).label("fat"),
            func.count(MealLogItem.id).label("item_count"),
        )
        .join(MealLogItem, MealLogItem.meal_log_id == MealLog.id)
        .where(MealLog.user_id == user_id)
    )
    if start_date:
        base = base.where(MealLog.date >= start_date)
    base = base.group_by(MealLog.date)

    result = await db.execute(base)
    rows = result.all()

    if not rows:
        return FoodLogSummaryResponse(
            range=range_str,
            averageDailyCalories=0,
            averageDailyProtein=0,
            averageDailyCarbs=0,
            averageDailyFat=0,
            totalMealsLogged=0,
            currentStreak=0,
            longestStreak=0,
        )

    num_days = len(rows)
    total_kcal = sum(float(r.kcal or 0) for r in rows)
    total_protein = sum(float(r.protein or 0) for r in rows)
    total_carbs = sum(float(r.carbs or 0) for r in rows)
    total_fat = sum(float(r.fat or 0) for r in rows)
    total_items = sum(int(r.item_count) for r in rows)

    # Streak calculation
    logged_dates = sorted({r.date for r in rows}, reverse=True)
    current_streak = 0
    check = today
    for d in logged_dates:
        if d == check:
            current_streak += 1
            check -= timedelta(days=1)
        elif d < check:
            break

    longest_streak = 0
    streak = 0
    for i, d in enumerate(sorted(logged_dates)):
        if i == 0:
            streak = 1
        elif d == sorted(logged_dates)[i - 1] + timedelta(days=1):
            streak += 1
        else:
            streak = 1
        longest_streak = max(longest_streak, streak)

    return FoodLogSummaryResponse(
        range=range_str,
        averageDailyCalories=round(total_kcal / num_days, 1),
        averageDailyProtein=round(total_protein / num_days, 1),
        averageDailyCarbs=round(total_carbs / num_days, 1),
        averageDailyFat=round(total_fat / num_days, 1),
        totalMealsLogged=total_items,
        currentStreak=current_streak,
        longestStreak=longest_streak,
    )


# ── POST /users/me/avatar ───────────────────────────────────────────────────

async def upload_avatar(
    user_id: uuid.UUID, file: UploadFile, db: AsyncSession
) -> dict:
    profile = await _get_profile_or_404(user_id, db)

    filename = (file.filename or "").strip()
    if not filename:
        raise HTTPException(status_code=400, detail="Image filename is required")

    ext = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""
    if ext not in _ALLOWED_AVATAR_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Use JPEG or PNG.",
        )

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Image payload is empty")

    _UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    dest = _UPLOAD_DIR / f"{user_id}{ext}"
    dest.write_bytes(data)

    avatar_url = f"/uploads/avatars/{user_id}{ext}"
    profile.avatar_url = avatar_url
    await db.commit()

    return {"message": "Avatar updated successfully", "avatarUrl": avatar_url}


# ── POST /users/me/change-password ──────────────────────────────────────────

async def change_password(
    user_id: uuid.UUID, current_password: str, new_password: str
) -> dict:
    if len(new_password) < 8:
        raise HTTPException(
            status_code=400,
            detail="New password must be at least 8 characters",
        )

    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not service_key:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Password change is not configured (missing Supabase credentials)",
        )

    # Verify current password by attempting sign-in
    profile_url = f"{supabase_url}/auth/v1/user"
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
    }

    # Get user email first
    user_resp = requests.get(
        f"{supabase_url}/auth/v1/admin/users/{user_id}",
        headers=headers,
        timeout=10,
    )
    if user_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Could not verify user")

    user_data = user_resp.json()
    email = user_data.get("email")

    # Skip for OAuth-only users
    providers = [
        i.get("provider")
        for i in user_data.get("identities", [])
    ]
    if "email" not in providers:
        raise HTTPException(
            status_code=400,
            detail="Password change is not available for OAuth users",
        )

    # Verify current password
    verify_resp = requests.post(
        f"{supabase_url}/auth/v1/token?grant_type=password",
        json={"email": email, "password": current_password},
        headers={"apikey": service_key, "Content-Type": "application/json"},
        timeout=10,
    )
    if verify_resp.status_code != 200:
        raise HTTPException(
            status_code=400, detail="Current password is incorrect"
        )

    # Update password
    update_resp = requests.put(
        f"{supabase_url}/auth/v1/admin/users/{user_id}",
        json={"password": new_password},
        headers=headers,
        timeout=10,
    )
    if update_resp.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail="Failed to update password",
        )

    return {"message": "Password changed successfully"}
