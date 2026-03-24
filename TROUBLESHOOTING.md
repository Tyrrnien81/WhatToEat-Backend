# Authentication System - Troubleshooting Guide & FAQ

## 🔧 Troubleshooting by Error Message

### "SQLALCHEMY Error: could not translate type annotation"

**Cause**: SQLAlchemy model type imports or annotations are incorrect

**Solution**:
1. Verify imports in `app/models/user.py`:
```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, DateTime, String, UUID, ForeignKey
```

2. Ensure using new-style annotations:
```python
# ✅ Correct
id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
email: Mapped[str] = mapped_column(String(255), unique=True)

# ❌ Wrong
Column(UUID(as_uuid=True), primary_key=True)
```

---

### "google.auth.exceptions.MalformedError: Malformed token"

**Cause**: Google ID token is invalid, expired, or for wrong client

**Solutions**:

1. **Wrong Client ID**
```python
# ❌ This ID doesn't match frontend's Google Sign-In client ID
GOOGLE_CLIENT_ID=abc123.apps.googleusercontent.com

# ✅ Use the exact Client ID from Google Cloud Console
GOOGLE_CLIENT_ID=550e8400e29b41d4a716446655440000.apps.googleusercontent.com
```

2. **Token Expired**
```python
# Google ID tokens expire after ~1 hour
# Frontend must get fresh token before sending to backend
# Check console for token timestamp
```

3. **Token for Wrong Audience**
```python
# Frontend Google Sign-In must use same Client ID as backend
# react example:
<GoogleLogin
  clientId={process.env.REACT_APP_GOOGLE_CLIENT_ID}
  // must match GOOGLE_CLIENT_ID in .env
/>
```

---

### "SMTPAuthenticationError: 535 5.7.8 Username and Password not accepted"

**Cause**: SMTP credentials are wrong

**Solutions**:

1. **Using Gmail Account Password (Wrong)**
```env
# ❌ Don't use your Gmail password
SMTP_PASSWORD=your-actual-gmail-password

# ✅ Use app-specific password instead
SMTP_PASSWORD=abcd efgh ijkl mnop
```

2. **Fix**: Generate app password:
   1. Go to https://myaccount.google.com/apppasswords
   2. Select "Mail" and "Windows Computer"
   3. Copy the generated password (16 characters with spaces)
   4. Update `.env`

3. **Common Mistakes**:
```env
# ❌ Missing @ symbol
SMTP_USER=your-email-gmail.com

# ✅ Include @ symbol
SMTP_USER=your-email@gmail.com

# ❌ Wrong hostname
SMTP_HOST=gmail.com

# ✅ Correct hostname
SMTP_HOST=smtp.gmail.com

# ❌ Wrong port
SMTP_PORT=465  # (SSL)

# ✅ Correct port for TLS
SMTP_PORT=587
```

---

### "psycopg2.OperationalError: could not translate host name to address"

**Cause**: PostgreSQL server not running or wrong connection string

**Solutions**:

1. **Start PostgreSQL**:
```bash
# macOS
brew services start postgresql
brew services list  # verify running

# Linux
sudo systemctl start postgresql

# Docker
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres
```

2. **Verify Connection String**:
```env
# ❌ Missing protocol
DATABASE_URL=postgres://user:pass@localhost:5432/db

# ✅ With asyncpg protocol
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
```

3. **Check Port and Host**:
```bash
# Test connection
psql -U postgres -h localhost -p 5432

# If default port changed:
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5433/db
```

4. **Credentials**:
```env
# Default PostgreSQL credentials
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/whattoeat

# Check if password is set:
# psql -U postgres -W   (then enter password)
```

---

### "NoSuchTableError: users"

**Cause**: Tables not created in database

**Solutions**:

1. **Restart server** (tables created on startup):
```bash
python -m uvicorn app.main:app --reload
```

2. **Create database first**:
```bash
createdb whattoeat
# Then restart server
```

3. **Check database URL**:
```bash
# Verify database exists
psql -l | grep whattoeat

# If not exists:
createdb whattoeat
```

---

### "ValueError: Password must contain an uppercase letter"

**Cause**: Password doesn't meet strength requirements

**Solution**: Password requirements are:
- Minimum 8 characters
- Must include uppercase letter (A-Z)
- Must include lowercase letter (a-z)
- Must include digit (0-9)
- Must include special character (!@#$%^&*(),.?":{}|<>)

**Examples**:
```
✅ ValidPassword123!
✅ MySecure@Pass2024
✅ Test#1Password

❌ password         (no uppercase, no digit, no special char)
❌ PASSWORD123!    (no lowercase)
❌ password123!    (no uppercase)
❌ Password!       (no digit)
❌ Password123     (no special char)
```

---

### "HTTPException: Email already registered"

**Cause**: Trying to sign up with email that already exists

**Solutions**:

1. **Use different email**:
```bash
# Sign up with new email
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "new-email@example.com",
    "password": "ValidPass123!",
    "name": "John Doe"
  }'
```

2. **Forgot password instead**:
```bash
# If you already have an account
curl -X POST http://localhost:8000/auth/forgot-pw \
  -H "Content-Type: application/json" \
  -d '{"email": "existing@example.com"}'
```

3. **Clear database** (development only):
```bash
# Drop and recreate database
dropdb whattoeat
createdb whattoeat
# Restart server
```

---

### "HTTPException: Invalid or expired verification code"

**Cause**: Code is wrong, expired, or already used

**Solutions**:

1. **Check code expiry** (6 minutes):
```bash
# Code must be used within 6 minutes of sending
# If expired, resend:
curl -X POST http://localhost:8000/auth/resend-code \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

2. **Check for typos**:
   - Code is 6 digits (e.g., "123456")
   - Copy from email carefully

3. **Code already used**:
   - Can't reuse same code
   - Request new one with resend-code endpoint

4. **Check email received**:
```python
# If email not received, check SMTP settings
# Temporary workaround: check server logs for code
# Look for "Verification code sent"
```

---

### "HTTPException: Invalid or expired refresh token"

**Cause**: Refresh token is invalid, expired, or revoked

**Solutions**:

1. **Token Expired** (7 days):
```bash
# Refresh tokens expire after 7 days
# User must sign in again
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "ValidPass123!"
  }'
```

2. **Token Revoked**:
```bash
# Happens after logout
# User must sign in again
```

3. **Token Tampered**:
```bash
# If token was modified or invalid
# Can't be used - must sign in again
```

---

### "HTTPException: Please wait before requesting a new code"

**Cause**: Code resend rate limit (30 seconds)

**Solution**: Wait at least 30 seconds before requesting another code

```bash
# ❌ This will fail if last request was <30 seconds ago
curl -X POST http://localhost:8000/auth/resend-code ...

# ✅ Should work after 30 second wait
sleep 30
curl -X POST http://localhost:8000/auth/resend-code ...
```

---

### "HTTPException: Email not verified"

**Cause**: User signed up but didn't verify email

**Solution**: Complete email verification first

```bash
# 1. Check if email in inbox, spam, or promotions
# 2. If not received, resend code:
curl -X POST http://localhost:8000/auth/resend-code \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# 3. Get code from email
# 4. Verify:
curl -X POST http://localhost:8000/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "code": "123456"
  }'

# 5. Now can sign in
curl -X POST http://localhost:8000/auth/signin ...
```

---

### "CORS error: Access to XMLHttpRequest blocked"

**Cause**: Frontend and backend on different origins without CORS headers

**Solution**: Configure CORS in FastAPI

```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React dev
        "http://localhost:5173",      # Vite dev
        "https://yourdomain.com",     # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## ❓ Frequently Asked Questions

### Q: How do I store JWTs securely?

**A**: Best practices in order:

1. **HttpOnly Secure Cookies** (Most Secure)
```javascript
// Backend sets cookie automatically
// Browser includes in all requests automatically
// JS cannot access (protected from XSS)
// Requires HTTPS in production
```

2. **Session Storage** (Good)
```javascript
// Lost on browser refresh
// Not vulnerable to XSS as much
const token = sessionStorage.getItem('token');
```

3. **RAM Variable** (Best for security)
```javascript
// Lost on page refresh
// Most secure but forces re-login
let token = accessTokenFromLogin;
```

4. **⚠️ LocalStorage** (Avoid)
```javascript
// ❌ Vulnerable to XSS attacks
// ❌ Persists across sessions
localStorage.setItem('token', accessToken);
```

---

### Q: What should Google Client ID be?

**A**: 

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Find your project
3. Go to Credentials
4. Copy "Client ID" (not Client Secret)
5. It looks like: `550e8400e29b41d4.apps.googleusercontent.com`
6. Add to `.env`:
```env
GOOGLE_CLIENT_ID=550e8400e29b41d4.apps.googleusercontent.com
```
7. Frontend also uses same Client ID in `<GoogleLogin clientId={...} />`

---

### Q: How long do tokens last?

**A**:
- **Access Token**: 30 minutes (set in ACCESS_TOKEN_EXPIRE_MINUTES)
- **Refresh Token**: 7 days (set in REFRESH_TOKEN_EXPIRE_DAYS)
- **Verification Code**: 6 minutes (hardcoded in code)

To change:
```env
# Change minutes
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Change days
REFRESH_TOKEN_EXPIRE_DAYS=30
```

---

### Q: Can I use same Google account for multiple services?

**A**: Yes, but each service needs:
1. Different Google Cloud Project
2. Different Google Client ID
3. Different authorized origins/redirects

Frontend must use the Client ID matching the backend's GOOGLE_CLIENT_ID.

---

### Q: How do I test Google Auth locally?

**A**:

1. **Using Google Client ID** (Required):
```bash
# 1. Get Client ID from Google Cloud Console
# 2. Add to .env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com

# 3. Frontend must use same Client ID
```

2. **Add localhost to approved origins**:
   - Google Cloud Console
   - APIs & Services > Credentials
   - Edit OAuth 2.0 Client ID
   - Authorized JavaScript origins:
     - `http://localhost:3000`
     - `http://localhost:5173`

3. **Test with curl** (won't work - needs real token):
```bash
# Can't test without frontend
# Must use real Google Sign-In token
```

---

### Q: What if user loses refresh token?

**A**: User must sign in again

```bash
# Lost token = can't get new access token
# Must sign in fresh
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "ValidPass123!"
  }'
```

---

### Q: Can I link email and Google auth for same account?

**A**: Current implementation: No (separate accounts)

If same email used:
```
1. User signs up with email/password as test@example.com
2. User tries Google auth with same email test@example.com
3. System reuses existing account (provider still = "email")
4. Both auth methods work for same account
```

Future enhancement: Allow official account linking.

---

### Q: How do I reset user password?

**A**: Two-step process:

```bash
# Step 1: Request password reset
curl -X POST http://localhost:8000/auth/forgot-pw \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
# Returns: {"message": "Verification code sent to email"}

# Step 2: Check email for 6-digit code, then:
curl -X POST http://localhost:8000/auth/reset-pw \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "code": "123456",
    "newPassword": "NewPassword123!"
  }'
# Returns: {"message": "Password reset successfully"}
```

---

### Q: How do I change password as logged-in user?

**A**: Current implementation: Use forgot-pw endpoint

Future enhancement: Add dedicated change-password endpoint

---

### Q: Is there a way to see all active sessions?

**A**: Current implementation: No (stateless JWT)

Could implement:
- Store session metadata in database
- Track login timestamp, IP, device
- Allow logout of specific sessions

---

### Q: What happens if database goes down?

**A**: 
- JWT validation still works (in-memory)
- But protected endpoints will fail (need DB for user lookup)
- Signup/signin will fail immediately

Solution: Implement database connection pooling and retries:
```python
# SQLAlchemy handles this automatically
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=40,
)
```

---

### Q: How do I deploy to production?

**A**: Checklist:

- [ ] Change `JWT_SECRET_KEY` to long random string
- [ ] Update `DATABASE_URL` to production database
- [ ] Get production GOOGLE_CLIENT_ID
- [ ] Add production domain to Google origins/redirects
- [ ] Set up SMTP (Gmail or SendGrid)
- [ ] Enable HTTPS (required for cookies)
- [ ] Set CORS allowed origins
- [ ] Use environment-specific `.env` files
- [ ] Set up monitoring/logging
- [ ] Test all endpoints in staging first

---

### Q: How do I debug authentication issues?

**A**: Enable verbose logging:

```python
# app/main.py
import logging
logging.basicConfig(level=logging.DEBUG)

# app/config.py - Enable SQLAlchemy echo
engine = create_async_engine(DATABASE_URL, echo=True)
```

---

### Q: Can I use this with mobile apps?

**A**: Yes! The REST API works with any client:

- React/Vue/Angular (web)
- React Native (mobile)
- Flutter (mobile)
- Native iOS/Android (mobile)

Just follow the same HTTP request patterns.

---

### Q: What about 2FA?

**A**: Not currently implemented

To add:
1. Store 2FA secret per user
2. After sign-in, prompt for 2FA code
3. Verify code before issuing tokens

Libraries:
```python
pip install pyotp qrcode  # For TOTP-based 2FA
```

---

### Q: Is HTTPS required?

**A**: 
- **Development**: HTTP fine (localhost)
- **Production**: HTTPS required
  - JWT in cookies requires Secure flag
  - Google OAuth requires HTTPS
  - Email links should be HTTPS

---

## 🎯 Common Workflows

### Workflow 1: First-time User (Email)

```
1. User clicks "Sign Up"
2. Submits: email, password, name
3. Server sends verification code to email
4. User receives email with 6-digit code
5. User enters code on website
6. Email verified
7. User can now sign in with email + password
8. User receives access token and refresh token
9. Access token used for protected endpoints
10. Refresh token used to get new access token when expired
```

### Workflow 2: First-time User (Google)

```
1. User clicks "Sign in with Google"
2. Google Sign-In popup appears
3. User completes Google authentication
4. Frontend gets ID token
5. Frontend sends ID token to /auth/google
6. Backend validates token with Google
7. Backend extracts email and name
8. Backend creates user (auto-verified)
9. Backend returns access token and refresh token
10. User logged in, ready to use app
```

### Workflow 3: Existing User

```
1. User clicks "Sign In"
2. Submits: email, password
3. Server checks email exists and password matches
4. Check email is verified
5. Return access token and refresh token
6. User logged in
```

### Workflow 4: Token Expired

```
1. User tries to call protected endpoint
2. Frontend gets 401 Unauthorized (token expired)
3. Frontend calls /auth/refresh-token with refresh token
4. Backend returns new access token
5. Frontend retries original request with new token
6. Request succeeds
```

### Workflow 5: Forgot Password

```
1. User clicks "Forgot Password"
2. Enters email
3. Server sends password reset code
4. User receives code in email
5. User enters code and new password
6. Server validates code, updates password
7. User can sign in with new password
```

---

## 📞 Still Having Issues?

1. **Check logs**:
```bash
# FastAPI logs show detailed error information
# Look for error message and stack trace
```

2. **Verify configuration**:
```bash
# Print env vars (don't commit this)
python -c "from app.config import settings; print(settings.dict())"
```

3. **Test database**:
```bash
# Test connection
psql -U postgres -d whattoeat -c "SELECT * FROM users;"
```

4. **Test SMTP**:
```python
# Simple SMTP test
import smtplib
with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login("email@gmail.com", "password")
    print("SMTP connection successful!")
```

5. **Review documentation**:
   - `IMPLEMENTATION_CHECKLIST.md` - Start here
   - `AUTHENTICATION_GUIDE.md` - Detailed guide
   - `CODE_ARCHITECTURE.md` - System design
   - `docs/api/auth/` - Endpoint details

---

**Last Resort**: Check the source code comments and error messages carefully. They often provide hints about what's wrong!
