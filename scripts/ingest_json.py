"""
Fast bulk ingest of Nutrislice JSON exports into Supabase.

Uses asyncpg executemany (pipelined) for batch operations instead of
individual INSERT-per-row, reducing thousands of network round-trips
to a handful of batched calls.

Maps JSON data to 9 tables:
  restaurants, meal_types, foods, food_nutrition, food_icons,
  food_icon_assignments, menu_snapshots, menu_sections, menu_section_items
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, date as date_type
from decimal import Decimal

import asyncpg
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def get_dsn():
    url = os.environ["DATABASE_URL"]
    if "+asyncpg" in url:
        url = url.replace("+asyncpg", "")
    return url


def dec(val):
    if val is None:
        return None
    return Decimal(str(val))


# ── Phase 1: Parse & collect ──────────────────────────────────────────


def collect_all(data_dir: Path, target=None):
    """
    Read JSON files and collect all unique entities in memory.

    target: None  -> all date folders
            Path  -> single file or folder
    """
    json_files = []
    if target is None:
        for folder in sorted(data_dir.iterdir()):
            if folder.is_dir() and folder.name[:4].isdigit():
                json_files.extend(sorted(folder.glob("*.json")))
    elif target.is_dir():
        json_files = sorted(target.glob("*.json"))
    else:
        json_files = [target]

    if not json_files:
        print("No JSON files found.")
        sys.exit(1)

    restaurants = {}       # ext_id -> name
    meal_types = {}        # ext_id -> name
    foods = {}             # ext_food_id -> dict
    nutrition = {}         # ext_food_id -> dict
    icons = {}             # ext_icon_id -> dict
    icon_assigns = set()   # (ext_food_id, ext_icon_id)
    snapshots = {}         # (rest_ext, mt_ext, date) -> exported_at
    sections = {}          # (rest_ext, mt_ext, date, ext_menu_id) -> (display_name, position)
    items = []             # list of item dicts

    for jf in json_files:
        with open(jf) as f:
            data = json.load(f)

        rest = data["restaurant"]
        restaurants[rest["id"]] = rest["name"]

        mt = data["meal_type"]
        meal_types[mt["id"]] = mt["name"]

        sdate = date_type.fromisoformat(data["date"])
        exported = (
            datetime.fromisoformat(data["exported_at"])
            if data.get("exported_at") else None
        )
        snap_key = (rest["id"], mt["id"], sdate)
        snapshots[snap_key] = exported

        for ext_mid_str, info in data["menu"]["menu_info"].items():
            ext_mid = int(ext_mid_str)
            sections[(rest["id"], mt["id"], sdate, ext_mid)] = (
                info["section_options"]["display_name"],
                info["position"],
            )

        current_station = None
        for item in data["menu"]["menu_items"]:
            if item.get("is_station_header"):
                current_station = item.get("text")
                continue

            fd = item.get("food")
            if not fd:
                continue

            ext_fid = fd["id"]
            if ext_fid not in foods:
                srv = fd.get("serving_size_info") or {}
                foods[ext_fid] = (
                    ext_fid,
                    fd["name"],
                    fd.get("description") or None,
                    fd.get("food_category"),
                    dec(fd.get("price")),
                    fd.get("ingredients"),
                    str(srv["serving_size_amount"]) if srv.get("serving_size_amount") is not None else None,
                    str(srv["serving_size_unit"]) if srv.get("serving_size_unit") is not None else None,
                )
                nutr = fd.get("rounded_nutrition_info")
                if nutr:
                    nutrition[ext_fid] = nutr

                for ic in fd.get("icons", {}).get("food_icons", []):
                    eid = ic["id"]
                    if eid not in icons:
                        icons[eid] = (
                            eid, ic["name"], ic["slug"],
                            ic.get("type", 1), ic.get("behavior", 1),
                            ic.get("is_filter", False), ic.get("is_highlight", False),
                            ic.get("sort_order", 0),
                        )
                    icon_assigns.add((ext_fid, eid))

            raw_id = item.get("id")
            raw_fv = item.get("food_variation_id")
            items.append((
                snap_key,
                item.get("menu_id"),
                ext_fid,
                raw_id if isinstance(raw_id, int) else None,
                raw_fv if isinstance(raw_fv, int) else None,
                item.get("position", 0),
                current_station,
                item.get("category"),
                dec(item.get("price")),
                str(item["serving_size_amount"]) if item.get("serving_size_amount") is not None else None,
                str(item["serving_size_unit"]) if item.get("serving_size_unit") is not None else None,
            ))

    print(f"Parsed {len(json_files)} files -> "
          f"{len(restaurants)} restaurants, {len(meal_types)} meal types, "
          f"{len(foods)} foods, {len(icons)} icons, "
          f"{len(snapshots)} snapshots, {len(items)} items")

    return restaurants, meal_types, foods, nutrition, icons, icon_assigns, snapshots, sections, items


# ── Phase 2: Bulk ingest ──────────────────────────────────────────────


async def bulk_ingest(restaurants, meal_types, foods, nutrition,
                      icons, icon_assigns, snapshots, sections, items):
    dsn = get_dsn()
    conn = await asyncpg.connect(dsn)
    print("Connected to database.")
    t0 = time.perf_counter()

    try:
        async with conn.transaction():
            # 1. Restaurants
            await conn.executemany(
                """INSERT INTO restaurants (external_restaurant_id, name)
                   VALUES ($1, $2)
                   ON CONFLICT (external_restaurant_id) DO UPDATE SET name = EXCLUDED.name""",
                [(eid, name) for eid, name in restaurants.items()],
            )
            rows = await conn.fetch("SELECT id, external_restaurant_id FROM restaurants")
            rid = {r["external_restaurant_id"]: r["id"] for r in rows}
            print(f"  restaurants: {len(rid)}")

            # 2. Meal types
            await conn.executemany(
                """INSERT INTO meal_types (external_meal_type_id, name)
                   VALUES ($1, $2)
                   ON CONFLICT (external_meal_type_id) DO UPDATE SET name = EXCLUDED.name""",
                [(eid, name) for eid, name in meal_types.items()],
            )
            rows = await conn.fetch("SELECT id, external_meal_type_id FROM meal_types")
            mtid = {r["external_meal_type_id"]: r["id"] for r in rows}
            print(f"  meal_types: {len(mtid)}")

            # 3. Foods
            await conn.executemany(
                """INSERT INTO foods (external_food_id, name, description, food_category,
                       price, ingredients, serving_size_amount, serving_size_unit)
                   VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
                   ON CONFLICT (external_food_id) DO UPDATE SET name = EXCLUDED.name""",
                list(foods.values()),
            )
            rows = await conn.fetch("SELECT id, external_food_id FROM foods")
            fid = {r["external_food_id"]: r["id"] for r in rows}
            print(f"  foods: {len(fid)}")

            # 4. Food nutrition
            nutr_rows = []
            for ext_fid, n in nutrition.items():
                nutr_rows.append((
                    fid[ext_fid],
                    dec(n.get("calories")), dec(n.get("g_fat")),
                    dec(n.get("g_saturated_fat")), dec(n.get("g_trans_fat")),
                    dec(n.get("mg_cholesterol")), dec(n.get("g_carbs")),
                    dec(n.get("g_added_sugar")), dec(n.get("g_sugar")),
                    dec(n.get("mg_potassium")), dec(n.get("mg_sodium")),
                    dec(n.get("g_fiber")), dec(n.get("g_protein")),
                    dec(n.get("mg_iron")), dec(n.get("mg_calcium")),
                    dec(n.get("mg_vitamin_c")),
                    dec(n.get("iu_vitamin_a")), dec(n.get("re_vitamin_a")),
                    dec(n.get("mcg_vitamin_a")),
                    dec(n.get("mg_vitamin_d")), dec(n.get("mcg_vitamin_d")),
                ))
            await conn.executemany(
                """INSERT INTO food_nutrition (
                       food_id, calories, g_fat, g_saturated_fat, g_trans_fat,
                       mg_cholesterol, g_carbs, g_added_sugar, g_sugar,
                       mg_potassium, mg_sodium, g_fiber, g_protein,
                       mg_iron, mg_calcium, mg_vitamin_c,
                       iu_vitamin_a, re_vitamin_a, mcg_vitamin_a,
                       mg_vitamin_d, mcg_vitamin_d)
                   VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21)
                   ON CONFLICT (food_id) DO NOTHING""",
                nutr_rows,
            )
            print(f"  food_nutrition: {len(nutr_rows)}")

            # 5. Food icons
            await conn.executemany(
                """INSERT INTO food_icons (external_icon_id, name, slug, icon_type,
                       behavior, is_filter, is_highlight, sort_order)
                   VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
                   ON CONFLICT (external_icon_id) DO UPDATE SET name = EXCLUDED.name""",
                list(icons.values()),
            )
            rows = await conn.fetch("SELECT id, external_icon_id FROM food_icons")
            icid = {r["external_icon_id"]: r["id"] for r in rows}
            print(f"  food_icons: {len(icid)}")

            # 6. Icon assignments
            assign_rows = [(fid[ef], icid[ei]) for ef, ei in icon_assigns]
            await conn.executemany(
                """INSERT INTO food_icon_assignments (food_id, icon_id)
                   VALUES ($1, $2) ON CONFLICT DO NOTHING""",
                assign_rows,
            )
            print(f"  icon_assignments: {len(assign_rows)}")

            # 7. Menu snapshots
            snap_rows = [
                (rid[re], mtid[me], sd, exp)
                for (re, me, sd), exp in snapshots.items()
            ]
            await conn.executemany(
                """INSERT INTO menu_snapshots (restaurant_id, meal_type_id, service_date, exported_at)
                   VALUES ($1,$2,$3,$4)
                   ON CONFLICT (restaurant_id, meal_type_id, service_date)
                   DO UPDATE SET exported_at = EXCLUDED.exported_at""",
                snap_rows,
            )
            rows = await conn.fetch(
                "SELECT id, restaurant_id, meal_type_id, service_date FROM menu_snapshots"
            )
            rev_r = {v: k for k, v in rid.items()}
            rev_m = {v: k for k, v in mtid.items()}
            sid = {}
            for r in rows:
                re = rev_r.get(r["restaurant_id"])
                me = rev_m.get(r["meal_type_id"])
                if re is not None and me is not None:
                    sid[(re, me, r["service_date"])] = r["id"]
            print(f"  menu_snapshots: {len(sid)}")

            # 8. Menu sections
            sec_rows = []
            for (re, me, sd, ext_mid), (dname, pos) in sections.items():
                snap_id = sid.get((re, me, sd))
                if snap_id is not None:
                    sec_rows.append((snap_id, ext_mid, dname, pos))
            await conn.executemany(
                """INSERT INTO menu_sections (snapshot_id, external_menu_id, display_name, position)
                   VALUES ($1,$2,$3,$4) ON CONFLICT DO NOTHING""",
                sec_rows,
            )
            rows = await conn.fetch(
                "SELECT id, snapshot_id, external_menu_id FROM menu_sections"
            )
            secid = {(r["snapshot_id"], r["external_menu_id"]): r["id"] for r in rows}
            print(f"  menu_sections: {len(secid)}")

            # 9. Menu section items
            item_rows = []
            for (snap_key, ext_mid, ext_fid, ext_item_id, fv_id,
                 pos, station, cat, price, sa, su) in items:
                snap_id = sid.get(snap_key)
                if snap_id is None:
                    continue
                sec = secid.get((snap_id, ext_mid))
                if sec is None:
                    continue
                item_rows.append((
                    sec, fid.get(ext_fid), ext_item_id,
                    fv_id, pos, station, cat, price, sa, su,
                ))
            await conn.executemany(
                """INSERT INTO menu_section_items (
                       section_id, food_id, external_menu_item_id,
                       food_variation_id, position, station_name,
                       category, price, serving_size_amount, serving_size_unit)
                   VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)""",
                item_rows,
            )
            print(f"  menu_section_items: {len(item_rows)}")

        elapsed = time.perf_counter() - t0
        print(f"\nAll data committed in {elapsed:.1f}s")
    finally:
        await conn.close()


# ── CLI ───────────────────────────────────────────────────────────────


if __name__ == "__main__":
    data_dir = Path(__file__).resolve().parent.parent / "data"

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/ingest_json.py all                 # all date folders")
        print("  python scripts/ingest_json.py <date-folder>       # one date folder")
        print("  python scripts/ingest_json.py <file.json>         # single file")
        sys.exit(1)

    arg = sys.argv[1]
    if arg == "all":
        target = None
    else:
        target = Path(arg)

    entities = collect_all(data_dir, target)
    asyncio.run(bulk_ingest(*entities))
