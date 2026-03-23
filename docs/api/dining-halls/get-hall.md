# GET /dining-halls/:hallId

Retrieve detailed information for a specific dining hall, including location, operating hours, current status, and description.

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
  "id": 45372,
  "name": "Gordon Avenue Market",
  "location": "770 W Dayton St",
  "status": "open",
  "hours": {
    "breakfast": "7:00 AM – 10:00 AM",
    "lunch": "11:00 AM – 2:00 PM",
    "dinner": "5:00 PM – 9:00 PM"
  },
  "description": "A food court style dining hall featuring multiple stations including pizza, grill, bakery, and international cuisine.",
  "emoji": "🍕",
  "latitude": 43.0722,
  "longitude": -89.4008
}
```

| Field | Type | Description |
| --- | --- | --- |
| `id` | number | Dining hall identifier |
| `name` | string | Dining hall name |
| `location` | string | Physical address |
| `status` | string | Current status: `open`, `closing_soon`, or `closed` |
| `hours` | object | Operating hours by meal period |
| `description` | string | Short description of the dining hall |
| `emoji` | string | Emoji identifier for UI display |
| `latitude` | number | GPS latitude for map/proximity features |
| `longitude` | number | GPS longitude for map/proximity features |

### Errors

| Status | Description |
| --- | --- |
| `404 Not Found` | Dining hall with the given ID does not exist |

## Notes

- Data is read from the `restaurants` table.
- The `status` is computed at request time based on `operating_hours` and the current time.
