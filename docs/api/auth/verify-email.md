# POST /auth/verify-email

> **Handled by Supabase client-side.** This is NOT a backend endpoint.

Verify the user's email address. Supabase handles this automatically via email confirmation links or OTP codes, depending on the project configuration.

## Frontend Usage (OTP mode)

```typescript
const { error } = await supabase.auth.verifyOtp({
  email: "user@example.com",
  token: "123456",
  type: "email",
});
```

## Notes

- Email verification behavior is configured in the Supabase dashboard (Settings > Authentication > Email).
- Supabase supports both magic-link and OTP-based verification.
- See [Supabase Auth docs](https://supabase.com/docs/reference/javascript/auth-verifyotp) for full reference.
