# POST /auth/signin

> **Handled by Supabase client-side.** This is NOT a backend endpoint.

Sign in with email and password. The frontend calls `supabase.auth.signInWithPassword()` directly. Supabase returns a JWT access token and refresh token. After successful auth, the frontend should call `POST /auth/profile` to sync the user's profile with the backend.

## Frontend Usage

```typescript
const { data, error } = await supabase.auth.signInWithPassword({
  email: "user@example.com",
  password: "yourPassword123",
});
```

## Supabase Response

```json
{
  "session": {
    "access_token": "<JWT>",
    "refresh_token": "<refresh token>",
    "expires_in": 3600
  },
  "user": {
    "id": "uuid",
    "email": "user@example.com"
  }
}
```

## Notes

- The user's email must be verified before sign-in is allowed.
- After successful sign-in, call `POST /auth/profile` to ensure the backend profile exists.
- Store the session using Supabase's built-in session management.
- See [Supabase Auth docs](https://supabase.com/docs/reference/javascript/auth-signinwithpassword) for full reference.
