# POST /auth/signup

Register a new user account with email and password. A 6-digit verification code is sent to the provided email address. The user must verify their email before they can sign in.

## Request

### Headers

None required (public endpoint).

### Body

```json
{
  "email": "user@example.com",
  "password": "yourPassword123",
  "name": "John Doe"
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `email` | string | Yes | Email address for the new account (must be unique) |
| `password` | string | Yes | Password (min 8 chars, must include uppercase, lowercase, digit, and special character) |
| `name` | string | Yes | User's display name |

## Response

### Success (`201 Created`)

```json
{
  "message": "Account created successfully. Verification code sent to email.",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

| Field | Type | Description |
| --- | --- | --- |
| `message` | string | Confirmation message |
| `user.id` | string (UUID) | Newly created user identifier |
| `user.email` | string | Registered email address |
| `user.name` | string | User's display name |

### Errors

| Status | Description |
| --- | --- |
| `400 Bad Request` | Missing or invalid fields — password does not meet complexity requirements |
| `409 Conflict` | Email address is already registered |

## Notes

- After signup, a 6-digit verification code is generated, stored in the `verification_codes` table, and sent to the user's email.
- The OTP expires after approximately 6 minutes.
- The user cannot sign in until their email is verified via `POST /auth/verify-email`.
- Password is hashed with bcrypt before storage.
- The `provider` field is set to `email` for email-based registrations.
