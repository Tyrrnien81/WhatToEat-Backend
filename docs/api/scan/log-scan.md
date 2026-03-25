# POST /scan/log

Save the recognized food items from a scan session to the user's daily food log.

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |
| `Content-Type` | `application/json` | Yes |

### Body

```json
{
  "scanId": "scan-uuid",
  "items": [
    {
      "name": "Grilled Chicken Breast",
      "calories": 350,
      "protein": 30,
      "carbs": 5,
      "fat": 12
    }
  ]
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `scanId` | string | No | Reference to the original scan session |
| `items` | array | Yes | Food items to log |
| `items[].name` | string | Yes | Food name |
| `items[].calories` | number | Yes | Calorie count |
| `items[].protein` | number | Yes | Protein in grams |
| `items[].carbs` | number | Yes | Carbohydrates in grams |
| `items[].fat` | number | Yes | Total fat in grams |

## Response

### Success (`201 Created`)

```json
{
  "message": "Food log saved successfully",
  "loggedCount": 1
}
```

| Field | Type | Description |
| --- | --- | --- |
| `message` | string | Confirmation message |
| `loggedCount` | number | Number of items logged |

### Errors

| Status | Description |
| --- | --- |
| `400 Bad Request` | Missing or invalid fields (e.g., empty items array) |
| `401 Unauthorized` | Missing or invalid JWT token |

## Notes

- The client may allow the user to modify or remove items from the scan results before calling this endpoint.
- Each logged item is persisted to the user's food log with the current timestamp.
- The `scanId` field is optional and serves as a reference back to the original scan for auditing purposes.
