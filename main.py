from fastapi import FastAPI, Query
from supabase import create_client
from dotenv import load_dotenv
from datetime import date
import os

load_dotenv()

app = FastAPI()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# GET /menu/{restaurant_id}?meal=breakfast&service_date=2026-03-24
# restaurant_id : 1=Gordon Avenue, 4=Carson's, 6=Four Lakes, 12=Rheta's, 45=Liz's, 48=Lowell
# meal          : breakfast / lunch / dinner
# service_date  : 날짜 (생략하면 오늘 날짜 자동 적용)
@app.get("/menu/{restaurant_id}")
def get_menu(
    restaurant_id: int,
    meal: str = Query(...),
    service_date: date = Query(default=None)
):
    if service_date is None:
        service_date = date.today()
    meal = meal.capitalize()  # breakfast → Breakfast

    # meal 이름으로 meal_type_id 조회
    meal_type = supabase.table("meal_types").select("id").eq("name", meal).single().execute()
    if not meal_type.data:
        return {"error": "Invalid meal type"}

    # 날짜 + 식당 + meal로 snapshot 조회 (중복 방지: 첫 번째만 사용)
    snapshot = supabase.table("menu_snapshots").select("id")\
        .eq("restaurant_id", restaurant_id)\
        .eq("meal_type_id", meal_type.data["id"])\
        .eq("service_date", str(service_date))\
        .limit(1).execute()
    if not snapshot.data:
        return {"error": "No menu found"}

    snapshot_id = snapshot.data[0]["id"]

    # 섹션 목록 조회
    sections = supabase.table("menu_sections").select("id, display_name, position")\
        .eq("snapshot_id", snapshot_id).order("position").execute()

    # 섹션별 메뉴 아이템 조회
    result = []
    for section in sections.data:
        items = supabase.table("menu_section_items").select("foods(id, name)")\
            .eq("section_id", section["id"]).execute()
        result.append({
            "section": section["display_name"],
            "items": [{"id": i["foods"]["id"], "name": i["foods"]["name"]} for i in items.data if i["foods"]]
        })

    return {"restaurant_id": restaurant_id, "meal": meal, "date": str(service_date), "sections": result}