import uuid
from datetime import date, datetime, timezone

from sqlalchemy import select, func as sqla_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.menu import (
    Restaurant, MealType, Food, FoodNutrition, FoodIcon,
    FoodIconAssignment, MenuSnapshot, MenuSection, MenuSectionItem,
)
from app.models.tracking import UserPreference, MealLog, MealLogItem, Favorite


# ─── Helpers ──────────────────────────────────────────────


def _infer_meal_type() -> str | None:
    """Infer the current meal period from time of day."""
    hour = datetime.now(timezone.utc).hour - 5  # rough CDT offset
    if hour < 0:
        hour += 24
    if hour < 10:
        return "Breakfast"
    elif hour < 15:
        return "Lunch"
    else:
        return "Dinner"


def _compute_combo_label(protein: float, carbs: float, fat: float, calories: float) -> str:
    """Generate a descriptive label like 'HIGH PROTEIN LEAN BULK' based on macro ratios."""
    if calories == 0:
        return "BALANCED"
    protein_pct = (protein * 4) / calories * 100
    fat_pct = (fat * 9) / calories * 100
    if protein_pct >= 35:
        if fat_pct <= 25:
            return "HIGH PROTEIN LEAN BULK"
        return "HIGH PROTEIN"
    if fat_pct <= 20:
        return "LOW FAT"
    if protein_pct >= 25:
        return "PROTEIN RICH"
    return "BALANCED"


async def _get_user_prefs(user_id: uuid.UUID, db: AsyncSession) -> UserPreference | None:
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def _get_allergen_food_ids(allergen_slugs: list[str], db: AsyncSession) -> set[int]:
    """Get food IDs that have any of the given allergen icons."""
    if not allergen_slugs:
        return set()
    result = await db.execute(
        select(FoodIconAssignment.food_id)
        .join(FoodIcon, FoodIconAssignment.icon_id == FoodIcon.id)
        .where(FoodIcon.slug.in_(allergen_slugs))
    )
    return {row[0] for row in result.all()}


async def _get_foods_for_snapshot(
    snapshot_id: int, db: AsyncSession
) -> list[dict]:
    """Get all food items with nutrition for a menu snapshot."""
    result = await db.execute(
        select(
            Food.id,
            Food.name,
            FoodNutrition.calories,
            FoodNutrition.g_protein,
            FoodNutrition.g_carbs,
            FoodNutrition.g_fat,
            MenuSectionItem.station_name,
            MenuSectionItem.serving_size_amount,
            MenuSectionItem.serving_size_unit,
        )
        .join(MenuSectionItem, MenuSectionItem.food_id == Food.id)
        .join(MenuSection, MenuSectionItem.section_id == MenuSection.id)
        .outerjoin(FoodNutrition, FoodNutrition.food_id == Food.id)
        .where(
            MenuSection.snapshot_id == snapshot_id,
            MenuSectionItem.food_id.isnot(None),
        )
        .order_by(MenuSectionItem.position)
    )
    rows = result.all()
    return [
        {
            "id": r[0],
            "name": r[1],
            "calories": float(r[2]) if r[2] else 0,
            "protein": float(r[3]) if r[3] else 0,
            "carbs": float(r[4]) if r[4] else 0,
            "fat": float(r[5]) if r[5] else 0,
            "station": r[6],
            "servingSizeAmount": r[7],
            "servingSizeUnit": r[8],
        }
        for r in rows
    ]


# ─── GET /recommendations/combo ──────────────────────────


async def get_combos(
    user_id: uuid.UUID,
    target_date: date,
    meal_type_filter: str | None,
    db: AsyncSession,
) -> dict:
    prefs = await _get_user_prefs(user_id, db)

    # Get allergen and dislike filters
    allergen_slugs = prefs.allergens if prefs and prefs.allergens else []
    dislikes = prefs.dislikes if prefs and prefs.dislikes else []
    allergen_food_ids = await _get_allergen_food_ids(allergen_slugs, db)

    # Determine meal type
    if meal_type_filter:
        mt_name = meal_type_filter.capitalize()
    else:
        mt_name = _infer_meal_type()

    # Find matching snapshots
    snapshot_query = (
        select(MenuSnapshot.id, Restaurant.name.label("hall_name"))
        .join(Restaurant, MenuSnapshot.restaurant_id == Restaurant.id)
        .join(MealType, MenuSnapshot.meal_type_id == MealType.id)
        .where(MenuSnapshot.service_date == target_date)
    )
    if mt_name:
        snapshot_query = snapshot_query.where(MealType.name == mt_name)

    snapshots = (await db.execute(snapshot_query)).all()

    # Nutrition targets (defaults if no prefs)
    target_cal = (prefs.target_calories if prefs and prefs.target_calories else 2000) / 3
    target_pro = (prefs.target_protein_g if prefs and prefs.target_protein_g else 120) / 3
    target_carb = (prefs.target_carbs_g if prefs and prefs.target_carbs_g else 250) / 3
    target_fat = (prefs.target_fat_g if prefs and prefs.target_fat_g else 65) / 3

    # Check which combos are already logged for this date
    logged_food_ids: set[int] = set()
    log_result = await db.execute(
        select(MealLogItem.food_id)
        .join(MealLog, MealLogItem.meal_log_id == MealLog.id)
        .where(
            MealLog.user_id == user_id,
            MealLog.date == target_date,
            MealLogItem.food_id.isnot(None),
        )
    )
    logged_food_ids = {row[0] for row in log_result.all()}

    combos = []
    for snap_id, hall_name in snapshots:
        foods = await _get_foods_for_snapshot(snap_id, db)

        # Filter out allergens and dislikes
        filtered = [
            f for f in foods
            if f["id"] not in allergen_food_ids
            and f["name"].lower() not in [d.lower() for d in dislikes]
        ]

        if not filtered:
            continue

        # Simple combo: pick foods that best approach calorie target per meal
        # Sort by calorie density and pick items greedily
        selected = []
        running_cal = 0.0
        for food in sorted(filtered, key=lambda f: f["calories"], reverse=True):
            if running_cal + food["calories"] <= target_cal * 1.2:
                selected.append(food)
                running_cal += food["calories"]
            if running_cal >= target_cal * 0.8:
                break

        # If we didn't get enough, add lower-calorie items
        if running_cal < target_cal * 0.5 and filtered:
            for food in filtered:
                if food not in selected:
                    selected.append(food)
                    running_cal += food["calories"]
                    if running_cal >= target_cal * 0.6:
                        break

        if not selected:
            continue

        total_cal = sum(f["calories"] for f in selected)
        total_pro = sum(f["protein"] for f in selected)
        total_carb = sum(f["carbs"] for f in selected)
        total_fat = sum(f["fat"] for f in selected)

        # Compute label based on dominant macro ratio
        label = _compute_combo_label(total_pro, total_carb, total_fat, total_cal)

        # Check if all items in this combo are logged
        combo_logged = all(f["id"] in logged_food_ids for f in selected)

        combo_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{snap_id}-{'-'.join(str(f['id']) for f in selected)}"))

        combos.append({
            "id": combo_id,
            "name": f"Balanced {mt_name or 'Meal'}",
            "label": label,
            "items": [
                {
                    "id": f["id"],
                    "name": f["name"],
                    "calories": f["calories"],
                    "protein": f["protein"],
                    "carbs": f["carbs"],
                    "fat": f["fat"],
                    "station": f["station"],
                    "servingSizeAmount": f.get("servingSizeAmount"),
                    "servingSizeUnit": f.get("servingSizeUnit"),
                }
                for f in selected
            ],
            "totalCalories": round(total_cal, 1),
            "totalProtein": round(total_pro, 1),
            "totalCarbs": round(total_carb, 1),
            "totalFat": round(total_fat, 1),
            "diningHall": hall_name,
            "logged": combo_logged,
        })

    return {"combos": combos}


# ─── GET /goals/daily ────────────────────────────────────


async def get_daily_goals(
    user_id: uuid.UUID,
    target_date: date,
    db: AsyncSession,
) -> dict:
    prefs = await _get_user_prefs(user_id, db)

    goal_cal = prefs.target_calories if prefs and prefs.target_calories else 2000
    goal_pro = prefs.target_protein_g if prefs and prefs.target_protein_g else 120
    goal_carb = prefs.target_carbs_g if prefs and prefs.target_carbs_g else 250
    goal_fat = prefs.target_fat_g if prefs and prefs.target_fat_g else 65

    # Sum consumed from meal_log_items for the given date
    result = await db.execute(
        select(
            sqla_func.coalesce(sqla_func.sum(MealLogItem.calories), 0),
            sqla_func.coalesce(sqla_func.sum(MealLogItem.g_protein), 0),
            sqla_func.coalesce(sqla_func.sum(MealLogItem.g_carbs), 0),
            sqla_func.coalesce(sqla_func.sum(MealLogItem.g_fat), 0),
        )
        .join(MealLog, MealLogItem.meal_log_id == MealLog.id)
        .where(MealLog.user_id == user_id, MealLog.date == target_date)
    )
    row = result.one()

    return {
        "date": target_date.isoformat(),
        "calories": {"goal": goal_cal, "consumed": float(row[0])},
        "protein": {"goal": goal_pro, "consumed": float(row[1])},
        "carbs": {"goal": goal_carb, "consumed": float(row[2])},
        "fat": {"goal": goal_fat, "consumed": float(row[3])},
    }


# ─── GET /menus/summary ──────────────────────────────────


async def get_menu_summary(
    user_id: uuid.UUID,
    target_date: date,
    db: AsyncSession,
    meal_type_filter: str | None = None,
) -> dict:
    prefs = await _get_user_prefs(user_id, db)
    allergen_slugs = prefs.allergens if prefs and prefs.allergens else []
    dislikes = prefs.dislikes if prefs and prefs.dislikes else []
    allergen_food_ids = await _get_allergen_food_ids(allergen_slugs, db)

    # Determine meal type filter
    mt_name = meal_type_filter.capitalize() if meal_type_filter else None

    # Get snapshots for the date, optionally filtered by meal type
    snapshot_query = (
        select(MenuSnapshot.id, Restaurant.id.label("hall_id"), Restaurant.name.label("hall_name"))
        .join(Restaurant, MenuSnapshot.restaurant_id == Restaurant.id)
        .join(MealType, MenuSnapshot.meal_type_id == MealType.id)
        .where(MenuSnapshot.service_date == target_date)
    )
    if mt_name:
        snapshot_query = snapshot_query.where(MealType.name == mt_name)

    snapshots = (await db.execute(snapshot_query)).all()

    # Group by dining hall
    hall_snapshots: dict[int, dict] = {}
    for snap_id, hall_id, hall_name in snapshots:
        if hall_id not in hall_snapshots:
            hall_snapshots[hall_id] = {"id": hall_id, "name": hall_name, "snapshot_ids": []}
        hall_snapshots[hall_id]["snapshot_ids"].append(snap_id)

    dining_halls = []
    for hall_id, info in hall_snapshots.items():
        all_items = []
        for snap_id in info["snapshot_ids"]:
            foods = await _get_foods_for_snapshot(snap_id, db)
            all_items.extend(foods)

        # Filter
        filtered = [
            f for f in all_items
            if f["id"] not in allergen_food_ids
            and f["name"].lower() not in [d.lower() for d in dislikes]
        ]

        # Get icons for these foods
        food_ids = [f["id"] for f in filtered]
        if food_ids:
            icon_result = await db.execute(
                select(FoodIconAssignment.food_id, FoodIcon.slug)
                .join(FoodIcon, FoodIconAssignment.icon_id == FoodIcon.id)
                .where(FoodIconAssignment.food_id.in_(food_ids))
            )
            food_icons: dict[int, list[str]] = {}
            for fid, slug in icon_result.all():
                food_icons.setdefault(fid, []).append(slug)
        else:
            food_icons = {}

        # Deduplicate by food id and take top 5 by calories
        seen = set()
        unique = []
        for f in sorted(filtered, key=lambda x: x["calories"], reverse=True):
            if f["id"] not in seen:
                seen.add(f["id"])
                unique.append(f)
            if len(unique) >= 5:
                break

        dining_halls.append({
            "id": info["id"],
            "name": info["name"],
            "recommendedItems": [
                {
                    "id": f["id"],
                    "name": f["name"],
                    "calories": f["calories"],
                    "protein": f["protein"],
                    "carbs": f["carbs"],
                    "fat": f["fat"],
                    "station": f["station"],
                    "icons": food_icons.get(f["id"], []),
                }
                for f in unique
            ],
        })

    return {"date": target_date.isoformat(), "diningHalls": dining_halls}


# ─── POST /meals/log ─────────────────────────────────────


async def log_meal(
    user_id: uuid.UUID,
    req_date: str,
    meal_type: str,
    items: list[dict],
    db: AsyncSession,
) -> dict:
    meal_date = date.fromisoformat(req_date)

    # Find or create meal log for this user/date/mealType
    result = await db.execute(
        select(MealLog).where(
            MealLog.user_id == user_id,
            MealLog.date == meal_date,
            MealLog.meal_type == meal_type,
        )
    )
    meal_log = result.scalar_one_or_none()

    if not meal_log:
        meal_log = MealLog(user_id=user_id, date=meal_date, meal_type=meal_type)
        db.add(meal_log)
        await db.flush()

    # Add items
    for item in items:
        # If foodId provided, look up nutrition from DB
        calories = item.get("calories")
        protein = item.get("protein")
        carbs = item.get("carbs")
        fat = item.get("fat")

        if item.get("foodId") and (calories is None):
            nut_result = await db.execute(
                select(FoodNutrition).where(FoodNutrition.food_id == item["foodId"])
            )
            nut = nut_result.scalar_one_or_none()
            if nut:
                calories = float(nut.calories) if nut.calories else None
                protein = float(nut.g_protein) if nut.g_protein else None
                carbs = float(nut.g_carbs) if nut.g_carbs else None
                fat = float(nut.g_fat) if nut.g_fat else None

        log_item = MealLogItem(
            meal_log_id=meal_log.id,
            food_id=item.get("foodId"),
            food_name=item["foodName"],
            quantity=item.get("quantity", 1.0),
            calories=calories,
            g_protein=protein,
            g_carbs=carbs,
            g_fat=fat,
            source=item.get("source", "menu"),
        )
        db.add(log_item)

    await db.commit()
    return {"mealLogId": meal_log.id, "message": "Meal logged successfully"}


# ─── POST /favorites ─────────────────────────────────────


async def save_favorite(
    user_id: uuid.UUID,
    combo_id: str,
    combo_snapshot: dict,
    db: AsyncSession,
) -> dict:
    combo_uuid = uuid.UUID(combo_id)

    # Check for duplicate
    existing = await db.execute(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.combo_id == combo_uuid,
        )
    )
    if existing.scalar_one_or_none():
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail="Combo already in favorites")

    fav = Favorite(
        user_id=user_id,
        combo_id=combo_uuid,
        recommendation_snapshot=combo_snapshot,
    )
    db.add(fav)
    await db.commit()
    await db.refresh(fav)
    return {"id": str(fav.id), "message": "Combo saved to favorites"}


# ─── DELETE /favorites/{favoriteId} ──────────────────────


async def delete_favorite(
    user_id: uuid.UUID,
    favorite_id: uuid.UUID,
    db: AsyncSession,
) -> dict:
    from fastapi import HTTPException

    result = await db.execute(
        select(Favorite).where(Favorite.id == favorite_id)
    )
    fav = result.scalar_one_or_none()

    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")
    if fav.user_id != user_id:
        raise HTTPException(status_code=403, detail="Cannot delete another user's favorite")

    await db.delete(fav)
    await db.commit()
    return {"message": "Favorite removed successfully"}


# ─── GET /recommendations/addons ─────────────────────────


async def get_addons(
    user_id: uuid.UUID,
    target_date: date,
    meal_type_filter: str | None,
    db: AsyncSession,
) -> dict:
    prefs = await _get_user_prefs(user_id, db)
    allergen_slugs = prefs.allergens if prefs and prefs.allergens else []
    dislikes = prefs.dislikes if prefs and prefs.dislikes else []
    allergen_food_ids = await _get_allergen_food_ids(allergen_slugs, db)

    mt_name = meal_type_filter.capitalize() if meal_type_filter else _infer_meal_type()

    # Get snapshots for this meal period
    snapshot_query = (
        select(MenuSnapshot.id)
        .join(MealType, MenuSnapshot.meal_type_id == MealType.id)
        .where(MenuSnapshot.service_date == target_date)
    )
    if mt_name:
        snapshot_query = snapshot_query.where(MealType.name == mt_name)
    snapshots = (await db.execute(snapshot_query)).all()

    # Collect all available foods
    all_foods: list[dict] = []
    for (snap_id,) in snapshots:
        foods = await _get_foods_for_snapshot(snap_id, db)
        all_foods.extend(foods)

    # Filter out allergens and dislikes
    filtered = [
        f for f in all_foods
        if f["id"] not in allergen_food_ids
        and f["name"].lower() not in [d.lower() for d in dislikes]
    ]

    # Get icons for filtered foods
    food_ids = [f["id"] for f in filtered]
    food_icons: dict[int, list[str]] = {}
    if food_ids:
        icon_result = await db.execute(
            select(FoodIconAssignment.food_id, FoodIcon.slug)
            .join(FoodIcon, FoodIconAssignment.icon_id == FoodIcon.id)
            .where(FoodIconAssignment.food_id.in_(food_ids))
        )
        for fid, slug in icon_result.all():
            food_icons.setdefault(fid, []).append(slug)

    # Deduplicate
    seen: set[int] = set()
    unique: list[dict] = []
    for f in filtered:
        if f["id"] not in seen:
            seen.add(f["id"])
            unique.append(f)

    def _make_item(f: dict) -> dict:
        return {
            "id": f["id"],
            "name": f["name"],
            "calories": f["calories"],
            "protein": f["protein"],
            "carbs": f["carbs"],
            "fat": f["fat"],
            "station": f["station"],
            "icons": food_icons.get(f["id"], []),
        }

    # Suggestions: medium-calorie, balanced items (100-400 cal) — grid items
    suggestions = sorted(
        [f for f in unique if 100 <= f["calories"] <= 400],
        key=lambda f: f["protein"],
        reverse=True,
    )[:6]

    # Quick add-ons: low-calorie items (<150 cal) — chip/pill items
    quick = sorted(
        [f for f in unique if f["calories"] < 150 and f not in suggestions],
        key=lambda f: f["calories"],
    )[:8]

    return {
        "mealType": mt_name or "Meal",
        "suggestions": [_make_item(f) for f in suggestions],
        "quickAddons": [_make_item(f) for f in quick],
    }
