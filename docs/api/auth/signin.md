# POST /auth/signin

Sign in with email and password. Returns a JWT access token and the authenticated user's basic profile information.

## Request

### Headers

None required (public endpoint).

### Body

```json
{
  "email": "user@example.com",
  "password": "yourPassword123"
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `email` | string | Yes | The user's registered email address |
| `password` | string | Yes | The user's password |

## Response

### Success (`200 OK`)

```json
{
  "token": "<JWT token>",
  "refreshToken": "<refresh token>",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

| Field | Type | Description |
| --- | --- | --- |
| `token` | string | JWT access token (expires in 24 hours) |
| `refreshToken` | string | Refresh token for obtaining new access tokens |
| `user.id` | string (UUID) | Unique user identifier |
| `user.email` | string | User's email address |
| `user.name` | string | User's display name |

### Errors

| Status | Description |
| --- | --- |
| `400 Bad Request` | Missing or invalid fields (e.g. empty email or password) |
| `401 Unauthorized` | Incorrect email or password |
| `401 Unauthorized` | Email not yet verified — user must verify before signing in |

## Notes

- The user's email must be verified before sign-in is allowed. If unverified, the client should redirect to the email verification flow.
- The JWT token should be stored securely on the client and included in the `Authorization: Bearer <token>` header for all protected endpoints.
- Password is validated against the bcrypt hash stored in the database.
