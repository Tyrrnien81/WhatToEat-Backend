# GET /auth/me

Retrieve the currently authenticated user's basic profile information, decoded from the JWT token. This is a lightweight endpoint used by the client to confirm the user's identity and display their info.

## Request

### Headers

```http
Authorization: Bearer <JWT token>
```

### Body

None.

## Response

### Success (`200 OK`)

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe"
}
```

| Field | Type | Description |
| --- | --- | --- |
| `id` | string (UUID) | Unique user identifier |
| `email` | string | User's email address |
| `name` | string | User's display name |

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Invalid, expired, or missing JWT token |

## Notes

- This endpoint decodes the JWT to extract user information. It may also query the database for the latest user data depending on implementation.
- Used by the client on app launch to validate the stored token and retrieve the user's name/email for display.
- For the full user profile (including preferences, weight, height, etc.), use `GET /users/me` from the Profile service instead.
