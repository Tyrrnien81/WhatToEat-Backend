# POST /auth/reset-pw

> **Handled by Supabase client-side.** This is NOT a backend endpoint.

Set a new password after the user has verified their identity via the reset email flow. The frontend calls `supabase.auth.updateUser()` directly.

## Frontend Usage

```typescript
const { error } = await supabase.auth.updateUser({
  password: "newSecurePassword456",
});
```

## Notes

- This must be called after the user has clicked the password reset link from their email and has an active Supabase session.
- Password requirements are configured in the Supabase dashboard.
- See [Supabase Auth docs](https://supabase.com/docs/reference/javascript/auth-updateuser) for full reference.
