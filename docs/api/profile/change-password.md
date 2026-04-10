# POST /users/me/change-password

Change the authenticated user's password. Requires the current password for verification.

> **Status:** ✅ Implemented — `app/routers/profile.py` → `app/services/profile_service.py`

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |
| `Content-Type` | `application/json` | Yes |

### Body

```json
{
  "currentPassword": "oldP@ss123",
  "newPassword": "newSecureP@ss456"
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `currentPassword` | string | Yes | The user's current password for verification |
| `newPassword` | string | Yes | The new password (minimum 8 characters) |

## Response

### Success (`200 OK`)

```json
{
  "message": "Password changed successfully"
}
```

### Errors

| Status | Description |
| --- | --- |
| `400 Bad Request` | Current password is incorrect, new password too short, or user is OAuth-only |
| `401 Unauthorized` | Missing or invalid JWT token |
| `501 Not Implemented` | Supabase credentials not configured on the server |

## Notes

- The new password must be at least 8 characters.
- The current password is verified by attempting a sign-in against the Supabase Auth API.
- This endpoint is not available for users who signed up via Google OAuth (they have no local password). Returns `400` with an explanatory message.
- Requires `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` environment variables.
