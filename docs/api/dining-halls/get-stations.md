# GET /dining-halls/:hallId/stations

Retrieve all food stations within a specific dining hall. Stations represent distinct serving areas (e.g. Grill, Salad Bar, Pizza) within the hall.

## Request

### Headers

None required (public endpoint).

### Path Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `hallId` | number | The unique ID of the dining hall |

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "hallId": 45372,
  "hallName": "Gordon Avenue Market",
  "stations": [
    {
      "id": 146701,
      "name": "1849",
      "position": 1
    },
    {
      "id": 146703,
      "name": "Gordon Buona Cucina",
      "position": 2
    },
    {
      "id": 146706,
      "name": "Gordon Capital City Pizza",
      "position": 3
    },
    {
      "id": 327206,
      "name": "Buckingham Bakery",
      "position": 6
    }
  ]
}
```

| Field | Type | Description |
| --- | --- | --- |
| `hallId` | number | Dining hall identifier |
| `hallName` | string | Dining hall name |
| `stations` | array | List of stations in display order |
| `stations[].id` | number | Station/section identifier (maps to `menu_sections.external_menu_id`) |
| `stations[].name` | string | Station display name (from `section_options.display_name` in Nutrislice data) |
| `stations[].position` | number | Display order within the hall |

### Errors

| Status | Description |
| --- | --- |
| `404 Not Found` | Dining hall with the given ID does not exist |

## Notes

- Station data comes from the `menu_sections` table, which is populated during daily Nutrislice ingestion.
- Station names correspond to specific food areas like `"Gordon Capital City Pizza"`, `"Great Greens"`, `"Fired Up"`, etc.
- Stations may vary by day if the dining hall changes its offerings.
