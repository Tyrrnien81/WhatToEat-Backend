# POST /scan

Upload a food photo for AI-based recognition. The server processes the image and returns identified food items along with calorie and macronutrient data.

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |
| `Content-Type` | `multipart/form-data` | Yes |

### Body (`multipart/form-data`)

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `image` | file | Yes | The food photo to analyze. Supported formats: JPEG, PNG, HEIC. |

## Response

### Success (`200 OK`)

```json
{
  "scanId": "scan-uuid",
  "items": [
    {
      "name": "Grilled Chicken Breast",
      "confidence": 0.92,
      "calories": 350,
      "protein": 30,
      "carbs": 5,
      "fat": 12
    },
    {
      "name": "Steamed Broccoli",
      "confidence": 0.87,
      "calories": 55,
      "protein": 4,
      "carbs": 11,
      "fat": 1
    }
  ],
  "summary": {
    "kcal": 405,
    "protein": 34,
    "carbs": 16,
    "fat": 13
  }
}
```

| Field | Type | Description |
| --- | --- | --- |
| `scanId` | string | Unique identifier for this scan session |
| `items` | array | List of identified food items |
| `items[].name` | string | Recognized food name |
| `items[].confidence` | number | Confidence score (0.0–1.0) for the recognition |
| `items[].calories` | number | Estimated calorie count |
| `items[].protein` | number | Protein in grams |
| `items[].carbs` | number | Carbohydrates in grams |
| `items[].fat` | number | Total fat in grams |
| `summary` | object | Aggregate nutrition totals for quick display |
| `summary.kcal` | number | Total calories across identified items |
| `summary.protein` | number | Total protein in grams across identified items |
| `summary.carbs` | number | Total carbohydrates in grams across identified items |
| `summary.fat` | number | Total fat in grams across identified items |

### Errors

| Status | Description |
| --- | --- |
| `400 Bad Request` | No image provided or unsupported file format |
| `401 Unauthorized` | Missing or invalid JWT token |
| `422 Unprocessable Entity` | Could not identify any food in the image |

## Notes

- Multiple food items may be identified from a single photo.
- The `scanId` is used when subsequently calling `POST /scan/log` to persist the results.
- Confidence scores below a threshold may indicate uncertain recognition — the client should allow the user to review and correct results before logging.
