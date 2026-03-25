import json
import os
import sys
import time
import requests
from datetime import date

RESTAURANTS = [
    "carsons-market",
    "four-lakes-market",
    "gordon-avenue-market",
    "lizs-market",
    "lowell-market",
    "rhetas-market",
]
MEALS = ["breakfast", "lunch", "dinner"]
SKIP_MEALS = {
    "carsons-market": {"breakfast"},
}
BASE_URL = "https://wisc-housingdining.api.nutrislice.com/menu/api/weeks/school"

# Nutrislice external IDs (from /menu/api/schools/ and weekly endpoints)
RESTAURANT_META = {
    "carsons-market":       {"id": 45370, "name": "Carson's Market"},
    "four-lakes-market":    {"id": 45371, "name": "Four Lakes Market"},
    "gordon-avenue-market": {"id": 45372, "name": "Gordon Avenue Market"},
    "lizs-market":          {"id": 45373, "name": "Liz's Market"},
    "lowell-market":        {"id": 45374, "name": "Lowell Market"},
    "rhetas-market":        {"id": 45375, "name": "Rheta's Market"},
}
MEAL_TYPE_META = {
    "breakfast": {"id": 14942, "name": "Breakfast"},
    "lunch":     {"id": 14943, "name": "Lunch"},
    "dinner":    {"id": 14944, "name": "Dinner"},
}


def fetch_menu(slug, meal, target_date):
    formatted = target_date.strftime("%Y/%m/%d")
    api_url = f"{BASE_URL}/{slug}/menu-type/{meal}/{formatted}/"
    response = requests.get(api_url, timeout=15)
    response.raise_for_status()
    return response.json()


def split_and_save(raw, slug, meal):
    """Split a weekly API response into per-date files under data/{date}/."""
    days = raw.get("days", [])
    exported_at = raw.get("last_updated")
    saved = 0

    for day in days:
        day_date = day.get("date")
        if not day_date or not day.get("menu_items"):
            continue

        # Build the flat structure that ingest_json.py expects
        flat = {
            "restaurant": RESTAURANT_META[slug],
            "meal_type": MEAL_TYPE_META[meal],
            "date": day_date,
            "exported_at": exported_at,
            "menu": {
                "menu_info": day.get("menu_info", {}),
                "menu_items": day.get("menu_items", []),
            },
        }

        out_dir = os.path.join("data", day_date)
        os.makedirs(out_dir, exist_ok=True)

        filepath = os.path.join(out_dir, f"{slug}_{meal}.json")
        with open(filepath, "w") as f:
            json.dump(flat, f, indent=2)
        saved += 1

    return saved


def main():
    target = date.today()
    if len(sys.argv) > 1:
        target = date.fromisoformat(sys.argv[1])

    pairs = [
        (slug, meal)
        for slug in RESTAURANTS
        for meal in MEALS
        if meal not in SKIP_MEALS.get(slug, set())
    ]
    total = len(pairs)
    done = 0

    for slug, meal in pairs:
        done += 1
        print(f"[{done}/{total}] {slug} / {meal}...", end=" ", flush=True)
        try:
            raw = fetch_menu(slug, meal, target)
            saved = split_and_save(raw, slug, meal)
            print(f"-> {saved} days saved")
        except Exception as e:
            print(f"SKIP ({e})")
        time.sleep(1)

    print("\nDone.")


if __name__ == "__main__":
    main()