# GET /auth/me

Retrieve the currently authenticated user's profile from the database. Used by the client on app launch to validate the stored token and display the user's info.

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
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@wisc.edu",
  "name": "John Doe",
  "avatar_url": null
}
```

| Field | Type | Description |
| --- | --- | --- |
| `id` | string (UUID) | User identifier (matches Supabase `auth.users.id`) |
| `email` | string \| null | User's email address |
| `name` | string \| null | Display name |
| `avatar_url` | string \| null | Profile photo URL |

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Invalid, expired, or missing JWT token |

## Notes

- If the user has authenticated via Supabase but has not yet called `POST /auth/profile`, this endpoint returns a minimal response with only `id` populated (from the JWT `sub` claim) and other fields as `null`.
- For the full user profile including preferences and body metrics, use `GET /users/me` from the Profile service.
- This is a lightweight endpoint; it queries the `profiles` table only.
