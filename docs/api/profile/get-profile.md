# GET /users/me

Retrieve the currently authenticated user's full profile, including personal information, body metrics, and dietary preferences.

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "id": "uuid",
  "email": "user@wisc.edu",
  "name": "John Doe",
  "birthday": "2000-01-15",
  "gender": "male",
  "height": 175,
  "weight": 70,
  "goalWeight": 65,
  "dietType": "vegetarian",
  "avatarUrl": "https://s3.amazonaws.com/whattoeat/avatars/user123.jpg",
  "createdAt": "2026-01-10T08:00:00Z"
}
```

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | User unique identifier |
| `email` | string | User's email address |
| `name` | string | Display name |
| `birthday` | string | Date of birth (`YYYY-MM-DD`) |
| `gender` | string | Gender: `male`, `female`, or `other` |
| `height` | number | Height in centimeters |
| `weight` | number | Current weight in kilograms |
| `goalWeight` | number | Target weight in kilograms |
| `dietType` | string | Dietary preference (e.g., `vegetarian`, `vegan`, `halal`, `none`) |
| `avatarUrl` | string \| null | Profile photo URL (S3) |
| `createdAt` | string | ISO 8601 account creation timestamp |

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Missing or invalid JWT token |
