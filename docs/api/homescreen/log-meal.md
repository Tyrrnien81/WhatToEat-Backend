# POST /meals/log

> **Status:** ✅ Implemented — `app/routers/homescreen.py` → `app/services/homescreen_service.py`

Log a meal with one or more food items. Creates or finds an existing meal log entry for the given user/date/meal type, then appends food items with snapshotted nutrition data.

## Request

### Headers

None required.

### Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `user_id` | string (UUID) | Yes | User ID logging the meal |

### Body

```json
{
  "date": "2026-03-24",
  "mealType": "lunch",
  "items": [
    {
      "foodId": 123,
      "foodName": "Grilled Chicken Breast",
      "quantity": 1.0,
      "calories": 350,
      "protein": 30,
      "carbs": 10,
      "fat": 15,
      "source": "menu"
    },
    {
      "foodId": 456,
      "foodName": "Brown Rice",
      "quantity": 1.0,
      "source": "menu"
    }
  ]
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `date` | string | Yes | Date of the meal (`YYYY-MM-DD`) |
| `mealType` | string | Yes | Meal period: `breakfast`, `lunch`, or `dinner` |
| `items` | array | Yes | List of food items to log |
| `items[].foodId` | integer | No | FK → `foods.id`. If provided and nutrition fields are omitted, nutrition is looked up from `food_nutrition` |
| `items[].foodName` | string | Yes | Display name of the food (denormalized for historical accuracy) |
| `items[].quantity` | number | No | Number of servings (default: `1.0`) |
| `items[].calories` | number | No | Calories to snapshot. If omitted and `foodId` is provided, looked up from DB |
| `items[].protein` | number | No | Protein (g) to snapshot |
| `items[].carbs` | number | No | Carbs (g) to snapshot |
| `items[].fat` | number | No | Fat (g) to snapshot |
| `items[].source` | string | No | How the item was logged: `menu`, `scan`, or `manual` (default: `menu`) |

## Response

### Success (`201 Created`)

```json
{
  "mealLogId": 42,
  "message": "Meal logged successfully"
}
```

| Field | Type | Description |
| --- | --- | --- |
| `mealLogId` | integer | ID of the created/updated `meal_logs` record |
| `message` | string | Confirmation message |

### Errors

| Status | Description |
| --- | --- |
| `422 Unprocessable Entity` | Invalid request body (missing required fields, bad date format) |

## Notes

- If a `meal_log` already exists for the same user + date + mealType, items are appended to it (no duplicate log created).
- Nutrition values are snapshotted at log time so historical logs stay accurate even if food data changes later.
- If `foodId` is provided but nutrition fields (`calories`, `protein`, etc.) are omitted, the service looks up values from the `food_nutrition` table automatically.
- The `source` field tracks how the item was logged — `menu` (from dining hall menu), `scan` (from photo recognition), or `manual` (user-entered).
