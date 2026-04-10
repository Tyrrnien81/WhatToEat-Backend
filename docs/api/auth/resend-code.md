# POST /auth/resend-code

> **Handled by Supabase client-side.** This is NOT a backend endpoint.

Resend a verification email to the user. The frontend calls `supabase.auth.resend()` directly.

## Frontend Usage

```typescript
const { error } = await supabase.auth.resend({
  type: "signup",
  email: "user@example.com",
});
```

## Notes

- Rate limiting is handled by Supabase (configurable in the dashboard).
- Works for both signup verification and email change confirmation.
- See [Supabase Auth docs](https://supabase.com/docs/reference/javascript/auth-resend) for full reference.
