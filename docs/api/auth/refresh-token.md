# POST /auth/refresh-token

> **Handled by Supabase client-side.** This is NOT a backend endpoint.

Refresh an expired JWT access token. The Supabase JS SDK handles token refresh automatically via its built-in session management.

## Frontend Usage

```typescript
// Automatic — Supabase SDK refreshes tokens before they expire.
// Manual refresh (if needed):
const { data, error } = await supabase.auth.refreshSession();
```

## Notes

- The Supabase JS SDK automatically refreshes the access token before it expires, so manual refresh is rarely needed.
- Token rotation is enabled by default — each refresh issues a new refresh token and invalidates the old one.
- See [Supabase Auth docs](https://supabase.com/docs/reference/javascript/auth-refreshsession) for full reference.
