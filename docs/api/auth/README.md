# Authentication Service

Handles user registration, email/password sign-in, Google OAuth, email verification, password recovery, token refresh, and session management.

## Authentication Header

All endpoints marked **JWT Required = Yes** must include:

```http
Authorization: Bearer <JWT token>
```

## Endpoints

| Method | Endpoint | File | Description | JWT Required |
| --- | --- | --- | --- | --- |
| POST | `/auth/signin` | [signin.md](signin.md) | Authenticate with email and password | No |
| POST | `/auth/signup` | [signup.md](signup.md) | Register a new user account | No |
| POST | `/auth/google` | [google.md](google.md) | Authenticate via Google OAuth | No |
| POST | `/auth/forgot-pw` | [forgot-pw.md](forgot-pw.md) | Send password reset verification code | No |
| POST | `/auth/verify-email` | [verify-email.md](verify-email.md) | Verify email with 6-digit code | No |
| POST | `/auth/resend-code` | [resend-code.md](resend-code.md) | Resend verification code | No |
| POST | `/auth/reset-pw` | [reset-pw.md](reset-pw.md) | Reset password after verification | No |
| POST | `/auth/refresh-token` | [refresh-token.md](refresh-token.md) | Refresh an expired JWT | No |
| POST | `/auth/logout` | [logout.md](logout.md) | Invalidate current session | Yes |
| GET | `/auth/me` | [me.md](me.md) | Get current user info | Yes |

## Implementation Notes

- JWT access token expires after 24 hours; refresh tokens are issued on sign-in and Google auth, with token rotation on refresh
- Password requirements: minimum 8 characters, must include uppercase, lowercase, digit, and special character
- Email verification uses a 6-digit code that expires after ~6 minutes
- Google OAuth validates the ID token server-side and auto-creates the user if not registered
- Password hashing uses bcrypt
- Logout revokes all refresh tokens for the user server-side

---

## Project Structure (Auth)

The following files handle auth implementation:

```
app/
├── main.py                  # FastAPI app entry point
├── config.py                # Settings (env vars, DB, JWT secrets)
├── dependencies.py          # Shared FastAPI dependencies (auth, db session)
├── routers/
│   └── auth.py              # /auth/* endpoint definitions
├── schemas/
│   └── auth.py              # Pydantic request/response schemas
├── services/
│   └── auth_service.py      # Auth business logic
├── models/
│   └── user.py              # User, VerificationCode, RefreshToken models
└── utils/
    ├── jwt.py               # JWT encode/decode helpers
    ├── email.py             # SMTP verification email sender
    └── google_oauth.py      # Google OAuth token validation
```

| File | Responsibility |
| --- | --- |
| `app/routers/auth.py` | Defines all `/auth/*` FastAPI route handlers |
| `app/schemas/auth.py` | Pydantic models for request bodies and response shapes (e.g., `SignInRequest`, `SignUpRequest`, `AuthResponse`) |
| `app/services/auth_service.py` | Core logic: password hashing (bcrypt), verification code generation/validation, user creation, Google token verification |
| `app/models/user.py` | ORM models for `users`, `verification_codes`, `refresh_tokens` tables |
| `app/utils/jwt.py` | JWT token creation (access + refresh) and decoding/validation |
| `app/utils/google_oauth.py` | Validates Google OAuth ID tokens and extracts user info |
| `app/dependencies.py` | `get_current_user` dependency that extracts and validates JWT from `Authorization` header |
| `app/config.py` | Environment-based settings: `SECRET_KEY`, `JWT_EXPIRY`, `DATABASE_URL`, `GOOGLE_CLIENT_ID`, etc. |
