# POST /users/me/avatar

Upload or update the user's profile photo.

> **Status:** ✅ Implemented — `app/routers/profile.py` → `app/services/profile_service.py`

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |
| `Content-Type` | `multipart/form-data` | Yes |

### Body (`multipart/form-data`)

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `avatar` | file | Yes | Profile photo image file. Supported formats: JPEG, PNG. |

## Response

### Success (`200 OK`)

```json
{
  "message": "Avatar updated successfully",
  "avatarUrl": "/uploads/avatars/user-uuid.jpg"
}
```

| Field | Type | Description |
| --- | --- | --- |
| `message` | string | Confirmation message |
| `avatarUrl` | string | URL path of the uploaded profile photo |

### Errors

| Status | Description |
| --- | --- |
| `400 Bad Request` | No image provided, empty payload, or unsupported file format |
| `401 Unauthorized` | Missing or invalid JWT token |
| `404 Not Found` | Profile not found |

## Notes

- Currently stores files locally under `uploads/avatars/`. In production, swap to S3 and return full S3 URLs.
- If the user already has an avatar, the previous file is overwritten.
- The `profiles.avatar_url` column is updated with the new URL path.
