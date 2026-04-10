# PATCH /users/me

Update the current user's profile information. Only include the fields to be updated — omitted fields remain unchanged.

> **Status:** ✅ Implemented — `app/routers/profile.py` → `app/services/profile_service.py`

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |
| `Content-Type` | `application/json` | Yes |

### Body (partial update)

```json
{
  "name": "John Smith",
  "weight": 68,
  "goalWeight": 63,
  "dietType": "vegan"
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | No | Display name |
| `birthday` | string | No | Date of birth (`YYYY-MM-DD`) |
| `gender` | string | No | Gender: `male`, `female`, or `other` |
| `height` | number | No | Height in centimeters |
| `weight` | number | No | Current weight in kilograms |
| `goalWeight` | number | No | Target weight in kilograms |
| `dietType` | string | No | Dietary preference |

## Response

### Success (`200 OK`)

```json
{
  "message": "Profile updated successfully"
}
```

### Errors

| Status | Description |
| --- | --- |
| `400 Bad Request` | Invalid field values |
| `401 Unauthorized` | Missing or invalid JWT token |
| `404 Not Found` | Profile not found |

## Notes

- Uses PATCH semantics — only the fields included in the request body are updated.
- `name` is updated on the `profiles` table. Body metric and diet fields (birthday, gender, height, weight, goalWeight, dietType) are updated on the `user_preferences` table.
- If no `user_preferences` row exists for the user, one is created automatically.
