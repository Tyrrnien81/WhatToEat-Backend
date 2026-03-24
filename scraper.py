import os
import requests
from datetime import date
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

DINING_HALL = "gordon-avenue-market"
MEALS = ["breakfast", "lunch", "dinner"]
BASE_URL = "https://wisc-housingdining.api.nutrislice.com/menu/api/weeks/school"

def fetch_menu(meal, target_date):
    formatted = target_date.strftime("%Y/%m/%d")
    api_url = f"{BASE_URL}/{DINING_HALL}/menu-type/{meal}/{formatted}/"
    response = requests.get(api_url)
    return response.json()

def save_to_db(data, meal, target_date):
    today_str = str(target_date)
    
    for day in data.get("days", []):
        if day.get("date") != today_str:
            continue
        
        for menu_item in day.get("menu_items", []):
            if menu_item.get("blank_line"):
                continue
            
            food = menu_item.get("food")
            if not food:
                continue

            # foods 테이블 저장
            supabase.table("foods").upsert({
                "id": food["id"],
                "name": food["name"]
            }).execute()

            # food_nutrition 저장
            nutrition = food.get("rounded_nutrition_info", {})
            if nutrition:
                supabase.table("food_nutrition").upsert({
                    "food_id": food["id"],
                    **{k: v for k, v in nutrition.items() if v is not None}
                }).execute()

            # food_flags 저장
            for flag in food.get("icons", {}).get("food_icons", []):
                supabase.table("food_flags").upsert({
                    "food_id": food["id"],
                    "type": flag.get("slug"),
                }).execute()

            # menu_items 저장
            supabase.table("menu_items").insert({
                "date": today_str,
                "meal": meal,
                "dining_hall": DINING_HALL,
                "food_id": food["id"]
            }).execute()

def main():
    today = date.today()
    for meal in MEALS:
        print(f"Fetching {meal}...")
        data = fetch_menu(meal, today)
        save_to_db(data, meal, today)
        print(f"{meal} done!")

if __name__ == "__main__":
    main()