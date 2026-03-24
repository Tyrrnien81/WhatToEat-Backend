# Authentication System - Code Architecture & File Structure

## 📁 Project Structure

```
WhatToEat-Backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Settings from .env
│   ├── database.py             # SQLAlchemy setup
│   ├── dependencies.py         # Shared dependencies
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py             # User, RefreshToken, VerificationCode models
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── auth.py             # Request/response Pydantic models
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   └── auth.py             # Auth endpoints
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── auth_service.py     # Business logic
│   │
│   └── utils/
│       ├── __init__.py
│       ├── jwt.py              # JWT token operations
│       ├── google_oauth.py      # Google OAuth verification
│       └── email.py            # Email sending
│
├── docs/
│   ├── AUTHENTICATION_GUIDE.md  # 📖 Complete auth guide
│   └── api/auth/
│       ├── README.md           # Endpoint overview
│       ├── signin.md           # Sign-in documentation
│       ├── signup.md           # Sign-up documentation
│       ├── google.md           # Google OAuth documentation
│       ├── verify-email.md
│       ├── resend-code.md
│       ├── forgot-pw.md
│       ├── reset-pw.md
│       ├── refresh-token.md
│       ├── logout.md
│       └── me.md
│
├── IMPLEMENTATION_CHECKLIST.md  # 📋 Quick start guide
├── .env                        # Environment variables
└── requirements.txt            # Python dependencies
```

---

## 🔄 Data Flow Diagram

### Sign-up Flow

```
Frontend (User submits form)
    ↓
POST /auth/signup
    ↓
auth.py (router)
    ↓
auth_service.sign_up()
    ├→ Check if email exists (User model)
    ├→ Hash password (passlib)
    ├→ Create User record (database)
    ├→ Generate verification code (6-digit)
    ├→ Create VerificationCode record (6-min expiry)
    ├→ Send email (email.py)
    └→ Return user info
    ↓
Frontend (stores user info, prompts to verify)
```

### Sign-in Flow

```
Frontend (email + password)
    ↓
POST /auth/signin
    ↓
auth.py (router)
    ↓
auth_service.sign_in()
    ├→ Find user by email (database)
    ├→ Verify password (passlib.verify)
    ├→ Check is_verified flag
    ├→ Create JWT access token (jwt.py)
    ├→ Create JWT refresh token (jwt.py)
    ├→ Store refresh token in database
    └→ Return tokens + user info
    ↓
Frontend (stores tokens in secure storage)
```

### Google OAuth Flow

```
Frontend (clicks Google Sign-In button)
    ↓
Google Sign-In API (user completes challenge)
    ↓
Frontend receives ID token
    ↓
POST /auth/google (with idToken)
    ↓
auth.py (router)
    ↓
auth_service.google_auth()
    ├→ Verify token with Google (google_oauth.py)
    ├→ Extract email, name, google_id
    ├→ Find/create user (provider = "google", is_verified = true)
    ├→ Create JWT tokens (jwt.py)
    ├→ Store refresh token (database)
    └→ Return tokens + user info
    ↓
Frontend (stores tokens, redirects to dashboard)
```

### Protected Endpoint Flow

```
Frontend (with Authorization header)
    ↓
GET /auth/me
    ↓
dependencies.get_current_user()
    ├→ Extract token from header
    ├→ Decode JWT (jwt.py)
    ├→ Validate token type = "access"
    └→ Extract user_id
    ↓
auth.py (router)
    ↓
auth_service.get_me()
    └→ Fetch user from database
    ↓
Frontend (receives user info)
```

---

## 📝 File Descriptions

### `app/main.py`
**Purpose**: FastAPI application entry point

**Key Components**:
- Creates FastAPI app with lifespan context manager
- Creates database tables on startup
- Includes auth router
- Defines root endpoint

**Key Functions**:
- `lifespan()` - Creates database tables on app startup
- `root()` - Test endpoint

---

### `app/config.py`
**Purpose**: Settings management

**Key Components**:
- Loads environment variables from `.env` using Pydantic Settings
- Defines all configuration constants

**Required Environment Variables**:
- DATABASE_URL
- JWT_SECRET_KEY
- JWT_ALGORITHM
- ACCESS_TOKEN_EXPIRE_MINUTES
- REFRESH_TOKEN_EXPIRE_DAYS
- GOOGLE_CLIENT_ID
- SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

---

### `app/database.py`
**Purpose**: Database connection and session management

**Key Components**:
- AsyncEngine for async database operations
- AsyncSessionMaker for session creation
- Base class for SQLAlchemy models

**Key Functions**:
- `get_db()` - Dependency that yields database session

---

### `app/dependencies.py`
**Purpose**: Shared FastAPI dependencies

**Key Components**:
- HTTPBearer security scheme for JWT validation

**Key Functions**:
- `get_current_user()` - Dependency that validates JWT and returns user_id

---

### `app/models/user.py`
**Purpose**: SQLAlchemy database models

**Models**:

**User**
- Represents a registered user
- Fields: id, email (unique), name, password_hash, provider, is_verified, timestamps
- Relationships: refresh_tokens

**RefreshToken**
- Stores refresh tokens for session management
- Fields: id, user_id, token (unique), is_revoked, created_at, expires_at
- Relationships: user

**VerificationCode**
- Stores 6-digit codes for email verification and password reset
- Fields: id, email, code, code_type, created_at, expires_at
- No relationships

---

### `app/schemas/auth.py`
**Purpose**: Pydantic models for request/response validation

**Request Schemas**:
- `SignInRequest` - email, password
- `SignUpRequest` - email, password, name (with validators)
- `GoogleAuthRequest` - idToken
- `ForgotPasswordRequest` - email
- `VerifyEmailRequest` - email, code
- `ResendCodeRequest` - email
- `ResetPasswordRequest` - email, code, newPassword
- `RefreshTokenRequest` - refreshToken

**Response Schemas**:
- `UserResponse` - id, email, name
- `AuthResponse` - token, refreshToken, user
- `TokenRefreshResponse` - token, refreshToken
- `MessageResponse` - message
- `SignUpResponse` - message, user

**Validators**:
- Password strength validation (8+ chars, uppercase, lowercase, digit, special)

---

### `app/routers/auth.py`
**Purpose**: HTTP endpoint definitions

**Endpoints**:

**Authentication (Public)**:
- `POST /auth/signin` → sign_in()
- `POST /auth/signup` → signup()
- `POST /auth/google` → google_login()

**Email Verification (Public)**:
- `POST /auth/verify-email` → verify_email()
- `POST /auth/resend-code` → resend_code()

**Password Recovery (Public)**:
- `POST /auth/forgot-pw` → forgot_password()
- `POST /auth/reset-pw` → reset_password()

**Token Management (Public)**:
- `POST /auth/refresh-token` → refresh_token()

**Session Management (Protected)**:
- `POST /auth/logout` → logout()
- `GET /auth/me` → me()

---

### `app/services/auth_service.py`
**Purpose**: Business logic for authentication

**Key Functions**:

**Authentication**:
- `sign_in()` - Authenticate user with email/password
- `sign_up()` - Register new user
- `google_auth()` - Authenticate via Google OAuth

**Email Verification**:
- `verify_email()` - Mark user as verified
- `resend_code()` - Resend verification code (with cooldown)

**Password Recovery**:
- `forgot_password()` - Send reset code
- `reset_password()` - Reset password with code

**Token Management**:
- `refresh_access_token()` - Get new access token
- `logout()` - Revoke all refresh tokens

**User Info**:
- `get_me()` - Get current user info

**Helpers**:
- `_hash_password()` - Hash password with bcrypt
- `_verify_password()` - Verify password against hash
- `_generate_code()` - Generate 6-digit code

---

### `app/utils/jwt.py`
**Purpose**: JWT token creation and validation

**Key Functions**:
- `create_access_token()` - Create JWT access token (30-min expiry)
- `create_refresh_token()` - Create JWT refresh token (7-day expiry)
- `decode_token()` - Decode and validate JWT

**Token Payload**:
```javascript
{
  "sub": "user_id (UUID)",    // Subject
  "email": "user@example.com", // Email (access token only)
  "exp": 1704067200,          // Expiration timestamp
  "type": "access|refresh"    // Token type
}
```

---

### `app/utils/google_oauth.py`
**Purpose**: Google OAuth token verification

**Key Functions**:
- `verify_google_token()` - Validate Google ID token and extract user info

**Returns**:
```python
{
  "email": "user@gmail.com",
  "name": "User Name",
  "google_id": "google_sub_id"
}
```

---

### `app/utils/email.py`
**Purpose**: Email sending

**Key Functions**:
- `send_verification_email()` - Send 6-digit code via SMTP

**Configuration**:
- Uses Gmail SMTP (smtp.gmail.com:587)
- STARTTLS encryption
- Credentials from .env

---

## 🔐 Security Layers

### Layer 1: Password Security
```
User Input
    ↓
Pydantic Validator (password strength)
    ↓
Passlib.hash_password() (bcrypt)
    ↓
Database (hash only, never plaintext)
```

### Layer 2: Token Security
```
User Authentication
    ↓
JWT Creation with secret key
    ↓
Token signed and hardcoded expiry
    ↓
Frontend storage (preferably HttpOnly cookie)
    ↓
Authorization header on each request
    ↓
JWT decode and validation
```

### Layer 3: Session Security
```
Refresh Token Issued
    ↓
Stored in database with expiry
    ↓
Token linked to user_id
    ↓
Marked as revoked on logout
    ↓
Only non-revoked tokens valid for refresh
```

### Layer 4: Email Security
```
Verification Code Generated
    ↓
Sent via SMTP with TLS
    ↓
Stored in database with 6-minute expiry
    ↓
Rate limited (30-second cooldown on resend)
    ↓
Consumed (deleted) after verification
```

---

## 🔌 Integration Points

### With Frontend
- REST API via HTTP/HTTPS
- JSON request/response format
- Bearer token authentication
- CORS configuration (see FastAPI docs)

### With Database
- PostgreSQL via SQLAlchemy ORM
- Async operations with asyncpg
- Automatic table creation on startup

### With Email Provider
- Gmail SMTP
- STARTTLS encryption
- App-specific passwords

### With Google OAuth
- Server-side token validation
- Uses google-auth library
- No client secret required (public web app)

---

## 🚀 Deployment Architecture

```
User Client (Web/Mobile)
        ↓
    HTTPS
        ↓
Frontend (React/Vue)
    ↓ API Calls ↓
    FastAPI Server (uvicorn)
        ├→ in-memory: JWT validation
        ├→ network: Google API verification
        ├→ database: PostgreSQL
        └→ network: Gmail SMTP
```

---

## 📊 Database Entity Relationships

```
┌─────────────┐
│   users     │
├─────────────┤
│ id (PK)     │
│ email (UQ)  │
│ name        │
│ password..  │
│ provider    │
│ is_verified │
└──────┬──────┘
       │ 1
       │
       │ Many
       ↓
┌──────────────────────┐
│  refresh_tokens      │
├──────────────────────┤
│ id (PK)              │
│ user_id (FK) ────────┘
│ token (UQ)
│ is_revoked
│ created_at
│ expires_at
└──────────────────────┘

┌──────────────────────┐
│ verification_codes   │
├──────────────────────┤
│ id (PK)              │
│ email                │
│ code                 │
│ code_type            │
│ created_at           │
│ expires_at           │
└──────────────────────┘
```

---

## 🧪 Testing Strategy

### Unit Tests
- Password hashing/verification
- JWT encode/decode
- Code generation
- Email formatting

### Integration Tests
- Sign-up flow (email sent)
- Sign-in with verification
- Google OAuth flow
- Token refresh
- Protected endpoint access

### E2E Tests
- Complete user journey (sign-up → verify → sign-in)
- Google OAuth flow
- Password recovery
- Token expiration and refresh

---

## 📈 Performance Considerations

### Database Optimization
- Email indexed for fast user lookups
- Refresh token lookups optimized (unique constraint)
- Verification codes indexed by email for quick searches

### Token Optimization
- JWT tokens are self-contained (no DB lookup on validate)
- Refresh tokens are short-lived and revoked on logout
- Verification codes expire after 6 minutes (auto-cleanup)

### Scalability
- Async operations throughout (asyncio)
- Connection pooling (SQLAlchemy)
- Stateless API design (scales horizontally)

---

## 🔮 Future Enhancements

Potential additions beyond current implementation:
- [ ] Two-factor authentication (2FA)
- [ ] Social login (GitHub, Facebook, etc.)
- [ ] Account linking (combine OAuth accounts)
- [ ] Premium features (passwordless login)
- [ ] Audit logging (track auth actions)
- [ ] IP-based security (geo-blocking, etc.)
- [ ] API key authentication
- [ ] Role-based access control (RBAC)
- [ ] Email change verification
- [ ] Account recovery codes

---

## 📖 Documentation Structure

**For Users/Developers**:
- `IMPLEMENTATION_CHECKLIST.md` - Quick start guide ← Start here!
- `docs/AUTHENTICATION_GUIDE.md` - Complete guide with examples
- `docs/api/auth/README.md` - Endpoint overview

**For API Consumers**:
- `docs/api/auth/` - Individual endpoint documentation
- `http://localhost:8000/docs` - Auto-generated Swagger UI

**For Maintainers**:
- This file - Code architecture and structure
- Source code comments and docstrings
- Git commit history

---

**This architecture supports secure, scalable authentication for the WhatToEat platform.**
