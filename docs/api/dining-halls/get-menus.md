# GET /dining-halls/:hallId/menus

Retrieve the menu items available at each station in a specific dining hall. Returns food items grouped by station with nutritional information and dietary tags.

## Request

### Headers

None required (public endpoint).

### Path Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `hallId` | number | The unique ID of the dining hall |

### Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `date` | string | No | Menu date (`YYYY-MM-DD`). Defaults to today. |
| `mealPeriod` | string | No | Filter by meal period: `breakfast`, `lunch`, or `dinner` |

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "hallId": 45372,
  "hallName": "Gordon Avenue Market",
  "date": "2026-03-23",
  "mealPeriod": "dinner",
  "stations": [
    {
      "id": 146701,
      "name": "1849",
      "items": [
        {
          "id": 1303331,
          "name": "Grilled Flank Steak",
          "category": "entree",
          "price": 6.99,
          "calories": 187,
          "protein": 24,
          "carbs": 0,
          "fat": 9,
          "icons": ["halal"],
          "allergens": []
        },
        {
          "id": 1303332,
          "name": "Roasted Vegetables",
          "category": "side",
          "price": 3.49,
          "calories": 120,
          "protein": 3,
          "carbs": 18,
          "fat": 5,
          "icons": ["vegan", "vegetarian"],
          "allergens": []
        }
      ]
    }
  ]
}
```

| Field | Type | Description |
| --- | --- | --- |
| `hallId` | number | Dining hall identifier |
| `hallName` | string | Dining hall name |
| `date` | string | Menu date |
| `mealPeriod` | string | Meal period for this menu |
| `stations` | array | List of stations with their menu items |
| `stations[].items` | array | Food items at this station |
| `stations[].items[].id` | number | Food identifier (from `foods.external_food_id`) |
| `stations[].items[].name` | string | Food name |
| `stations[].items[].category` | string | Food category: `entree`, `side`, `dessert`, `other` |
| `stations[].items[].price` | number | Price in USD |
| `stations[].items[].calories` | number | Calorie count |
| `stations[].items[].protein` | number | Protein in grams |
| `stations[].items[].carbs` | number | Carbohydrates in grams |
| `stations[].items[].fat` | number | Total fat in grams |
| `stations[].items[].icons` | string[] | Dietary tags (e.g. `vegan`, `vegetarian`, `halal`) |
| `stations[].items[].allergens` | string[] | Allergen flags (e.g. `dairy`, `gluten`, `peanuts`) |

### Errors

| Status | Description |
| --- | --- |
| `404 Not Found` | Dining hall not found, or no menu available for the requested date/meal period |

## Notes

- Menu data is sourced from the daily Nutrislice ingestion pipeline and stored across `menu_snapshots`, `menu_section_items`, `foods`, `food_nutrition`, and `food_icon_assignments` tables.
- Section header rows from the Nutrislice data (where `food = null` and `is_section_title = true`) are filtered out — only actual food items are returned.
- The `icons` field maps from the `food_icons` table via `food_icon_assignments`.
- If `mealPeriod` is omitted, the server may return all available meal periods or infer the current one.
