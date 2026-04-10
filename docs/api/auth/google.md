# POST /auth/google

> **Handled by Supabase client-side.** This is NOT a backend endpoint.

Authenticate using Google OAuth. The frontend calls `supabase.auth.signInWithOAuth()` directly. Supabase handles the OAuth flow, creates the user if new, and returns a session.

## Frontend Usage

```typescript
const { data, error } = await supabase.auth.signInWithOAuth({
  provider: "google",
});
```

## Notes

- Google OAuth must be enabled and configured in the Supabase dashboard (Settings > Authentication > Providers).
- Supabase auto-creates the user record if the Google email is not yet registered.
- Google-authenticated users skip email verification.
- After successful OAuth, call `POST /auth/profile` to sync the backend profile.
- See [Supabase Auth docs](https://supabase.com/docs/reference/javascript/auth-signinwithoauth) for full reference.
