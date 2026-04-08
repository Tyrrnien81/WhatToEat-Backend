# GET /recommendations/addons

Retrieve add-on recommendations for the target meal period.

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
  "mealType": "Lunch",
  "suggestions": [
    {
      "id": 305,
      "name": "Greek Yogurt",
      "calories": 150,
      "protein": 20,
      "carbs": 10,
      "fat": 2,
      "station": "Dairy",
      "icons": ["vegetarian"]
    }
  ],
  "quickAddons": [
    {
      "id": 407,
      "name": "Apple",
      "calories": 95,
      "protein": 0,
      "carbs": 25,
      "fat": 0,
      "station": "Fruit Bar",
      "icons": ["vegan", "vegetarian"]
    }
  ]
}
```

| Field | Type | Description |
| --- | --- | --- |
| `mealType` | string | Resolved meal period returned by backend |
| `suggestions` | array | Balanced add-on recommendations (up to 6) |
| `quickAddons` | array | Lower-calorie quick additions (up to 8) |
| `suggestions[].icons` | string[] | Dietary or allergen icon slugs |
| `quickAddons[].icons` | string[] | Dietary or allergen icon slugs |

### Errors

| Status | Description |
| --- | --- |
| `422 Unprocessable Entity` | Missing or invalid `user_id` query parameter |

## Notes

- Results are filtered by user allergens and dislikes.
- If `mealType` is omitted, backend infers meal period from current time.
