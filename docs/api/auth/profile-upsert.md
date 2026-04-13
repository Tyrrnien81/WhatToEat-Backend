# POST /auth/profile

Create or update the authenticated user's profile in the backend database. Called by the frontend after a successful Supabase auth flow (signup, signin, or Google OAuth) to sync the user's identity into the `profiles` table.

> **Status:** ✅ Implemented — `app/routers/auth.py` → `app/services/auth_service.py`

## Request

### Headers

| Header | Value | Required |
| --- | --- | --- |
| `Authorization` | `Bearer <JWT token>` | Yes |
| `Content-Type` | `application/json` | Yes |

### Body

```json
{
  "name": "John Doe"
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | No | Display name (1–100 characters). If omitted on create, stored as `null`. If omitted on update, existing name is preserved. |

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
| `id` | string (UUID) | User identifier |
| `email` | string \| null | Email extracted from the JWT payload |
| `name` | string \| null | Display name |
| `avatar_url` | string \| null | Profile photo URL |

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Invalid, expired, or missing JWT token |

## Notes

- This is an **upsert** operation: if no `profiles` row exists for the user, one is created; otherwise the existing row is updated.
- The `email` field is extracted from the Supabase JWT payload (not from the request body), ensuring it always matches the authenticated identity.
- The `user_id` (primary key) is the Supabase `auth.users.id` UUID, extracted from the JWT `sub` claim.
- This endpoint should be called once after every successful Supabase auth flow to ensure the backend profile stays in sync.
