from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tracking import MealLog, MealLogItem
from app.models.user import User


_ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/heic",
    "image/heif",
    "application/octet-stream",
}

_ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".heif"}


_FOOD_TEMPLATES = [
    [
        {"name": "Grilled Chicken Breast", "confidence": 0.93, "calories": 310, "protein": 34, "carbs": 2, "fat": 14},
        {"name": "Steamed Broccoli", "confidence": 0.88, "calories": 55, "protein": 4, "carbs": 11, "fat": 1},
    ],
    [
        {"name": "Turkey Sandwich", "confidence": 0.91, "calories": 420, "protein": 27, "carbs": 41, "fat": 16},
        {"name": "Apple Slices", "confidence": 0.86, "calories": 70, "protein": 0, "carbs": 19, "fat": 0},
    ],
    [
        {"name": "Tofu Stir Fry", "confidence": 0.89, "calories": 460, "protein": 24, "carbs": 45, "fat": 19},
    ],
    [
        {"name": "Salmon Rice Bowl", "confidence": 0.9, "calories": 640, "protein": 36, "carbs": 58, "fat": 29},
    ],
]


async def _get_user_or_404(user_id: uuid.UUID, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _normalize_meal_type(value: str | None) -> str:
    if value and value.strip():
        return value.strip()

    hour = datetime.now(timezone.utc).hour - 5  # rough CDT offset
    if hour < 0:
        hour += 24
    if hour < 10:
        return "Breakfast"
    if hour < 15:
        return "Lunch"
    return "Dinner"


def _validate_upload(file: UploadFile) -> None:
    filename = (file.filename or "").strip()
    if not filename:
        raise HTTPException(status_code=400, detail="Image filename is required")

    ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use JPEG, PNG, HEIC, or HEIF")

    content_type = file.content_type or "application/octet-stream"
    if content_type not in _ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported media type")


def _select_template(image_bytes: bytes, filename: str) -> list[dict]:
    checksum = len(image_bytes) + sum(image_bytes[:256]) + sum(ord(ch) for ch in filename)
    idx = checksum % len(_FOOD_TEMPLATES)
    return _FOOD_TEMPLATES[idx]


def _build_summary(items: list[dict]) -> dict:
    return {
        "kcal": round(sum(float(i["calories"]) for i in items), 1),
        "protein": round(sum(float(i["protein"]) for i in items), 1),
        "carbs": round(sum(float(i["carbs"]) for i in items), 1),
        "fat": round(sum(float(i["fat"]) for i in items), 1),
    }


async def scan_image(user_id: uuid.UUID, image: UploadFile, db: AsyncSession) -> dict:
    await _get_user_or_404(user_id, db)
    _validate_upload(image)

    raw = await image.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Image payload is empty")

    items = _select_template(raw, image.filename or "upload.jpg")
    if not items:
        raise HTTPException(status_code=422, detail="Could not identify food in the image")

    return {
        "scanId": str(uuid.uuid4()),
        "items": items,
        "summary": _build_summary(items),
    }


async def log_scan_result(
    user_id: uuid.UUID,
    scan_id: str | None,
    items: list[dict],
    meal_type: str | None,
    req_date: str | None,
    db: AsyncSession,
) -> dict:
    await _get_user_or_404(user_id, db)

    if not items:
        raise HTTPException(status_code=400, detail="items cannot be empty")

    try:
        target_date = date.fromisoformat(req_date) if req_date else date.today()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="date must be YYYY-MM-DD") from exc

    normalized_meal_type = _normalize_meal_type(meal_type)

    result = await db.execute(
        select(MealLog).where(
            MealLog.user_id == user_id,
            MealLog.date == target_date,
            MealLog.meal_type == normalized_meal_type,
        )
    )
    meal_log = result.scalar_one_or_none()

    if meal_log is None:
        meal_log = MealLog(user_id=user_id, date=target_date, meal_type=normalized_meal_type)
        db.add(meal_log)
        await db.flush()

    for item in items:
        db.add(
            MealLogItem(
                meal_log_id=meal_log.id,
                food_id=None,
                food_name=item["name"],
                quantity=1.0,
                calories=float(item["calories"]),
                g_protein=float(item["protein"]),
                g_carbs=float(item["carbs"]),
                g_fat=float(item["fat"]),
                source="scan",
            )
        )

    await db.commit()

    suffix = f" (scanId: {scan_id})" if scan_id else ""
    return {
        "message": f"Food log saved successfully{suffix}",
        "loggedCount": len(items),
        "mealLogId": meal_log.id,
    }
