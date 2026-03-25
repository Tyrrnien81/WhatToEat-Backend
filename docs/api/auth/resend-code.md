# POST /auth/resend-code

Resend a 6-digit verification code to the user's email. A 30-second cooldown is enforced between consecutive resend requests to prevent abuse.

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
| `email` | string | Yes | The email address to resend the verification code to |

## Response

### Success (`200 OK`)

```json
{
  "message": "Verification code resent to email"
}
```

### Errors

| Status | Description |
| --- | --- |
| `404 Not Found` | No account registered with this email address |
| `429 Too Many Requests` | Resend cooldown has not elapsed (must wait 30 seconds between attempts) |

## Notes

- A new verification code is generated each time this endpoint is called (previous codes remain valid until they expire).
- The new code expires after approximately 6 minutes.
- The 30-second cooldown is tracked server-side per user to prevent rapid resend abuse.
- This endpoint works for both signup verification and password reset verification flows.
