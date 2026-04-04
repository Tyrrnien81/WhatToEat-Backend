# POST /auth/logout

Log out the current user and invalidate their session. Accessed from the Settings screen in the app, not from the home screen.

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
  "message": "Logged out successfully"
}
```

### Errors

| Status | Description |
| --- | --- |
| `401 Unauthorized` | Invalid, expired, or missing JWT token |

## Notes

- Logout revokes all refresh tokens for the user server-side, preventing further token refreshes.
- The client should also clear the stored JWT and refresh token from secure storage and redirect to the sign-in screen.
- This endpoint is accessed from **Settings**, not from the main home screen.
