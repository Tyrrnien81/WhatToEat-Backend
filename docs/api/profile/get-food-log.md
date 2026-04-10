# GET /users/me/food-log

Retrieve the authenticated user's food consumption history with pagination and optional date filtering.

> **Status:** ✅ Implemented — `app/routers/profile.py` → `app/services/profile_service.py`

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |

### Query Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `date` | string | No | — | Filter by date (`YYYY-MM-DD`). If omitted, returns all dates. |
| `page` | number | No | `1` | Page number for pagination |
| `limit` | number | No | `20` | Number of entries per page (max 100) |

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "entries": [
    {
      "id": 42,
      "name": "Grilled Chicken Breast",
      "calories": 350,
      "protein": 30,
      "carbs": 5,
      "fat": 12,
      "source": "scan",
      "loggedAt": "2026-03-18T12:00:00Z"
    },
    {
      "id": 43,
      "name": "Banana",
      "calories": 105,
      "protein": 1,
      "carbs": 27,
      "fat": 0,
      "source": "manual",
      "loggedAt": "2026-03-18T15:30:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "limit": 20
}
```

| Field | Type | Description |
| --- | --- | --- |
| `entries` | array | List of food log entries |
| `entries[].id` | number | Entry unique identifier (meal_log_items PK) |
| `entries[].name` | string | Food name |
| `entries[].calories` | number \| null | Calorie count |
| `entries[].protein` | number \| null | Protein in grams |
| `entries[].carbs` | number \| null | Carbohydrates in grams |
| `entries[].fat` | number \| null | Total fat in grams |
| `entries[].source` | string | How the entry was logged: `scan`, `manual`, or `menu` |
| `entries[].loggedAt` | string \| null | ISO 8601 timestamp when the entry was logged |
| `total` | number | Total number of entries matching the query |
| `page` | number | Current page number |
| `limit` | number | Entries per page |

### Errors

| Status | Description |
| --- | --- |
| `400 Bad Request` | Invalid date format |
| `401 Unauthorized` | Missing or invalid JWT token |

## Notes

- Returns flat `meal_log_items` entries ordered by `logged_at` descending (most recent first).
- Entries originate from manual input, scan results, or dining hall menu selections.
