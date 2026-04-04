# POST /auth/verify-email

Verify the user's email address using a 6-digit verification code. This endpoint is used in both the signup flow (to activate a new account) and the password reset flow (to authorize a password change).

## Request

### Headers

None required (public endpoint).

### Body

```json
{
  "email": "user@example.com",
  "code": "123456"
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `email` | string | Yes | The email address to verify |
| `code` | string | Yes | The 6-digit verification code sent to the email |

## Response

### Success (`200 OK`)

```json
{
  "message": "Email verified successfully"
}
```

### Errors

| Status | Description |
| --- | --- |
| `400 Bad Request` | Invalid or expired verification code (codes expire after ~6 minutes) |
| `404 Not Found` | No account registered with this email address |

## Notes

- The code is looked up in the `verification_codes` table by `email` + `code` and checked against `expires_at`.
- Once verified successfully, all verification code records for that email are deleted.
- For signup: the user's email is marked as verified, allowing them to sign in.
- For password reset: verification must be completed before calling `POST /auth/reset-pw`.
- A code can only be used once. If the user needs a new code, they should use `POST /auth/resend-code`.
