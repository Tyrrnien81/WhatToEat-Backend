# GET /menus/summary

Retrieve today's highlighted menu items from each dining hall, filtered and ranked by the user's dietary preferences. Used to render the dining hall cards on the home screen.

## Request

### Headers

```http
Authorization: Bearer <JWT token>
```

### Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `date` | string | No | Target date (`YYYY-MM-DD`). Defaults to today. |

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "date": "2026-03-23",
  "diningHalls": [
    {
      "id": "hall-uuid",
      "name": "Gordon Avenue Market",
      "status": "open",
      "recommendedItems": [
        {
          "id": "food-uuid",
          "name": "Grilled Salmon",
          "calories": 400,
          "protein": 35,
          "carbs": 5,
          "fat": 20,
          "station": "Grill",
          "icons": ["halal"]
        },
        {
          "id": "food-uuid",
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
| `diningHalls[].id` | string | Dining hall identifier |
| `diningHalls[].name` | string | Dining hall name |
| `diningHalls[].status` | string | Current status: `open`, `closing_soon`, or `closed` |
| `diningHalls[].recommendedItems` | array | Top menu items at this hall matching user preferences |

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Invalid or missing JWT token |

## Notes

- Items are filtered by the user's allergens and dislikes, then ranked by relevance to their nutrition goals.
- The number of recommended items per dining hall may be limited (e.g. top 3-5 items).
- Dining hall status is derived from `operating_hours` in the `restaurants` table.
- Results may be grouped by meal period depending on the time of day.
- Data is sourced from the daily Nutrislice ingestion pipeline and cached in Redis.
