# POST /auth/refresh-token

Refresh an expired JWT access token using a valid refresh token. Used on app launch and when API calls return `401` to maintain seamless user sessions without re-authentication.

## Request

### Headers

None required (public endpoint).

### Body

```json
{
  "refreshToken": "<refresh token>"
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `refreshToken` | string | Yes | The refresh token issued during sign-in or a previous refresh |

## Response

### Success (`200 OK`)

```json
{
  "token": "<new JWT access token>",
  "refreshToken": "<new refresh token>"
}
```

| Field | Type | Description |
| --- | --- | --- |
| `token` | string | New JWT access token (expires in 24 hours) |
| `refreshToken` | string | New refresh token (rotated for security) |

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Refresh token is invalid, expired, or has been revoked |

## Notes

- Refresh token rotation is used — each refresh call issues a new refresh token and revokes the old one.
- If a revoked or invalid refresh token is used, the request is rejected with `401`.
- The client should call this endpoint automatically when receiving a `401` response from any protected endpoint, and retry the original request with the new access token.
