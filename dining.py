from fastapi import FastAPI, Query
from supabase import create_client
from dotenv import load_dotenv
from datetime import date
import os

load_dotenv()
app = FastAPI()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))


# 1. GET /dining-hall — 전체 다이닝홀 목록
@app.get("/dining-hall")
def get_all_dining_halls():
    res = supabase.table("restaurants").select("id, name").execute()
    return {"dining_halls": res.data}


# 2. GET /dining-hall/{hall_id} — 특정 다이닝홀 상세
@app.get("/dining-hall/{hall_id}")
def get_dining_hall(hall_id: int):
    res = supabase.table("restaurants").select("id, name")\
        .eq("id", hall_id).single().execute()
    if not res.data:
        return {"error": "Not found"}
    return res.data


# 3. GET /dining-hall/{hall_id}/stations — 스테이션 목록
@app.get("/dining-hall/{hall_id}/stations")
def get_stations(
    hall_id: int,
    meal: str = Query(...),
    service_date: date = Query(default=None)
):
    if service_date is None:
        service_date = date.today()

    meal_type = supabase.table("meal_types").select("id")\
        .eq("name", meal.capitalize()).single().execute()
    if not meal_type.data:
        return {"error": "Invalid meal type"}

    snapshot = supabase.table("menu_snapshots").select("id")\
        .eq("restaurant_id", hall_id)\
        .eq("meal_type_id", meal_type.data["id"])\
        .eq("service_date", str(service_date))\
        .limit(1).execute()
    if not snapshot.data:
        return {"error": "No menu found"}

    sections = supabase.table("menu_sections").select("id, display_name, position")\
        .eq("snapshot_id", snapshot.data[0]["id"]).order("position").execute()

    return {"hall_id": hall_id, "stations": sections.data}


# 4. GET /dining-hall/{hall_id}/stations/menu — 스테이션별 메뉴
@app.get("/dining-hall/{hall_id}/stations/menu")
def get_stations_menu(
    hall_id: int,
    meal: str = Query(...),
    service_date: date = Query(default=None)
):
    if service_date is None:
        service_date = date.today()

    meal_type = supabase.table("meal_types").select("id")\
        .eq("name", meal.capitalize()).single().execute()
    if not meal_type.data:
        return {"error": "Invalid meal type"}

    snapshot = supabase.table("menu_snapshots").select("id")\
        .eq("restaurant_id", hall_id)\
        .eq("meal_type_id", meal_type.data["id"])\
        .eq("service_date", str(service_date))\
        .limit(1).execute()
    if not snapshot.data:
        return {"error": "No menu found"}

    sections = supabase.table("menu_sections").select("id, display_name, position")\
        .eq("snapshot_id", snapshot.data[0]["id"]).order("position").execute()

    result = []
    for section in sections.data:
        items = supabase.table("menu_section_items").select("foods(id, name)")\
            .eq("section_id", section["id"]).execute()
        result.append({
            "station": section["display_name"],
            "items": [{"id": i["foods"]["id"], "name": i["foods"]["name"]} for i in items.data if i["foods"]]
        })

    return {"hall_id": hall_id, "meal": meal, "date": str(service_date), "stations": result}