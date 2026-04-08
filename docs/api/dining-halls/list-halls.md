# GET /dining-halls

Retrieve a list of all available UW-Madison dining halls.

## Request

### Headers

None required (public endpoint).

### Query Parameters

None.

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
      "externalRestaurantId": 45372
    },
    {
      "id": 45373,
      "name": "Carson's Market",
      "externalRestaurantId": 45373
    }
  ]
}
```

| Field | Type | Description |
| --- | --- | --- |
| `diningHalls` | array | List of all dining halls |
| `diningHalls[].id` | number | Internal dining hall identifier |
| `diningHalls[].name` | string | Dining hall name |
| `diningHalls[].externalRestaurantId` | number | External Nutrislice restaurant ID |

### Errors

None expected (always returns a list, may be empty).

## Notes

- Use `/dining-halls/:hallId` for available meal types and dates.
