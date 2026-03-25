# POST /users/me/food-log

Manually add a food entry to the user's food log. Used for items not logged via scan or dining hall menu selection.

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
  "id": "entry-uuid",
  "message": "Food log entry added successfully"
}
```

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Unique identifier for the new entry |
| `message` | string | Confirmation message |

### Errors

| Status | Description |
| --- | --- |
| `400 Bad Request` | Missing or invalid fields |
| `401 Unauthorized` | Missing or invalid JWT token |
