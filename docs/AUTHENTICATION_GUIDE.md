# Sign-in/Sign-up API + Google Authentication - Setup & Integration Guide

## Overview

The WhatToEat Backend provides a complete authentication system with:
- **Email/Password Sign-up & Sign-in** with email verification
- **Google OAuth 2.0** integration for seamless sign-up/sign-in
- **JWT-based session management** with access and refresh tokens
- **Password recovery** with email verification
- **Secure password hashing** using bcrypt

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Configuration](#backend-configuration)
3. [Google OAuth Setup](#google-oauth-setup)
4. [API Endpoints Overview](#api-endpoints-overview)
5. [Authentication Flow](#authentication-flow)
6. [Usage Examples](#usage-examples)
7. [Frontend Integration Example](#frontend-integration-example)
8. [Token Management](#token-management)
9. [Error Handling](#error-handling)

---

## Prerequisites

The backend requires:
- Python 3.9+
- PostgreSQL database
- SMTP server (Gmail recommended)
- Google OAuth credentials

### Install Dependencies

```bash
pip install -r requirements.txt
```

Key packages:
- `fastapi` - Web framework
- `sqlalchemy` - ORM
- `google-auth` - Google OAuth token verification
- `python-jose[cryptography]` - JWT handling
- `passlib[bcrypt]` - Password hashing
- `pydantic[email]` - Data validation

---

## Backend Configuration

### 1. Environment Variables (.env)

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/whattoeat

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
```

### 2. Database Setup

Ensure PostgreSQL is running and accessible:

```bash
# Create the database
createdb whattoeat

# Run the FastAPI app - tables will be created automatically on startup
python -m uvicorn app.main:app --reload
```

---

## Google OAuth Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project: "WhatToEat"
3. Navigate to **APIs & Services** > **Credentials**

### Step 2: Create OAuth 2.0 Consent Screen

1. Click **Consent Screen**
2. Select **External** user type
3. Fill in:
   - **App name**: WhatToEat
   - **User support email**: your-email@gmail.com
   - **Developer contact**: your-email@gmail.com
4. Scopes: Add `openid`, `email`, `profile`
5. Test users: Add your test email

### Step 3: Create OAuth 2.0 Credentials

1. Go to **Credentials** > **Create Credentials** > **OAuth 2.0 Client ID**
2. **Application type**: Web application
3. **Authorized JavaScript origins**: 
   - `http://localhost:3000` (frontend dev)
   - `https://yourdomain.com` (production)
4. **Authorized redirect URIs**:
   - `http://localhost:3000/auth/callback` (frontend dev)
   - `https://yourdomain.com/auth/callback` (production)
5. Copy the **Client ID** and save to `.env` as `GOOGLE_CLIENT_ID`

### Step 4: Download and Store Credentials

```bash
# Optional: Download JSON key file for reference
# Save it securely - don't commit to git
```

---

## API Endpoints Overview

### Authentication Endpoints (No JWT Required)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/auth/signup` | POST | Register new user with email/password |
| `/auth/signin` | POST | Sign in with email/password |
| `/auth/google` | POST | Sign in with Google OAuth token |
| `/auth/verify-email` | POST | Verify email with 6-digit code |
| `/auth/resend-code` | POST | Resend verification code |
| `/auth/forgot-pw` | POST | Request password reset |
| `/auth/reset-pw` | POST | Reset password with code |
| `/auth/refresh-token` | POST | Get new access token |

### Protected Endpoints (JWT Required)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/auth/me` | GET | Get current user profile |
| `/auth/logout` | POST | Logout (revoke tokens) |

---

## Authentication Flow

### Email/Password Sign-up Flow

```
1. User submits email, password, name
   ↓
2. Validate password strength (8 chars, uppercase, lowercase, digit, special)
   ↓
3. Check if email already registered
   ↓
4. Hash password with bcrypt
   ↓
5. Create user account (is_verified = false)
   ↓
6. Generate 6-digit verification code
   ↓
7. Send verification code via email (6 min expiry)
   ↓
8. Return user ID and message
   ↓
9. User receives email with code
   ↓
10. User calls /auth/verify-email with code
    ↓
11. Mark user as verified (is_verified = true)
    ↓
12. Success - Now can sign in
```

### Email/Password Sign-in Flow

```
1. User submits email and password
   ↓
2. Find user by email
   ↓
3. Verify password against hash
   ↓
4. Check if email is verified
   ↓
5. Generate JWT access token (30 min expiry)
   ↓
6. Generate refresh token (7 day expiry)
   ↓
7. Store refresh token in database
   ↓
8. Return tokens and user info
```

### Google OAuth Sign-in/Sign-up Flow

```
1. Frontend calls Google Sign-In API
   ↓
2. User completes Google authentication
   ↓
3. Frontend receives ID token
   ↓
4. Frontend sends ID token to /auth/google
   ↓
5. Backend validates ID token with Google
   ↓
6. Extract email and name from token
   ↓
7. Check if user exists
   ├─ No: Create new user (is_verified = true, provider = "google")
   └─ Yes: Use existing user
   ↓
8. Generate JWT access and refresh tokens
   ↓
9. Store refresh token in database
   ↓
10. Return tokens and user info
```

### Token Refresh Flow

```
1. Frontend detects access token expiring
   ↓
2. Frontend sends refresh token to /auth/refresh-token
   ↓
3. Backend validates refresh token
   ↓
4. Revoke old refresh token
   ↓
5. Generate new access and refresh tokens
   ↓
6. Return new tokens
```

---

## Usage Examples

### 1. Sign Up with Email/Password

**Request:**
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "name": "John Doe"
  }'
```

**Response (201 Created):**
```json
{
  "message": "Account created successfully. Verification code sent to email.",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

### 2. Verify Email

**Request:**
```bash
curl -X POST http://localhost:8000/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "code": "123456"
  }'
```

**Response (200 OK):**
```json
{
  "message": "Email verified successfully"
}
```

### 3. Sign In with Email/Password

**Request:**
```bash
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

### 4. Google OAuth Sign-in

**Request:**
```bash
curl -X POST http://localhost:8000/auth/google \
  -H "Content-Type: application/json" \
  -d '{
    "idToken": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjFiOTRjMjRjN2Q5YTc3Y2Y4ZDRkZjE2OTdjMTY2MDk2M2I0ZGE3ZDEiLCJ0eXAiOiJKV1QifQ..."
  }'
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@gmail.com",
    "name": "Google User"
  }
}
```

### 5. Get Current User Info

**Request:**
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "John Doe"
}
```

### 6. Refresh Access Token

**Request:**
```bash
curl -X POST http://localhost:8000/auth/refresh-token \
  -H "Content-Type: application/json" \
  -d '{
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 7. Logout

**Request:**
```bash
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response (200 OK):**
```json
{
  "message": "Logged out successfully"
}
```

---

## Frontend Integration Example

### React with Google Sign-In

```javascript
import { GoogleLogin } from '@react-oauth/google';

function LoginComponent() {
  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      const response = await fetch('http://localhost:8000/auth/google', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          idToken: credentialResponse.credential
        })
      });

      const data = await response.json();
      
      // Store tokens in localStorage or secure cookie
      localStorage.setItem('accessToken', data.token);
      localStorage.setItem('refreshToken', data.refreshToken);
      localStorage.setItem('user', JSON.stringify(data.user));
      
      // Redirect to dashboard
      window.location.href = '/dashboard';
    } catch (error) {
      console.error('Google login failed:', error);
    }
  };

  return (
    <GoogleLogin
      onSuccess={handleGoogleSuccess}
      onError={() => console.error('Login Failed')}
    />
  );
}
```

### Making Authenticated Requests

```javascript
async function fetchWithAuth(url, options = {}) {
  const token = localStorage.getItem('accessToken');
  
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    }
  });

  if (response.status === 401) {
    // Token expired - refresh it
    const refreshToken = localStorage.getItem('refreshToken');
    const refreshResponse = await fetch('http://localhost:8000/auth/refresh-token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refreshToken })
    });

    if (refreshResponse.ok) {
      const newData = await refreshResponse.json();
      localStorage.setItem('accessToken', newData.token);
      localStorage.setItem('refreshToken', newData.refreshToken);

      // Retry original request with new token
      return fetchWithAuth(url, options);
    } else {
      // Refresh failed - redirect to login
      window.location.href = '/login';
    }
  }

  return response;
}
```

---

## Token Management

### JWT Token Structure

**Access Token:**
```javascript
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",  // User ID
  "email": "user@example.com",
  "exp": 1704067200,                               // Expiry timestamp
  "type": "access"
}
```

**Refresh Token:**
```javascript
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",  // User ID
  "exp": 1704672000,                               // Expiry timestamp
  "type": "refresh"
}
```

### Token Expiration Times

- **Access Token**: 30 minutes
- **Refresh Token**: 7 days
- **Verification Code**: 6 minutes

### Token Storage Best Practices

```javascript
// ✅ Best: HttpOnly secure cookie (server-set)
// Backend should set: Set-Cookie: accessToken=...; HttpOnly; Secure; SameSite=Strict

// ✅ Alternative: In-memory (lost on refresh)
const accessToken = sessionStorage.getItem('token');

// ⚠️ Avoid: localStorage for sensitive tokens
// localStorage.setItem('token', accessToken); // Vulnerable to XSS
```

---

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "detail": "Validation error or invalid input"
}
```

#### 401 Unauthorized
```json
{
  "detail": "Incorrect email or password"
}
```

#### 409 Conflict
```json
{
  "detail": "Email already registered"
}
```

#### 404 Not Found
```json
{
  "detail": "Email not registered"
}
```

#### 429 Too Many Requests
```json
{
  "detail": "Please wait before requesting a new code"
}
```

### Error Response Format

All error responses follow FastAPI's HTTPException format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255),
  provider VARCHAR(50) NOT NULL DEFAULT 'email',
  is_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Refresh Tokens Table
```sql
CREATE TABLE refresh_tokens (
  id SERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  token VARCHAR(500) UNIQUE NOT NULL,
  is_revoked BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

### Verification Codes Table
```sql
CREATE TABLE verification_codes (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL,
  code VARCHAR(6) NOT NULL,
  code_type VARCHAR(20) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

---

## Security Considerations

1. **Password Security**:
   - Minimum 8 characters
   - Must include: uppercase, lowercase, digit, special character
   - Hashed with bcrypt (automatically salted)

2. **Token Security**:
   - JWT tokens signed with secret key
   - Short-lived access tokens (30 min)
   - Longer-lived refresh tokens (7 days)
   - Refresh tokens stored in database and marked revoked on logout

3. **Email Security**:
   - SMTP with STARTTLS encryption
   - Verification codes expire after 6 minutes
   - Rate limiting on code resend (30 second cooldown)

4. **Google OAuth Security**:
   - Server-side token validation
   - Verifies token signature with Google's public keys
   - No credentials stored locally

---

## Running the Server

```bash
# Install dependencies
pip install -r requirements.txt

# Set up .env file with your configuration

# Run development server
python -m uvicorn app.main:app --reload

# Run production server
pm2 start "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000" --name whattoeat-api
```

Server runs on `http://localhost:8000`
API docs available at `http://localhost:8000/docs`

---

## Troubleshooting

### Google OAuth Token Verification Fails

**Issue**: "Invalid or expired Google token"

**Solutions**:
1. Verify `GOOGLE_CLIENT_ID` matches your Google project
2. Check token hasn't expired (usually 1 hour)
3. Ensure token was issued for your client ID
4. Verify internet connection for Google validation

### Email Not Sending

**Issue**: "SMTP error" or empty email

**Solutions**:
1. Enable 2-step verification for Gmail
2. Generate app-specific password: https://myaccount.google.com/apppasswords
3. Verify SMTP credentials in `.env`
4. Check firewall/provider doesn't block SMTP port 587
5. For Gmail: Allow "Less secure app access" if not using app password

### Database Connection Error

**Issue**: "could not connect to server"

**Solutions**:
1. Ensure PostgreSQL is running: `brew services start postgresql`
2. Verify `DATABASE_URL` in `.env`
3. Check database exists: `psql -l | grep whattoeat`
4. Verify credentials (username, password, host, port)

---

## Next Steps

1. ✅ Set up Google OAuth credentials
2. ✅ Configure `.env` with your values
3. ✅ Start PostgreSQL
4. ✅ Run `python -m uvicorn app.main:app --reload`
5. ✅ Test endpoints with provided curl examples
6. ✅ Integrate with frontend
7. ✅ Deploy to production

For detailed API documentation, see individual files in `docs/api/auth/`.
