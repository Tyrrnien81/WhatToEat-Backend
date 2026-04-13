# POST /auth/forgot-pw

> **Handled by Supabase client-side.** This is NOT a backend endpoint.

Initiate the password reset flow. The frontend calls `supabase.auth.resetPasswordForEmail()` directly. Supabase sends a password reset email with a link or OTP.

## Frontend Usage

```typescript
const { error } = await supabase.auth.resetPasswordForEmail(
  "user@example.com"
);
```

## Notes

- The reset email template and redirect URL are configured in the Supabase dashboard.
- After the user clicks the reset link, they are redirected to the app where `supabase.auth.updateUser()` is called with the new password.
- See [Supabase Auth docs](https://supabase.com/docs/reference/javascript/auth-resetpasswordforemail) for full reference.
