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


def fetch_menu(slug, meal, target_date):
    formatted = target_date.strftime("%Y/%m/%d")
    api_url = f"{BASE_URL}/{slug}/menu-type/{meal}/{formatted}/"
    response = requests.get(api_url, timeout=15)
    response.raise_for_status()
    return response.json()


def main():
    target = date.today()
    if len(sys.argv) > 1:
        target = date.fromisoformat(sys.argv[1])

    out_dir = os.path.join("data", target.strftime("%Y-%m-%d"))
    os.makedirs(out_dir, exist_ok=True)

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
                data = fetch_menu(slug, meal, target)
                filename = f"{slug}_{meal}.json"
                filepath = os.path.join(out_dir, filename)
                with open(filepath, "w") as f:
                    json.dump(data, f, indent=2)
                print(f"-> {filepath}")
            except Exception as e:
                print(f"SKIP ({e})")
            time.sleep(1)

    print(f"\nDone. Files saved to {out_dir}/")


if __name__ == "__main__":
    main()