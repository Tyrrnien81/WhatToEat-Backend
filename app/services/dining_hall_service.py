import uuid
from datetime import date

from sqlalchemy import select, func as sqla_func, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.menu import (
    Restaurant, MealType, Food, FoodNutrition, FoodIcon,
    FoodIconAssignment, MenuSnapshot, MenuSection, MenuSectionItem,
)
from app.models.tracking import Favorite


# ─── Hall Metadata (static for 6 UW-Madison halls) ──────

HALL_META: dict[str, dict] = {
    "Gordon Avenue Market": {
        "slug": "gordon",
        "emoji": "🏛️",
        "emojiBg": "#FFE8D6",
        "mapsUrl": "https://maps.app.goo.gl/gordonavenue",
    },
    "Rheta's Market": {
        "slug": "rhetas",
        "emoji": "🥗",
        "emojiBg": "#D4EDDA",
        "mapsUrl": "https://maps.app.goo.gl/rhetasmarket",
    },
    "Four Lakes Market": {
        "slug": "four-lakes",
        "emoji": "🌊",
        "emojiBg": "#D6EAF8",
        "mapsUrl": "https://maps.app.goo.gl/fourlakes",
    },
    "Liz's Market": {
        "slug": "lizs",
        "emoji": "🍎",
        "emojiBg": "#FADBD8",
        "mapsUrl": "https://maps.app.goo.gl/lizsmarket",
    },
    "Carson's Market": {
        "slug": "carsons",
        "emoji": "🥪",
        "emojiBg": "#FEF9E7",
        "mapsUrl": "https://maps.app.goo.gl/carsonsmarket",
    },
    "Lowell Market": {
        "slug": "lowell",
        "emoji": "🍜",
        "emojiBg": "#F5EEF8",
        "mapsUrl": "https://maps.app.goo.gl/lowellmarket",
    },
}

_DEFAULT_META = {"slug": "unknown", "emoji": "🍽️", "emojiBg": "#F0F0F0", "mapsUrl": ""}


def _get_hall_meta(name: str) -> dict:
    return HALL_META.get(name, _DEFAULT_META)


# ─── GET /dining-halls ───────────────────────────────────


async def get_dining_halls(db: AsyncSession) -> dict:
    result = await db.execute(
        select(Restaurant).order_by(Restaurant.name)
    )
    halls = result.scalars().all()
    return {
        "diningHalls": [
            {
                "id": h.id,
                "name": h.name,
                "externalRestaurantId": h.external_restaurant_id,
            }
            for h in halls
        ]
    }


# ─── GET /dining-halls/{hallId} ──────────────────────────


async def get_dining_hall_detail(hall_id: int, db: AsyncSession) -> dict:
    result = await db.execute(
        select(Restaurant).where(Restaurant.id == hall_id)
    )
    hall = result.scalar_one_or_none()
    if not hall:
        raise HTTPException(status_code=404, detail="Dining hall not found")

    # Available meal types for this hall
    mt_result = await db.execute(
        select(distinct(MealType.name))
        .join(MenuSnapshot, MenuSnapshot.meal_type_id == MealType.id)
        .where(MenuSnapshot.restaurant_id == hall_id)
        .order_by(MealType.name)
    )
    meal_types = [row[0] for row in mt_result.all()]

    # Available dates
    date_result = await db.execute(
        select(distinct(MenuSnapshot.service_date))
        .where(MenuSnapshot.restaurant_id == hall_id)
        .order_by(MenuSnapshot.service_date.desc())
        .limit(30)
    )
    dates = [row[0].isoformat() for row in date_result.all()]

    return {
        "id": hall.id,
        "name": hall.name,
        "externalRestaurantId": hall.external_restaurant_id,
        "availableMealTypes": meal_types,
        "availableDates": dates,
    }


# ─── GET /dining-halls/{hallId}/stations ─────────────────


async def get_dining_hall_stations(
    hall_id: int,
    target_date: date,
    meal_type_filter: str | None,
    db: AsyncSession,
) -> dict:
    # Verify hall exists
    hall = await db.execute(
        select(Restaurant).where(Restaurant.id == hall_id)
    )
    if not hall.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Dining hall not found")

    # Find snapshots
    snap_query = (
        select(MenuSnapshot.id)
        .join(MealType, MenuSnapshot.meal_type_id == MealType.id)
        .where(
            MenuSnapshot.restaurant_id == hall_id,
            MenuSnapshot.service_date == target_date,
        )
    )
    if meal_type_filter:
        snap_query = snap_query.where(MealType.name == meal_type_filter.capitalize())

    snap_ids = [row[0] for row in (await db.execute(snap_query)).all()]

    if not snap_ids:
        return {
            "hallId": hall_id,
            "date": target_date.isoformat(),
            "mealType": meal_type_filter,
            "stations": [],
        }

    # Count items per station
    result = await db.execute(
        select(
            MenuSectionItem.station_name,
            sqla_func.count(MenuSectionItem.id),
        )
        .join(MenuSection, MenuSectionItem.section_id == MenuSection.id)
        .where(
            MenuSection.snapshot_id.in_(snap_ids),
            MenuSectionItem.food_id.isnot(None),
            MenuSectionItem.station_name.isnot(None),
        )
        .group_by(MenuSectionItem.station_name)
        .order_by(MenuSectionItem.station_name)
    )

    stations = [
        {"station": row[0], "itemCount": row[1]}
        for row in result.all()
    ]

    return {
        "hallId": hall_id,
        "date": target_date.isoformat(),
        "mealType": meal_type_filter,
        "stations": stations,
    }


# ─── GET /dining-halls/{hallId}/menus ────────────────────


async def get_dining_hall_menus(
    hall_id: int,
    target_date: date,
    meal_type_filter: str | None,
    db: AsyncSession,
) -> dict:
    # Verify hall exists
    hall_result = await db.execute(
        select(Restaurant).where(Restaurant.id == hall_id)
    )
    hall = hall_result.scalar_one_or_none()
    if not hall:
        raise HTTPException(status_code=404, detail="Dining hall not found")

    # Find snapshots
    snap_query = (
        select(MenuSnapshot.id)
        .join(MealType, MenuSnapshot.meal_type_id == MealType.id)
        .where(
            MenuSnapshot.restaurant_id == hall_id,
            MenuSnapshot.service_date == target_date,
        )
    )
    if meal_type_filter:
        snap_query = snap_query.where(MealType.name == meal_type_filter.capitalize())

    snap_ids = [row[0] for row in (await db.execute(snap_query)).all()]

    if not snap_ids:
        return {
            "hallId": hall_id,
            "hallName": hall.name,
            "date": target_date.isoformat(),
            "mealType": meal_type_filter,
            "stationMenus": [],
        }

    # Fetch all items with nutrition
    items_result = await db.execute(
        select(
            Food.id,
            Food.name,
            FoodNutrition.calories,
            FoodNutrition.g_protein,
            FoodNutrition.g_carbs,
            FoodNutrition.g_fat,
            MenuSectionItem.station_name,
            MenuSectionItem.category,
            MenuSectionItem.serving_size_amount,
            MenuSectionItem.serving_size_unit,
            MenuSectionItem.position,
        )
        .join(MenuSectionItem, MenuSectionItem.food_id == Food.id)
        .join(MenuSection, MenuSectionItem.section_id == MenuSection.id)
        .outerjoin(FoodNutrition, FoodNutrition.food_id == Food.id)
        .where(
            MenuSection.snapshot_id.in_(snap_ids),
            MenuSectionItem.food_id.isnot(None),
        )
        .order_by(MenuSectionItem.station_name, MenuSectionItem.position)
    )
    rows = items_result.all()

    # Get icons for all food IDs
    food_ids = list({r[0] for r in rows})
    food_icons: dict[int, list[str]] = {}
    if food_ids:
        icon_result = await db.execute(
            select(FoodIconAssignment.food_id, FoodIcon.slug)
            .join(FoodIcon, FoodIconAssignment.icon_id == FoodIcon.id)
            .where(FoodIconAssignment.food_id.in_(food_ids))
        )
        for fid, slug in icon_result.all():
            food_icons.setdefault(fid, []).append(slug)

    # Group by station
    station_groups: dict[str, list[dict]] = {}
    for r in rows:
        station = r[6] or "Other"
        item = {
            "id": r[0],
            "name": r[1],
            "calories": float(r[2]) if r[2] else None,
            "protein": float(r[3]) if r[3] else None,
            "carbs": float(r[4]) if r[4] else None,
            "fat": float(r[5]) if r[5] else None,
            "station": station,
            "category": r[7],
            "icons": food_icons.get(r[0], []),
            "servingSizeAmount": r[8],
            "servingSizeUnit": r[9],
        }
        station_groups.setdefault(station, []).append(item)

    station_menus = [
        {"station": station, "items": items}
        for station, items in station_groups.items()
    ]

    return {
        "hallId": hall_id,
        "hallName": hall.name,
        "date": target_date.isoformat(),
        "mealType": meal_type_filter,
        "stationMenus": station_menus,
    }


# ─── GET /dining-halls/full ─────────────────────────────
# Returns the nested structure the frontend expects:
# Each hall has days → meals → categories → items


async def get_dining_halls_full(
    target_date: date,
    user_id: uuid.UUID | None,
    db: AsyncSession,
) -> dict:
    # Get all restaurants
    halls_result = await db.execute(
        select(Restaurant).order_by(Restaurant.name)
    )
    halls = halls_result.scalars().all()

    # Get user favorites for favorited flag
    user_favorites: set[int] = set()
    if user_id:
        fav_result = await db.execute(
            select(Favorite.food_id).where(
                Favorite.user_id == user_id,
                Favorite.food_id.isnot(None),
            )
        )
        user_favorites = {row[0] for row in fav_result.all()}

    # Get all meal types
    mt_result = await db.execute(select(MealType))
    meal_type_map = {mt.id: mt.name for mt in mt_result.scalars().all()}

    dining_halls = []
    for hall in halls:
        meta = _get_hall_meta(hall.name)

        # Get all snapshots for this hall on the target date
        snaps_result = await db.execute(
            select(MenuSnapshot.id, MenuSnapshot.meal_type_id)
            .where(
                MenuSnapshot.restaurant_id == hall.id,
                MenuSnapshot.service_date == target_date,
            )
        )
        snapshots = snaps_result.all()

        # Build menus per meal type
        menus: dict[str, dict] = {}
        for mt_key in ["breakfast", "lunch", "dinner"]:
            menus[mt_key] = {"count": 0, "categories": []}

        for snap_id, mt_id in snapshots:
            mt_name = meal_type_map.get(mt_id, "").lower()
            if mt_name not in menus:
                continue

            # Get items grouped by station/section
            items_result = await db.execute(
                select(
                    Food.id,
                    Food.name,
                    FoodNutrition.calories,
                    FoodNutrition.g_protein,
                    FoodNutrition.g_carbs,
                    FoodNutrition.g_fat,
                    MenuSection.display_name,
                    MenuSectionItem.position,
                )
                .join(MenuSectionItem, MenuSectionItem.food_id == Food.id)
                .join(MenuSection, MenuSectionItem.section_id == MenuSection.id)
                .outerjoin(FoodNutrition, FoodNutrition.food_id == Food.id)
                .where(
                    MenuSection.snapshot_id == snap_id,
                    MenuSectionItem.food_id.isnot(None),
                )
                .order_by(MenuSection.position, MenuSectionItem.position)
            )
            rows = items_result.all()

            # Group by category (section display_name)
            cat_groups: dict[str, list[dict]] = {}
            for r in rows:
                cat_name = r[6] or "Other"
                item = {
                    "name": r[1],
                    "id": r[0],
                    "calories": float(r[2]) if r[2] else None,
                    "protein": float(r[3]) if r[3] else None,
                    "carbs": float(r[4]) if r[4] else None,
                    "fat": float(r[5]) if r[5] else None,
                    "favorited": r[0] in user_favorites,
                }
                cat_groups.setdefault(cat_name, []).append(item)

            categories = [
                {"category": cat, "items": items}
                for cat, items in cat_groups.items()
            ]
            total_count = sum(len(c["items"]) for c in categories)

            menus[mt_name] = {"count": total_count, "categories": categories}

        # Determine hall status for the day
        has_data = any(menus[m]["count"] > 0 for m in menus)
        status = "open" if has_data else "closed"
        hours = "" if not has_data else "Check dining.wisc.edu"

        # AI pick: highest-calorie item across all meals as a simple heuristic
        ai_pick_label = None
        ai_pick_name = None
        for mt_key in ["lunch", "dinner", "breakfast"]:
            for cat in menus[mt_key]["categories"]:
                for item in cat["items"]:
                    if item.get("calories") and (ai_pick_name is None or item["calories"] > 0):
                        if item.get("protein") and item["protein"] > 20:
                            ai_pick_label = "High Protein"
                            ai_pick_name = item["name"]
                            break
                if ai_pick_name:
                    break
            if ai_pick_name:
                break

        day_data = {
            "status": status,
            "hours": hours,
            "aiPickLabel": ai_pick_label,
            "aiPickName": ai_pick_name,
            "menus": menus,
        }

        dining_halls.append({
            "id": meta["slug"],
            "name": hall.name,
            "emoji": meta["emoji"],
            "emojiBg": meta["emojiBg"],
            "mapsUrl": meta["mapsUrl"],
            "days": {target_date.isoformat(): day_data},
        })

    return {"diningHalls": dining_halls}
