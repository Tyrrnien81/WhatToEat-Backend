# GET /users/me/food-log

Retrieve the authenticated user's food consumption history with pagination and optional date filtering.

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |

### Query Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `date` | string | No | Today | Filter by date (`YYYY-MM-DD`) |
| `page` | number | No | `1` | Page number for pagination |
| `limit` | number | No | `20` | Number of entries per page |

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "entries": [
    {
      "id": "entry-uuid",
      "name": "Grilled Chicken Breast",
      "calories": 350,
      "protein": 30,
      "carbs": 5,
      "fat": 12,
      "source": "scan",
      "loggedAt": "2026-03-18T12:00:00Z"
    },
    {
      "id": "entry-uuid-2",
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
| `entries[].id` | string | Entry unique identifier |
| `entries[].name` | string | Food name |
| `entries[].calories` | number | Calorie count |
| `entries[].protein` | number | Protein in grams |
| `entries[].carbs` | number | Carbohydrates in grams |
| `entries[].fat` | number | Total fat in grams |
| `entries[].source` | string | How the entry was logged: `scan`, `manual`, or `menu` |
| `entries[].loggedAt` | string | ISO 8601 timestamp when the entry was logged |
| `total` | number | Total number of entries matching the query |
| `page` | number | Current page number |
| `limit` | number | Entries per page |

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Missing or invalid JWT token |
