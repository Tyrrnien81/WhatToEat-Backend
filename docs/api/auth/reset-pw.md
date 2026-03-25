# POST /auth/reset-pw

Reset the user's password after successful email verification. The user must first call `POST /auth/forgot-pw` to receive a code, then `POST /auth/verify-email` to validate it, before using this endpoint.

## Request

### Headers

None required (public endpoint).

### Body

```json
{
  "email": "user@example.com",
  "code": "123456",
  "newPassword": "newSecurePassword456"
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `email` | string | Yes | The email address associated with the account |
| `code` | string | Yes | The 6-digit verification code (must be already verified) |
| `newPassword` | string | Yes | The new password (min 8 chars, must include uppercase, lowercase, digit, and special character) |

## Response

### Success (`200 OK`)

```json
{
  "message": "Password reset successfully"
}
```

### Errors

| Status | Description |
| --- | --- |
| `400 Bad Request` | Invalid or expired verification code, or new password does not meet complexity requirements |
| `404 Not Found` | No account registered with this email address |

## Notes

- The code is re-validated during this call to prevent tampering between verification and reset.
- The new password is hashed with bcrypt before updating the `password_hash` column in the `users` table.
- After a successful reset, all existing OTP codes for this user are invalidated.
- The user's existing JWT sessions are not automatically invalidated (MVP behavior). Consider adding token revocation in v2.
- Only available for users with `provider: email`.
