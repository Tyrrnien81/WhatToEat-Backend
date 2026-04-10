# POST /auth/logout

Revoke the current user's Supabase session server-side. This invalidates all active sessions for the user, preventing further use of existing tokens. Accessed from the Settings screen.

> **Status:** ✅ Implemented — `app/routers/auth.py` → `app/services/auth_service.py`

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
  "message": "Logged out successfully"
}
```

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Invalid, expired, or missing JWT token |
| `502 Bad Gateway` | Failed to revoke session via Supabase Admin API |

## Notes

- The backend calls the Supabase Auth Admin API (`POST /auth/v1/logout` with `scope: global`) to revoke all sessions for the user.
- The client should also clear any locally stored tokens and redirect to the sign-in screen after a successful response.
- Requires `SUPABASE_SERVICE_ROLE_KEY` to be configured in the backend environment.
