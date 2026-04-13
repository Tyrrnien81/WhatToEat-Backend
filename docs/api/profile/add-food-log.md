# POST /users/me/food-log

Manually add a food entry to the user's food log. Used for items not logged via scan or dining hall menu selection.

> **Status:** ✅ Implemented — `app/routers/profile.py` → `app/services/profile_service.py`

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |
| `Content-Type` | `application/json` | Yes |

### Body

```json
{
  "name": "Banana",
  "calories": 105,
  "protein": 1,
  "carbs": 27,
  "fat": 0,
  "date": "2026-03-18"
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | Yes | Food name |
| `calories` | number | Yes | Calorie count |
| `protein` | number | Yes | Protein in grams |
| `carbs` | number | Yes | Carbohydrates in grams |
| `fat` | number | Yes | Total fat in grams |
| `date` | string | No | Date for the entry (`YYYY-MM-DD`). Defaults to today. |

## Response

### Success (`201 Created`)

```json
{
  "id": "42",
  "message": "Food log entry added successfully"
}
```

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | The new entry's unique identifier (stringified integer) |
| `message` | string | Confirmation message |

### Errors

| Status | Description |
| --- | --- |
| `400 Bad Request` | Missing required fields or invalid date format |
| `401 Unauthorized` | Missing or invalid JWT token |

## Notes

- If a `meal_log` already exists for the given date, the new entry is added to it. Otherwise a new meal log is created with `meal_type` set to `"Manual"`.
- The entry `source` is always set to `"manual"`.
