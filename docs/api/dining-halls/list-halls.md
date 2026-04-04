# GET /dining-halls

Retrieve a list of all available UW-Madison dining halls with their current status and basic information.

## Request

### Headers

None required (public endpoint).

### Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `sort` | string | No | Sort order: `openNow` (open halls first), `closest` (by proximity), or `relevance` (default) |

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "diningHalls": [
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
      "emoji": "🍕"
    },
    {
      "id": 45373,
      "name": "Carson's Market",
      "location": "1515 Tripp Circle",
      "status": "closed",
      "hours": {
        "lunch": "11:00 AM – 2:00 PM",
        "dinner": "5:00 PM – 8:00 PM"
      },
      "emoji": "🥗"
    }
  ]
}
```

| Field | Type | Description |
| --- | --- | --- |
| `diningHalls` | array | List of all dining halls |
| `diningHalls[].id` | number | Dining hall identifier (maps to `external_restaurant_id`) |
| `diningHalls[].name` | string | Dining hall name |
| `diningHalls[].location` | string | Physical address |
| `diningHalls[].status` | string | Current status: `open`, `closing_soon`, or `closed` |
| `diningHalls[].hours` | object | Operating hours by meal period |
| `diningHalls[].emoji` | string | Emoji identifier for the hall (used in UI) |

### Errors

None expected (always returns a list, may be empty).

## Notes

- Status is derived from `operating_hours` (JSONB) in the `restaurants` table compared against the current time.
- UW-Madison currently has 6 dining halls. This endpoint returns all of them regardless of status.
- Results are cached in Redis and invalidated daily after Nutrislice ingestion.
