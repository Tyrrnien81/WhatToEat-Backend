# POST /auth/google

Authenticate using a Google OAuth2 ID token. If the Google account's email is not yet registered, a new user account is automatically created. Returns a JWT access token.

## Request

### Headers

None required (public endpoint).

### Body

```json
{
  "idToken": "<Google OAuth ID token>"
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `idToken` | string | Yes | The ID token obtained from Google Sign-In on the client |

## Response

### Success (`200 OK`)

```json
{
  "token": "<JWT token>",
  "refreshToken": "<refresh token>",
  "user": {
    "id": "uuid",
    "email": "user@gmail.com",
    "name": "John Doe"
  }
}
```

| Field | Type | Description |
| --- | --- | --- |
| `token` | string | JWT access token (expires in 24 hours) |
| `refreshToken` | string | Refresh token for obtaining new access tokens |
| `user.id` | string (UUID) | User identifier |
| `user.email` | string | Email from the Google account |
| `user.name` | string | Display name from the Google account |

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Invalid, expired, or malformed Google ID token |

## Notes

- The server validates the Google ID token using Google's public keys and checks the `aud` claim against `GOOGLE_CLIENT_ID`.
- If the email from the Google token matches an existing user with `provider: google`, the user is signed in.
- If no matching user exists, a new user record is created with `provider: google` and `password_hash: null`.
- Google-authenticated users skip email verification since Google has already verified the email.
- If a user already exists with the same email but a different provider (e.g. `email`), a `409 Conflict` may be returned depending on the linking strategy.
