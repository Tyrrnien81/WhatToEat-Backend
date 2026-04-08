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
| `mealType` | string | No | Filter by meal period: `breakfast`, `lunch`, or `dinner` |
| `meal` | string | No | Backward-compatible alias of `mealType` |

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "hallId": 45372,
  "hallName": "Gordon Avenue Market",
  "date": "2026-03-23",
  "mealType": "dinner",
  "stationMenus": [
    {
      "station": "1849",
      "items": [
        {
          "id": 1303331,
          "name": "Grilled Flank Steak",
          "category": "entree",
          "calories": 187,
          "protein": 24,
          "carbs": 0,
          "fat": 9,
          "icons": ["halal"],
          "station": "1849",
          "servingSizeAmount": "1",
          "servingSizeUnit": "serving"
        },
        {
          "id": 1303332,
          "name": "Roasted Vegetables",
          "category": "side",
          "calories": 120,
          "protein": 3,
          "carbs": 18,
          "fat": 5,
          "icons": ["vegan", "vegetarian"],
          "station": "1849",
          "servingSizeAmount": "1",
          "servingSizeUnit": "cup"
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
| `mealType` | string \| null | Meal period filter used by the endpoint |
| `stationMenus` | array | List of station groups with menu items |
| `stationMenus[].station` | string | Station display name |
| `stationMenus[].items` | array | Food items in the station |
| `stationMenus[].items[].id` | number | Food ID |
| `stationMenus[].items[].category` | string \| null | Source category label |
| `stationMenus[].items[].icons` | string[] | Dietary/allergen icon slugs |
| `stationMenus[].items[].servingSizeAmount` | string \| null | Serving quantity |
| `stationMenus[].items[].servingSizeUnit` | string \| null | Serving unit |

### Errors

| Status | Description |
| --- | --- |
| `404 Not Found` | Dining hall not found |

## Notes

- Menu data is sourced from the daily Nutrislice ingestion pipeline and stored across `menu_snapshots`, `menu_section_items`, `foods`, `food_nutrition`, and `food_icon_assignments` tables.
- Section header rows from the Nutrislice data (where `food = null` and `is_section_title = true`) are filtered out — only actual food items are returned.
- The `icons` field maps from the `food_icons` table via `food_icon_assignments`.
- If both `mealType` and `meal` are supplied, `mealType` takes precedence.
- If no snapshots match the filters, the endpoint returns an empty `stationMenus` list.
