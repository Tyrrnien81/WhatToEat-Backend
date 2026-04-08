# GET /menus/summary

> **Status:** ✅ Implemented — `app/routers/homescreen.py` → `app/services/homescreen_service.py`

Retrieve today's highlighted menu items from each dining hall, filtered and ranked by the user's dietary preferences. Used to render the dining hall cards on the home screen.

## Request

### Headers

None required.

### Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `user_id` | string (UUID) | Yes | User ID |
| `date` | string | No | Target date (`YYYY-MM-DD`). Defaults to today. |
| `mealType` | string | No | Filter by meal period: `breakfast`, `lunch`, or `dinner` |

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "date": "2026-03-23",
  "diningHalls": [
    {
      "id": 1,
      "name": "Gordon Avenue Market",
      "recommendedItems": [
        {
          "id": 201,
          "name": "Grilled Salmon",
          "calories": 400,
          "protein": 35,
          "carbs": 5,
          "fat": 20,
          "station": "Grill",
          "icons": ["halal"]
        },
        {
          "id": 202,
          "name": "Quinoa Bowl",
          "calories": 320,
          "protein": 12,
          "carbs": 50,
          "fat": 8,
          "station": "Great Greens",
          "icons": ["vegan", "vegetarian"]
        }
      ]
    }
  ]
}
```

| Field | Type | Description |
| --- | --- | --- |
| `date` | string | Date the summary is for |
| `diningHalls` | array | List of dining halls with their recommended items |
| `diningHalls[].id` | number | Dining hall identifier |
| `diningHalls[].name` | string | Dining hall name |
| `diningHalls[].recommendedItems` | array | Top menu items at this hall matching user preferences |

### Errors

| Status | Description |
| --- | --- |
| `422 Unprocessable Entity` | Missing or invalid `user_id` query parameter |

## Notes

- Items are filtered by the user's allergens and dislikes, then ranked by relevance to their nutrition goals.
- The number of recommended items per dining hall may be limited (e.g. top 3-5 items).
- Dining hall status is derived from `operating_hours` in the `restaurants` table.
- Results may be grouped by meal period depending on the time of day.
- Data is sourced from the daily Nutrislice ingestion pipeline and cached in Redis.
