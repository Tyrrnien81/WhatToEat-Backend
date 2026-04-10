# 1. Authentication

Authentication uses **Supabase Auth** on the client side. The frontend calls the Supabase JS SDK directly for signup, signin, Google OAuth, email verification, password reset, and token refresh. The backend validates Supabase-issued JWT tokens via JWKS and exposes 3 endpoints for profile management and session revocation.

## Backend Endpoints

| Method | Endpoint | Docs | Description | JWT Required | Status |
| --- | --- | --- | --- | --- | --- |
| GET | `/auth/me` | [me.md](me.md) | Retrieve the authenticated user's profile | Yes | ✅ Built |
| POST | `/auth/profile` | [profile-upsert.md](profile-upsert.md) | Create or update profile after Supabase auth | Yes | ✅ Built |
| POST | `/auth/logout` | [logout.md](logout.md) | Revoke Supabase session server-side | Yes | ✅ Built |

## Supabase Client-Side Flows

The following auth flows are handled entirely by the frontend using `@supabase/supabase-js`. The backend is **not involved** in these operations — Supabase manages user credentials, email verification, and token lifecycle directly.

| Flow | Supabase Method | Frontend Screen |
| --- | --- | --- |
| Sign in | `signInWithPassword()` | LoginScreen |
| Sign up | `signUp()` | SignupScreen |
| Google OAuth | `signInWithOAuth()` | LoginScreen (social button) |
| Forgot password | `resetPasswordForEmail()` | ForgotPasswordScreen |
| Verify email | Automatic (email link or OTP) | VerifyEmailScreen |
| Resend code | `resend()` | VerifyEmailScreen |
| Reset password | `updateUser()` | ResetPasswordScreen |
| Refresh token | Automatic (SDK session management) | — |

## Project Structure (Auth)

```
app/
├── routers/
│   └── auth.py              # /auth/* endpoint definitions
├── schemas/
│   └── auth.py              # Pydantic request/response models
├── services/
│   └── auth_service.py      # Business logic: profile CRUD, logout
├── models/
│   └── user.py              # Profile model (profiles table)
├── dependencies.py          # JWT via Supabase JWKS; optional dev `?user_id=` when ALLOW_QUERY_USER_ID (homescreen/community/scan only)
└── config.py                # Supabase URL, issuer, service role key
```

| File | Responsibility |
| --- | --- |
| `app/routers/auth.py` | Defines `/auth/me`, `/auth/profile`, `/auth/logout` route handlers |
| `app/schemas/auth.py` | `UserResponse`, `UpsertProfileRequest`, `MessageResponse` |
| `app/services/auth_service.py` | Profile lookup/upsert, Supabase session revocation |
| `app/dependencies.py` | Validates Supabase JWT via async JWKS fetch with 1-hour TTL cache |
| `app/config.py` | `SUPABASE_URL`, `SUPABASE_ISSUER`, `SUPABASE_SERVICE_ROLE_KEY` |

## Implementation Notes

- JWT tokens are issued by Supabase Auth and validated by the backend using Supabase's JWKS endpoint.
- JWKS keys are cached for 1 hour to avoid hitting Supabase on every request while still handling key rotation.
- `POST /auth/profile` is called by the frontend after successful Supabase auth to sync the user's profile into the backend `profiles` table.
- `POST /auth/logout` calls the Supabase Auth Admin API to revoke all sessions for the user.
- The `profiles` table uses the Supabase `auth.users.id` (UUID) as its primary key, establishing a 1:1 relationship.
