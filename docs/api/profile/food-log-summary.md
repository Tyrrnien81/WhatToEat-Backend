# GET /users/me/food-log/summary

Retrieve an aggregated nutrition summary, streak data, and weight history for the user's profile dashboard.

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |

### Query Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `range` | string | No | `week` | Time range: `week`, `month`, or `all` |

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "range": "week",
  "averageDailyCalories": 1850,
  "averageDailyProtein": 95,
  "averageDailyCarbs": 220,
  "averageDailyFat": 65,
  "totalMealsLogged": 18,
  "currentStreak": 5,
  "longestStreak": 12,
  "weightHistory": [
    { "date": "2026-03-12", "weight": 71 },
    { "date": "2026-03-14", "weight": 70.5 },
    { "date": "2026-03-18", "weight": 70 }
  ]
}
```

| Field | Type | Description |
| --- | --- | --- |
| `range` | string | Time range for this summary |
| `averageDailyCalories` | number | Average daily calorie intake |
| `averageDailyProtein` | number | Average daily protein in grams |
| `averageDailyCarbs` | number | Average daily carbohydrates in grams |
| `averageDailyFat` | number | Average daily fat in grams |
| `totalMealsLogged` | number | Total meals logged in the period |
| `currentStreak` | number | Current consecutive days with at least one log entry |
| `longestStreak` | number | Longest-ever consecutive logging streak |
| `weightHistory` | array | Weight data points for charting |
| `weightHistory[].date` | string | Date of the weight entry |
| `weightHistory[].weight` | number | Weight in kilograms |

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Missing or invalid JWT token |

## Notes

- The `currentStreak` counts consecutive days (up to today) where the user logged at least one food item.
- Weight history is derived from periodic weight updates via `PATCH /users/me`.
