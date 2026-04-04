# POST /auth/forgot-pw

Initiate the password reset flow by sending a 6-digit verification code to the user's registered email address. The code is stored in the `verification_codes` table and must be used with `POST /auth/reset-pw` to complete the reset.

## Request

### Headers

None required (public endpoint).

### Body

```json
{
  "email": "user@example.com"
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `email` | string | Yes | The email address associated with the account |

## Response

### Success (`200 OK`)

```json
{
  "message": "Verification code sent to email"
}
```

### Errors

| Status | Description |
| --- | --- |
| `404 Not Found` | No account is registered with this email address |

## Notes

- The 6-digit verification code expires after approximately 6 minutes.
- A new code is generated and stored each time this endpoint is called (previous codes remain valid until they expire).
- The response always returns `200` for registered emails to avoid leaking whether an email exists (in production, consider returning 200 regardless for security).
- After receiving the code, the user should verify it via `POST /auth/verify-email`, then reset the password via `POST /auth/reset-pw`.
- Only available for users with `provider: email`. Google OAuth users cannot reset a password since they don't have one.
