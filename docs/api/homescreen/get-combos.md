# GET /recommendations/combo

> **Status:** ✅ Implemented — `app/routers/homescreen.py` → `app/services/homescreen_service.py`

Retrieve personalized meal combo recommendations. Combos are optimized to match the user's daily nutrition targets, filtered by their allergens, dislikes, and diet type.

## Request

### Headers

None required.

### Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `user_id` | string (UUID) | Yes | User ID requesting recommendations |
| `date` | string | No | Target date (`YYYY-MM-DD`). Defaults to today. |
| `mealType` | string | No | Filter by meal period: `breakfast`, `lunch`, or `dinner` |

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "combos": [
    {
      "id": "combo-uuid",
      "name": "Balanced Lunch",
      "label": "HIGH PROTEIN",
      "items": [
        {
          "id": 123,
          "name": "Grilled Chicken Breast",
          "calories": 350,
          "protein": 30,
          "carbs": 10,
          "fat": 15,
          "station": "Grill",
          "servingSizeAmount": "1",
          "servingSizeUnit": "serving"
        },
        {
          "id": 456,
          "name": "Brown Rice",
          "calories": 215,
          "protein": 5,
          "carbs": 45,
          "fat": 2,
          "station": "Sides",
          "servingSizeAmount": "1",
          "servingSizeUnit": "cup"
        }
      ],
      "totalCalories": 565,
      "totalProtein": 35,
      "totalCarbs": 55,
      "totalFat": 17,
      "diningHall": "Gordon Avenue Market",
      "logged": false
    }
  ]
}
```

| Field | Type | Description |
| --- | --- | --- |
| `combos` | array | List of recommended meal combos |
| `combos[].id` | string (UUID) | Unique combo identifier (used for saving to favorites) |
| `combos[].name` | string | Display label for the combo (e.g. "Balanced Lunch", "High Protein") |
| `combos[].label` | string \| null | Computed label based on macro ratio |
| `combos[].items` | array | List of food items in the combo |
| `combos[].items[].id` | number | Food ID |
| `combos[].items[].servingSizeAmount` | string \| null | Serving quantity label |
| `combos[].items[].servingSizeUnit` | string \| null | Serving unit label |
| `combos[].totalCalories` | number | Sum of calories for all items |
| `combos[].totalProtein` | number | Sum of protein (g) |
| `combos[].totalCarbs` | number | Sum of carbs (g) |
| `combos[].totalFat` | number | Sum of fat (g) |
| `combos[].diningHall` | string | Dining hall where the combo is available |
| `combos[].logged` | boolean | Whether all items in the combo were already logged that day |

### Errors

| Status | Description |
| --- | --- |
| `422 Unprocessable Entity` | Missing or invalid `user_id` query parameter |

## Notes

- The recommendation engine uses the user's `target_calories`, `target_protein_g`, `target_carbs_g`, and `target_fat_g` from `user_preferences` to optimize combos.
- Combos only include foods that pass the user's allergen and dislike filters.
- Results are scoped to menus available at UW-Madison dining halls for the given date.
- The `mealType` filter is context-aware — if omitted, the server may infer the current meal period based on the time of day.
