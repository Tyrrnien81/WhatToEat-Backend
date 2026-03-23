# 1. User Service (Authentication)

Handles user sign-in, sign-up, password recovery, Google login, email verification, and session management.

## Authentication Header

All endpoints marked **JWT Required = Yes** must include:

```http
Authorization: Bearer <JWT token>
```

## Endpoints Overview

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| POST | `/auth/signin` | Sign in with email and password; returns a JWT token | No |
| POST | `/auth/signup` | Register a new user account | No |
| POST | `/auth/google` | Sign in using Google OAuth | No |
| POST | `/auth/forgot-pw` | Send a verification code to the user's email for password reset | No |
| POST | `/auth/verify-email` | Verify user's email address with a 6-digit code | No |
| POST | `/auth/resend-code` | Resend verification code (30s cooldown) | No |
| POST | `/auth/reset-pw` | Reset the password after email verification | No |
| POST | `/auth/refresh-token` | Refresh an expired JWT token | No |
| POST | `/auth/logout` | Log out the current user (from Settings) | Yes |
| GET | `/auth/me` | Retrieve the current user's info from the JWT | Yes |

---

## Endpoint Details

### `POST /auth/signin`

Sign in with email and password.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "yourPassword123"
}
```

**Response (`200 OK`):**

```json
{
  "token": "<JWT token>",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**Error Responses:**
- `400 Bad Request` — Missing or invalid fields
- `401 Unauthorized` — Incorrect email or password

---

### `POST /auth/signup`

Register a new user account. A 6-digit verification code will be sent to the provided email.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "yourPassword123",
  "name": "John Doe"
}
```

**Response (`201 Created`):**

```json
{
  "message": "Account created successfully. Verification code sent to email.",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**Error Responses:**
- `400 Bad Request` — Missing or invalid fields (password must be 8+ chars with upper, lower, digit, special char)
- `409 Conflict` — Email already registered

---

### `POST /auth/google`

Authenticate using a Google OAuth ID token. Creates a new user if the Google account is not yet registered.

**Request Body:**

```json
{
  "idToken": "<Google OAuth ID token>"
}
```

**Response (`200 OK`):**

```json
{
  "token": "<JWT token>",
  "user": {
    "id": "uuid",
    "email": "user@gmail.com",
    "name": "John Doe"
  }
}
```

**Error Responses:**
- `401 Unauthorized` — Invalid or expired Google token

---

### `POST /auth/forgot-pw`

Send a 6-digit verification code to the user's email to initiate password reset.

**Request Body:**

```json
{
  "email": "user@example.com"
}
```

**Response (`200 OK`):**

```json
{
  "message": "Verification code sent to email"
}
```

**Error Responses:**
- `404 Not Found` — Email not registered

---

### `POST /auth/verify-email`

Verify the user's email address using a 6-digit verification code. Used during signup and password reset flows. Code expires after approximately 6 minutes.

**Request Body:**

```json
{
  "email": "user@example.com",
  "code": "123456"
}
```

**Response (`200 OK`):**

```json
{
  "message": "Email verified successfully"
}
```

**Error Responses:**
- `400 Bad Request` — Invalid or expired verification code
- `404 Not Found` — Email not registered

---

### `POST /auth/resend-code`

Resend a verification code to the user's email. Enforces a 30-second cooldown between resend attempts.

**Request Body:**

```json
{
  "email": "user@example.com"
}
```

**Response (`200 OK`):**

```json
{
  "message": "Verification code resent to email"
}
```

**Error Responses:**
- `404 Not Found` — Email not registered
- `429 Too Many Requests` — Resend cooldown has not elapsed (30 seconds)

---

### `POST /auth/reset-pw`

Reset the user's password after email verification.

**Request Body:**

```json
{
  "email": "user@example.com",
  "code": "123456",
  "newPassword": "newSecurePassword456"
}
```

**Response (`200 OK`):**

```json
{
  "message": "Password reset successfully"
}
```

**Error Responses:**
- `400 Bad Request` — Invalid or expired verification code, or password does not meet requirements
- `404 Not Found` — Email not registered

---

### `POST /auth/refresh-token`

Refresh an expired JWT token. Used on app launch and when API calls return `401` to maintain seamless user sessions.

**Request Body:**

```json
{
  "refreshToken": "<refresh token>"
}
```

**Response (`200 OK`):**

```json
{
  "token": "<new JWT token>",
  "refreshToken": "<new refresh token>"
}
```

**Error Responses:**
- `401 Unauthorized` — Refresh token is invalid or expired

---

### `POST /auth/logout`

Log out the current user. Accessed from the Settings screen, not the home screen. Invalidates the current session.

**Headers:** `Authorization: Bearer <JWT token>`

**Request Body:** None

**Response (`200 OK`):**

```json
{
  "message": "Logged out successfully"
}
```

**Error Responses:**
- `401 Unauthorized` — Invalid or missing token

---

### `GET /auth/me`

Retrieve the currently authenticated user's information from the JWT.

**Headers:** `Authorization: Bearer <JWT token>`

**Request Body:** None

**Response (`200 OK`):**

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe"
}
```

**Error Responses:**
- `401 Unauthorized` — Invalid or missing token

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
│   └── user.py              # User, UserPreferences, OTPCodes models
└── utils/
    ├── jwt.py               # JWT encode/decode helpers
    └── google_oauth.py      # Google OAuth token validation
```

| File | Responsibility |
| --- | --- |
| `app/routers/auth.py` | Defines all `/auth/*` FastAPI route handlers |
| `app/schemas/auth.py` | Pydantic models for request bodies and response shapes (e.g., `SigninRequest`, `SignupRequest`, `TokenResponse`) |
| `app/services/auth_service.py` | Core logic: password hashing (bcrypt), OTP generation/validation, user creation, Google token verification |
| `app/models/user.py` | ORM models for `users`, `user_preferences`, `otp_codes` tables |
| `app/utils/jwt.py` | JWT token creation (access + refresh) and decoding/validation |
| `app/utils/google_oauth.py` | Validates Google OAuth ID tokens and extracts user info |
| `app/dependencies.py` | `get_current_user` dependency that extracts and validates JWT from `Authorization` header |
| `app/config.py` | Environment-based settings: `SECRET_KEY`, `JWT_EXPIRY`, `DATABASE_URL`, `GOOGLE_CLIENT_ID`, etc. |
