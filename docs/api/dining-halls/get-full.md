# GET /dining-halls/full

Retrieve a frontend-oriented nested dining hall payload for a specific date.

## Request

### Headers

Optional. Send `Authorization: Bearer <JWT>` to set `favorited` on items using that user’s saved favorites (`sub`). Without auth, `favorited` is always `false`.

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
  "diningHalls": [
    {
      "id": "gordon",
      "name": "Gordon Avenue Market",
      "emoji": "🏛️",
      "emojiBg": "#FFE8D6",
      "mapsUrl": "https://maps.app.goo.gl/gordonavenue",
      "days": {
        "2026-04-07": {
          "status": "open",
          "hours": "Check dining.wisc.edu",
          "aiPickLabel": "High Protein",
          "aiPickName": "Grilled Chicken Breast",
          "menus": {
            "breakfast": { "count": 0, "categories": [] },
            "lunch": {
              "count": 2,
              "categories": [
                {
                  "category": "Grill",
                  "items": [
                    {
                      "name": "Grilled Chicken Breast",
                      "id": 123,
                      "calories": 350,
                      "protein": 30,
                      "carbs": 5,
                      "fat": 15,
                      "favorited": false
                    }
                  ]
                }
              ]
            },
            "dinner": { "count": 0, "categories": [] }
          }
        }
      }
    }
  ]
}
```

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Invalid or expired JWT (only if `Authorization` was sent) |

## Notes

- The response is shaped for current frontend hall-card rendering (hall metadata + date-keyed day data).
- `favorited` uses `favorites.food_id` for the authenticated user when a JWT is sent. Local dev only: `ALLOW_QUERY_USER_ID=true` allows `?user_id=` when the header is omitted.
- When no data exists for the date, halls return `status: "closed"` and empty menu categories.
