# GET /dining-halls/:hallId

Retrieve detailed metadata for a specific dining hall.

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
  "externalRestaurantId": 45372,
  "availableMealTypes": ["Breakfast", "Lunch", "Dinner"],
  "availableDates": ["2026-04-07", "2026-04-06", "2026-04-05"]
}
```

| Field | Type | Description |
| --- | --- | --- |
| `id` | number | Dining hall identifier |
| `name` | string | Dining hall name |
| `externalRestaurantId` | number | External Nutrislice restaurant ID |
| `availableMealTypes` | string[] | Meal types available for this hall |
| `availableDates` | string[] | Most recent available service dates |

### Errors

| Status | Description |
| --- | --- |
| `404 Not Found` | Dining hall with the given ID does not exist |

## Notes

- `availableMealTypes` and `availableDates` are derived from existing menu snapshots.
