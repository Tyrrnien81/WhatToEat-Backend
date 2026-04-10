# GET /users/me/food-log/summary

Retrieve an aggregated nutrition summary and streak data for the user's profile dashboard.

> **Status:** ✅ Implemented — `app/routers/profile.py` → `app/services/profile_service.py`

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |

### Query Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `range` | string | No | `week` | Time range: `week` (7 days), `month` (30 days), or `all` |

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
  "weightHistory": []
}
```

| Field | Type | Description |
| --- | --- | --- |
| `range` | string | Time range for this summary |
| `averageDailyCalories` | number | Average daily calorie intake (rounded to 1 decimal) |
| `averageDailyProtein` | number | Average daily protein in grams |
| `averageDailyCarbs` | number | Average daily carbohydrates in grams |
| `averageDailyFat` | number | Average daily fat in grams |
| `totalMealsLogged` | number | Total individual food items logged in the period |
| `currentStreak` | number | Current consecutive days with at least one log entry (counting back from today) |
| `longestStreak` | number | Longest-ever consecutive logging streak |
| `weightHistory` | array | Weight data points for charting (currently empty; requires weight tracking feature) |
| `weightHistory[].date` | string | Date of the weight entry |
| `weightHistory[].weight` | number | Weight in kilograms |

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Missing or invalid JWT token |

## Notes

- Averages are computed by dividing total macros by the number of distinct days with logged items (not by calendar days in the range).
- The `currentStreak` counts consecutive days ending at today. If the user has not logged anything today, the streak is 0.
- `weightHistory` is reserved for a future weight tracking feature and currently returns an empty array.
