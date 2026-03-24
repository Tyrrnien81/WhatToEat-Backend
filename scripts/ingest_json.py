"""
Ingest Gordon_Avenue_Market_03-15-2026.json into the Supabase database.

Maps the Nutrislice JSON export to 9 tables:
  restaurants, meal_types, foods, food_nutrition, food_icons,
  food_icon_assignments, menu_snapshots, menu_sections, menu_section_items
"""

import asyncio
import json
import os
import sys
from pathlib import Path

import asyncpg
from decimal import Decimal
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def get_db_params():
    """Parse DATABASE_URL into asyncpg connection params."""
    url = os.environ["DATABASE_URL"]
    # Strip SQLAlchemy driver prefix
    if "+asyncpg" in url:
        url = url.replace("+asyncpg", "")
    return url


def dec(val):
    """Convert a JSON number to Decimal for NUMERIC columns, or None."""
    if val is None:
        return None
    return Decimal(str(val))


async def ingest(json_path: str):
    dsn = get_db_params()
    conn = await asyncpg.connect(dsn)
    print("Connected to database.")

    with open(json_path) as f:
        data = json.load(f)

    try:
        async with conn.transaction():
            # ── 1. Restaurant ──
            rest = data["restaurant"]
            row = await conn.fetchrow(
                """
                INSERT INTO restaurants (external_restaurant_id, name)
                VALUES ($1, $2)
                ON CONFLICT (external_restaurant_id) DO UPDATE SET name = EXCLUDED.name
                RETURNING id
                """,
                rest["id"],
                rest["name"],
            )
            restaurant_id = row["id"]
            print(f"  restaurant: {rest['name']} -> id={restaurant_id}")

            # ── 2. Meal type ──
            mt = data["meal_type"]
            row = await conn.fetchrow(
                """
                INSERT INTO meal_types (external_meal_type_id, name)
                VALUES ($1, $2)
                ON CONFLICT (external_meal_type_id) DO UPDATE SET name = EXCLUDED.name
                RETURNING id
                """,
                mt["id"],
                mt["name"],
            )
            meal_type_id = row["id"]
            print(f"  meal_type: {mt['name']} -> id={meal_type_id}")

            # ── 3. Menu snapshot ──
            from datetime import datetime, date as date_type

            service_date = date_type.fromisoformat(data["date"])
            exported_at = (
                datetime.fromisoformat(data["exported_at"])
                if data.get("exported_at")
                else None
            )
            row = await conn.fetchrow(
                """
                INSERT INTO menu_snapshots (restaurant_id, meal_type_id, service_date, exported_at)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (restaurant_id, meal_type_id, service_date)
                DO UPDATE SET exported_at = EXCLUDED.exported_at
                RETURNING id
                """,
                restaurant_id,
                meal_type_id,
                service_date,
                exported_at,
            )
            snapshot_id = row["id"]
            print(f"  menu_snapshot: {service_date} -> id={snapshot_id}")

            # ── 4. Menu sections (from menu_info) ──
            menu_info = data["menu"]["menu_info"]
            # Map external_menu_id -> internal section id
            section_map = {}
            for ext_menu_id_str, info in menu_info.items():
                ext_menu_id = int(ext_menu_id_str)
                display_name = info["section_options"]["display_name"]
                position = info["position"]
                row = await conn.fetchrow(
                    """
                    INSERT INTO menu_sections (snapshot_id, external_menu_id, display_name, position)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT DO NOTHING
                    RETURNING id
                    """,
                    snapshot_id,
                    ext_menu_id,
                    display_name,
                    position,
                )
                if row:
                    section_map[ext_menu_id] = row["id"]
                else:
                    # Already exists — fetch it
                    row = await conn.fetchrow(
                        "SELECT id FROM menu_sections WHERE snapshot_id = $1 AND external_menu_id = $2",
                        snapshot_id,
                        ext_menu_id,
                    )
                    section_map[ext_menu_id] = row["id"]
            print(f"  menu_sections: {len(section_map)} sections")

            # ── 5. Foods, nutrition, icons ──
            menu_items = data["menu"]["menu_items"]
            foods_inserted = 0
            icons_inserted = 0
            icon_assignments_inserted = 0
            items_inserted = 0

            # Collect unique foods and icons first
            food_map = {}  # external_food_id -> internal food id
            icon_map = {}  # external_icon_id -> internal icon id

            # Track current station name from header items
            current_station = None

            for item in menu_items:
                if item.get("is_station_header"):
                    current_station = item.get("text")
                    continue

                food_data = item.get("food")
                if not food_data:
                    continue

                ext_food_id = food_data["id"]

                # Insert food if not yet seen
                if ext_food_id not in food_map:
                    serving = food_data.get("serving_size_info") or {}
                    row = await conn.fetchrow(
                        """
                        INSERT INTO foods (
                            external_food_id, name, description, food_category,
                            price, ingredients,
                            serving_size_amount, serving_size_unit
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        ON CONFLICT (external_food_id) DO UPDATE SET name = EXCLUDED.name
                        RETURNING id
                        """,
                        ext_food_id,
                        food_data["name"],
                        food_data.get("description") or None,
                        food_data.get("food_category"),
                        dec(food_data.get("price")),
                        food_data.get("ingredients"),
                        str(serving["serving_size_amount"]) if serving.get("serving_size_amount") is not None else None,
                        str(serving["serving_size_unit"]) if serving.get("serving_size_unit") is not None else None,
                    )
                    food_id = row["id"]
                    food_map[ext_food_id] = food_id
                    foods_inserted += 1

                    # ── 5a. Nutrition ──
                    nutr = food_data.get("rounded_nutrition_info")
                    if nutr:
                        await conn.execute(
                            """
                            INSERT INTO food_nutrition (
                                food_id, calories, g_fat, g_saturated_fat, g_trans_fat,
                                mg_cholesterol, g_carbs, g_added_sugar, g_sugar,
                                mg_potassium, mg_sodium, g_fiber, g_protein,
                                mg_iron, mg_calcium, mg_vitamin_c,
                                iu_vitamin_a, re_vitamin_a, mcg_vitamin_a,
                                mg_vitamin_d, mcg_vitamin_d
                            ) VALUES (
                                $1, $2, $3, $4, $5,
                                $6, $7, $8, $9,
                                $10, $11, $12, $13,
                                $14, $15, $16,
                                $17, $18, $19,
                                $20, $21
                            )
                            ON CONFLICT (food_id) DO NOTHING
                            """,
                            food_id,
                            dec(nutr.get("calories")),
                            dec(nutr.get("g_fat")),
                            dec(nutr.get("g_saturated_fat")),
                            dec(nutr.get("g_trans_fat")),
                            dec(nutr.get("mg_cholesterol")),
                            dec(nutr.get("g_carbs")),
                            dec(nutr.get("g_added_sugar")),
                            dec(nutr.get("g_sugar")),
                            dec(nutr.get("mg_potassium")),
                            dec(nutr.get("mg_sodium")),
                            dec(nutr.get("g_fiber")),
                            dec(nutr.get("g_protein")),
                            dec(nutr.get("mg_iron")),
                            dec(nutr.get("mg_calcium")),
                            dec(nutr.get("mg_vitamin_c")),
                            dec(nutr.get("iu_vitamin_a")),
                            dec(nutr.get("re_vitamin_a")),
                            dec(nutr.get("mcg_vitamin_a")),
                            dec(nutr.get("mg_vitamin_d")),
                            dec(nutr.get("mcg_vitamin_d")),
                        )

                    # ── 5b. Icons ──
                    food_icons = (
                        food_data.get("icons", {}).get("food_icons", [])
                    )
                    for icon in food_icons:
                        ext_icon_id = icon["id"]
                        if ext_icon_id not in icon_map:
                            row = await conn.fetchrow(
                                """
                                INSERT INTO food_icons (
                                    external_icon_id, name, slug, icon_type,
                                    behavior, is_filter, is_highlight, sort_order
                                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                                ON CONFLICT (external_icon_id) DO UPDATE SET name = EXCLUDED.name
                                RETURNING id
                                """,
                                ext_icon_id,
                                icon["name"],
                                icon["slug"],
                                icon.get("type", 1),
                                icon.get("behavior", 1),
                                icon.get("is_filter", False),
                                icon.get("is_highlight", False),
                                icon.get("sort_order", 0),
                            )
                            icon_map[ext_icon_id] = row["id"]
                            icons_inserted += 1

                        # ── 5c. Food-icon assignment ──
                        await conn.execute(
                            """
                            INSERT INTO food_icon_assignments (food_id, icon_id)
                            VALUES ($1, $2)
                            ON CONFLICT DO NOTHING
                            """,
                            food_id,
                            icon_map[ext_icon_id],
                        )
                        icon_assignments_inserted += 1

                # ── 6. Menu section item ──
                section_id = section_map.get(item.get("menu_id"))
                if section_id is None:
                    continue

                food_id = food_map.get(ext_food_id)

                # external_menu_item_id can be int or comma-separated string (smart recipes)
                raw_item_id = item.get("id")
                ext_menu_item_id = raw_item_id if isinstance(raw_item_id, int) else None

                raw_fv_id = item.get("food_variation_id")
                fv_id = raw_fv_id if isinstance(raw_fv_id, int) else None

                await conn.execute(
                    """
                    INSERT INTO menu_section_items (
                        section_id, food_id, external_menu_item_id,
                        food_variation_id, position, station_name,
                        category, price, serving_size_amount, serving_size_unit
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    """,
                    section_id,
                    food_id,
                    ext_menu_item_id,
                    fv_id,
                    item.get("position", 0),
                    current_station,
                    item.get("category"),
                    dec(item.get("price")),
                    str(item["serving_size_amount"]) if item.get("serving_size_amount") is not None else None,
                    str(item["serving_size_unit"]) if item.get("serving_size_unit") is not None else None,
                )
                items_inserted += 1

            print(f"  foods: {foods_inserted}")
            print(f"  icons: {icons_inserted}")
            print(f"  icon_assignments: {icon_assignments_inserted}")
            print(f"  menu_section_items: {items_inserted}")

        print("\nDone — all data committed.")

    finally:
        await conn.close()


if __name__ == "__main__":
    json_file = sys.argv[1] if len(sys.argv) > 1 else "data/Gordon_Avenue_Market_03-15-2026.json"
    asyncio.run(ingest(json_file))
