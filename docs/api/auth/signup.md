# POST /auth/signup

> **Handled by Supabase client-side.** This is NOT a backend endpoint.

Register a new user account. The frontend calls `supabase.auth.signUp()` directly. Supabase handles email verification and password hashing.

## Frontend Usage

```typescript
const { data, error } = await supabase.auth.signUp({
  email: "user@example.com",
  password: "yourPassword123",
  options: {
    data: { name: "John Doe" },
  },
});
```

## Notes

- Supabase sends a verification email automatically.
- Password requirements are configured in the Supabase dashboard.
- After email verification and first sign-in, call `POST /auth/profile` to create the backend profile.
- See [Supabase Auth docs](https://supabase.com/docs/reference/javascript/auth-signup) for full reference.
