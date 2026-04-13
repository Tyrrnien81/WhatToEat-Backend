# GET /users/me

Retrieve the currently authenticated user's full profile, including personal information, body metrics, and dietary preferences.

> **Status:** ✅ Implemented — `app/routers/profile.py` → `app/services/profile_service.py`

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
  "avatarUrl": null,
  "createdAt": "2026-01-10T08:00:00Z"
}
```

| Field | Type | Description |
| --- | --- | --- |
| `id` | string (UUID) | User unique identifier |
| `email` | string | User's email address |
| `name` | string | Display name |
| `birthday` | string \| null | Date of birth (`YYYY-MM-DD`) |
| `gender` | string \| null | Gender: `male`, `female`, or `other` |
| `height` | number \| null | Height in centimeters |
| `weight` | number \| null | Current weight in kilograms |
| `goalWeight` | number \| null | Target weight in kilograms |
| `dietType` | string \| null | Dietary preference (e.g., `vegetarian`, `vegan`, `halal`, `none`) |
| `avatarUrl` | string \| null | Profile photo URL |
| `createdAt` | string | ISO 8601 account creation timestamp |

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Missing or invalid JWT token |
| `404 Not Found` | Profile not found for the authenticated user |

## Notes

- Response merges data from `profiles` table (id, email, name, avatarUrl, createdAt) and `user_preferences` table (birthday, gender, height, weight, goalWeight, dietType).
- If the user has not completed the questionnaire, preference fields return `null`.
