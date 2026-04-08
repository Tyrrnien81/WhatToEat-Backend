# GET /goals/daily

> **Status:** ✅ Implemented — `app/routers/homescreen.py` → `app/services/homescreen_service.py`

Retrieve the user's daily nutrition goal progress. Returns target values and consumed amounts for calories and macronutrients, used to render the nutrition status bar on the home screen.

## Request

### Headers

None required.

### Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `user_id` | string (UUID) | Yes | User ID |
| `date` | string | No | Target date (`YYYY-MM-DD`). Defaults to today. |

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "date": "2026-03-23",
  "calories": { "goal": 2000, "consumed": 850 },
  "protein": { "goal": 120, "consumed": 55 },
  "carbs": { "goal": 250, "consumed": 100 },
  "fat": { "goal": 65, "consumed": 30 }
}
```

| Field | Type | Description |
| --- | --- | --- |
| `date` | string | The date this summary is for |
| `calories.goal` | number | User's daily calorie target (from `user_preferences`) |
| `calories.consumed` | number | Total calories consumed so far (from `meal_logs` + `meal_log_items`) |
| `protein.goal` | number | Daily protein target in grams |
| `protein.consumed` | number | Total protein consumed in grams |
| `carbs.goal` | number | Daily carbohydrate target in grams |
| `carbs.consumed` | number | Total carbohydrates consumed in grams |
| `fat.goal` | number | Daily fat target in grams |
| `fat.consumed` | number | Total fat consumed in grams |

### Errors

| Status | Description |
| --- | --- |
| `422 Unprocessable Entity` | Missing or invalid `user_id` query parameter |

## Notes

- Goal values come from the `user_preferences` table (`target_calories`, `target_protein_g`, etc.).
- Consumed values are aggregated from the `meal_logs` and `meal_log_items` tables for the specified date, joined with `food_nutrition` for nutritional data.
- If no meals have been logged for the day, all `consumed` values return `0`.
- This data may be cached in Redis with a short TTL and invalidated when a new meal is logged.
