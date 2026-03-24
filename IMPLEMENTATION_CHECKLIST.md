# Sign-in/Sign-up API Implementation - Quick Start Checklist

## ✅ Backend Implementation Status

All core authentication features have been implemented. Here's what's ready to use:

### Code Files

- ✅ **app/models/user.py** - User, RefreshToken, VerificationCode models
- ✅ **app/routers/auth.py** - All auth endpoints defined
- ✅ **app/services/auth_service.py** - All business logic implemented
- ✅ **app/schemas/auth.py** - Request/response validation schemas
- ✅ **app/utils/jwt.py** - JWT token creation and validation
- ✅ **app/utils/google_oauth.py** - Google OAuth token verification
- ✅ **app/utils/email.py** - Email sending utility
- ✅ **app/dependencies.py** - JWT authentication dependency
- ✅ **app/config.py** - Settings management (loads from .env)
- ✅ **app/database.py** - Database connection and session management

### API Endpoints (10 Total)

**Public Endpoints:**
- ✅ POST `/auth/signup` - Register with email/password
- ✅ POST `/auth/signin` - Sign in with email/password
- ✅ POST `/auth/google` - Sign in with Google OAuth token
- ✅ POST `/auth/verify-email` - Verify email with 6-digit code
- ✅ POST `/auth/resend-code` - Resend verification code
- ✅ POST `/auth/forgot-pw` - Request password reset
- ✅ POST `/auth/reset-pw` - Reset password with code
- ✅ POST `/auth/refresh-token` - Get new access token

**Protected Endpoints (requires JWT):**
- ✅ GET `/auth/me` - Get current user info
- ✅ POST `/auth/logout` - Logout and revoke tokens

### Features

- ✅ Email/password authentication with bcrypt hashing
- ✅ Google OAuth 2.0 integration
- ✅ Email verification with 6-digit codes (6-minute expiry)
- ✅ Password reset/recovery flow
- ✅ JWT access tokens (30-minute expiry)
- ✅ Refresh tokens (7-day expiry, stored in DB)
- ✅ Token revocation on logout
- ✅ Strong password validation
- ✅ Duplicate email prevention
- ✅ Rate limiting on code resend (30-second cooldown)

---

## 🔧 Setup & Configuration Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

Create `.env` file in project root with:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/whattoeat

# JWT
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Google OAuth (get from Google Cloud Console)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com

# Email (Gmail with app-specific password)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
```

### Step 3: Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project "WhatToEat"
3. Enable Google+ API
4. Go to Credentials → Create OAuth 2.0 Client ID (Web application)
5. Add authorized origins:
   - `http://localhost:3000` (dev)
   - `https://yourdomain.com` (prod)
6. Copy Client ID to `.env` as `GOOGLE_CLIENT_ID`
7. Frontend will use this same Client ID to get ID tokens

### Step 4: Set Up Email (Gmail)

1. Enable 2-step verification on Gmail
2. Create app-specific password: https://myaccount.google.com/apppasswords
3. Save to `.env` as `SMTP_PASSWORD`

### Step 5: Start Database

```bash
# Start PostgreSQL
brew services start postgresql

# Create database
createdb whattoeat
```

### Step 6: Start Backend Server

```bash
python -m uvicorn app.main:app --reload
```

Server runs on `http://localhost:8000`
API docs: `http://localhost:8000/docs`

---

## 📋 Testing the API

### 1. Test Sign-up

```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "name": "Test User"
  }'
```

**Expected Response:**
- Status: 201 Created
- Body contains user ID and message about verification email

### 2. Test Verify Email

Check your email for the 6-digit code, then:

```bash
curl -X POST http://localhost:8000/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "code": "123456"
  }'
```

### 3. Test Sign-in

```bash
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

**Expected Response:**
- Status: 200 OK
- Body contains `token`, `refreshToken`, and user info

### 4. Test Protected Endpoint

Use the token from sign-in response:

```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 5. Test Google OAuth

```bash
curl -X POST http://localhost:8000/auth/google \
  -H "Content-Type: application/json" \
  -d '{
    "idToken": "GOOGLE_ID_TOKEN_FROM_CLIENT"
  }'
```

---

## 🎯 Frontend Integration

### React Example

```javascript
// Install required packages
npm install @react-oauth/google

// In your app.js
import { GoogleOAuthProvider } from '@react-oauth/google';

<GoogleOAuthProvider clientId={process.env.REACT_APP_GOOGLE_CLIENT_ID}>
  <YourApp />
</GoogleOAuthProvider>

// In your login component
import { GoogleLogin } from '@react-oauth/google';

<GoogleLogin
  onSuccess={(credentialResponse) => {
    // Send to backend
    fetch('http://localhost:8000/auth/google', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ idToken: credentialResponse.credential })
    })
    .then(res => res.json())
    .then(data => {
      localStorage.setItem('accessToken', data.token);
      localStorage.setItem('refreshToken', data.refreshToken);
      // Redirect to dashboard
    });
  }}
/>
```

### Making Authenticated Requests

```javascript
async function fetchWithAuth(endpoint, options = {}) {
  const token = localStorage.getItem('accessToken');
  
  const response = await fetch(`http://localhost:8000${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers
    }
  });

  if (response.status === 401) {
    // Refresh token
    const refreshToken = localStorage.getItem('refreshToken');
    const refresh = await fetch('http://localhost:8000/auth/refresh-token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refreshToken })
    });
    
    if (refresh.ok) {
      const data = await refresh.json();
      localStorage.setItem('accessToken', data.token);
      localStorage.setItem('refreshToken', data.refreshToken);
      return fetchWithAuth(endpoint, options); // Retry
    } else {
      window.location.href = '/login'; // Redirect to login
    }
  }

  return response;
}
```

---

## 📊 Database Schema

The following tables are automatically created on first startup:

```
users
├── id (UUID, primary key)
├── email (unique, indexed)
├── name
├── password_hash (nullable for OAuth users)
├── provider (email | google)
├── is_verified (boolean)
├── created_at
└── updated_at

refresh_tokens
├── id (primary key)
├── user_id (foreign key → users.id)
├── token (unique)
├── is_revoked (boolean)
├── created_at
└── expires_at

verification_codes
├── id (primary key)
├── email (indexed)
├── code (6-digit string)
├── code_type (signup | reset)
├── created_at
└── expires_at
```

---

## 🔐 Security Features

✅ **Password Security**
- Bcrypt hashing with automatic salt
- Minimum 8 characters
- Requires: uppercase, lowercase, digit, special character

✅ **Token Security**
- JWT tokens signed with secret key
- Access tokens short-lived (30 min)
- Refresh tokens longer-lived (7 days)
- Tokens revoked on logout
- Refresh tokens stored in database

✅ **Email Security**
- STARTTLS encryption
- Codes expire after 6 minutes
- Rate limiting on resend (30 sec cooldown)

✅ **Google OAuth Security**
- Server-side token validation
- Token signature verified with Google
- No sensitive data stored locally

---

## ⚠️ Common Issues & Solutions

### "Invalid Google token"
- Check `GOOGLE_CLIENT_ID` in `.env`
- Verify frontend is using same Client ID
- Check token hasn't expired

### "Email not sending"
- Enable Gmail 2-step verification
- Generate app-specific password
- Check `SMTP_USER` and `SMTP_PASSWORD` in `.env`
- Verify SMTP credentials

### "Database connection error"
- Start PostgreSQL: `brew services start postgresql`
- Check `DATABASE_URL` in `.env`
- Verify database exists: `createdb whattoeat`

### "Token invalid" in protected endpoint
- Check token includes "Bearer " prefix
- Verify token hasn't expired
- Use refresh token if expired

---

## 📚 Documentation

- **[AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md)** - Complete guide with examples
- **[api/auth/README.md](api/auth/README.md)** - API overview and endpoints
- **[api/auth/signin.md](api/auth/signin.md)** - Sign-in endpoint details
- **[api/auth/signup.md](api/auth/signup.md)** - Sign-up endpoint details
- **[api/auth/google.md](api/auth/google.md)** - Google OAuth endpoint details

---

## 🚀 Production Deployment

### Pre-deployment Checklist

- [ ] Update `JWT_SECRET_KEY` to strong random string
- [ ] Update `DATABASE_URL` to production database
- [ ] Set up production SMTP credentials (or email service)
- [ ] Update `GOOGLE_CLIENT_ID` with production app
- [ ] Update frontend origin URLs in Google Cloud Console
- [ ] Enable HTTPS (required for secure cookies)
- [ ] Set up monitoring/logging
- [ ] Implement rate limiting
- [ ] Enable CORS for your domain
- [ ] Test all endpoints in production environment

### Environment Variables for Production

```env
DATABASE_URL=postgresql+asyncpg://user:password@prod-db:5432/whattoeat
JWT_SECRET_KEY=your-long-random-production-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
GOOGLE_CLIENT_ID=your-prod-client-id.apps.googleusercontent.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@yourdomain.com
SMTP_PASSWORD=your-app-specific-password
```

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review [AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md)
3. Check API docs at `http://localhost:8000/docs`
4. Review individual endpoint documentation in `docs/api/auth/`

---

**Status: ✅ Ready to Use**

All code is implemented and tested. Proceed with frontend integration!
