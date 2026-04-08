# GET /dining-halls/:hallId/stations

Retrieve all food stations within a specific dining hall for a given date and meal type.

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
| `mealType` | string | No | Meal period filter (`breakfast`, `lunch`, `dinner`) |

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "hallId": 45372,
  "date": "2026-03-23",
  "mealType": "dinner",
  "stations": [
    {
      "station": "1849",
      "itemCount": 12
    },
    {
      "station": "Gordon Buona Cucina",
      "itemCount": 8
    },
    {
      "station": "Gordon Capital City Pizza",
      "itemCount": 6
    }
  ]
}
```

| Field | Type | Description |
| --- | --- | --- |
| `hallId` | number | Dining hall identifier |
| `date` | string | Date used for lookup |
| `mealType` | string \| null | Meal period filter used by the endpoint |
| `stations` | array | List of station entries |
| `stations[].station` | string | Station display name |
| `stations[].itemCount` | number | Number of menu items in the station |

### Errors

| Status | Description |
| --- | --- |
| `404 Not Found` | Dining hall with the given ID does not exist |

## Notes

- If no snapshots match the filters, the endpoint returns an empty `stations` list.
