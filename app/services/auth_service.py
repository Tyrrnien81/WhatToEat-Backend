import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, VerificationCode, RefreshToken
from app.utils.jwt import create_access_token, create_refresh_token, decode_token
from app.utils.google_oauth import verify_google_token
from app.utils.email import send_verification_email

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

VERIFICATION_CODE_EXPIRY_MINUTES = 6
RESEND_COOLDOWN_SECONDS = 30


def _hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _generate_code() -> str:
    return f"{secrets.randbelow(900000) + 100000}"


# ─── Sign In ─────────────────────────────────────────────

async def sign_in(email: str, password: str, db: AsyncSession) -> dict:
    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if not user or not user.password_hash or not _verify_password(password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    if not user.is_verified:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email not verified")

    access_token = create_access_token(user.id, user.email)
    refresh_tok, refresh_exp = create_refresh_token(user.id)
    db.add(RefreshToken(user_id=user.id, token=refresh_tok, expires_at=refresh_exp))
    await db.commit()

    return {
        "token": access_token,
        "refreshToken": refresh_tok,
        "user": {"id": str(user.id), "email": user.email, "name": user.name},
    }


# ─── Sign Up ─────────────────────────────────────────────

async def sign_up(email: str, password: str, name: str, db: AsyncSession) -> dict:
    existing = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

    user = User(
        email=email,
        name=name,
        password_hash=_hash_password(password),
        provider="email",
        is_verified=False,
    )
    db.add(user)
    await db.flush()

    code = _generate_code()
    db.add(VerificationCode(
        email=email,
        code=code,
        code_type="signup",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=VERIFICATION_CODE_EXPIRY_MINUTES),
    ))
    await db.commit()

    try:
        send_verification_email(email, code)
    except Exception:
        pass  # don't block signup if email fails; user can resend

    return {
        "message": "Account created successfully. Verification code sent to email.",
        "user": {"id": str(user.id), "email": user.email, "name": user.name},
    }


# ─── Google Auth ──────────────────────────────────────────

async def google_auth(id_token: str, db: AsyncSession) -> dict:
    google_info = verify_google_token(id_token)
    if not google_info:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired Google token")

    email = google_info["email"]
    name = google_info["name"]

    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if not user:
        user = User(email=email, name=name, provider="google", is_verified=True)
        db.add(user)
        await db.flush()

    access_token = create_access_token(user.id, user.email)
    refresh_tok, refresh_exp = create_refresh_token(user.id)
    db.add(RefreshToken(user_id=user.id, token=refresh_tok, expires_at=refresh_exp))
    await db.commit()

    return {
        "token": access_token,
        "refreshToken": refresh_tok,
        "user": {"id": str(user.id), "email": user.email, "name": user.name},
    }


# ─── Forgot Password ─────────────────────────────────────

async def forgot_password(email: str, db: AsyncSession) -> dict:
    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Email not registered")

    code = _generate_code()
    db.add(VerificationCode(
        email=email,
        code=code,
        code_type="reset",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=VERIFICATION_CODE_EXPIRY_MINUTES),
    ))
    await db.commit()

    try:
        send_verification_email(email, code)
    except Exception:
        pass

    return {"message": "Verification code sent to email"}


# ─── Verify Email ─────────────────────────────────────────

async def verify_email(email: str, code: str, db: AsyncSession) -> dict:
    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Email not registered")

    vc = (await db.execute(
        select(VerificationCode)
        .where(
            VerificationCode.email == email,
            VerificationCode.code == code,
            VerificationCode.expires_at > datetime.now(timezone.utc),
        )
        .order_by(VerificationCode.created_at.desc())
    )).scalar_one_or_none()

    if not vc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired verification code")

    user.is_verified = True
    # clean up used codes for this email
    await db.execute(delete(VerificationCode).where(VerificationCode.email == email))
    await db.commit()

    return {"message": "Email verified successfully"}


# ─── Resend Code ──────────────────────────────────────────

async def resend_code(email: str, db: AsyncSession) -> dict:
    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Email not registered")

    latest = (await db.execute(
        select(VerificationCode)
        .where(VerificationCode.email == email)
        .order_by(VerificationCode.created_at.desc())
    )).scalar_one_or_none()

    if latest:
        elapsed = (datetime.now(timezone.utc) - latest.created_at.replace(tzinfo=timezone.utc)).total_seconds()
        if elapsed < RESEND_COOLDOWN_SECONDS:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Please wait before requesting a new code")

    code_type = "signup" if not user.is_verified else "reset"
    code = _generate_code()
    db.add(VerificationCode(
        email=email,
        code=code,
        code_type=code_type,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=VERIFICATION_CODE_EXPIRY_MINUTES),
    ))
    await db.commit()

    try:
        send_verification_email(email, code)
    except Exception:
        pass

    return {"message": "Verification code resent to email"}


# ─── Reset Password ──────────────────────────────────────

async def reset_password(email: str, code: str, new_password: str, db: AsyncSession) -> dict:
    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Email not registered")

    vc = (await db.execute(
        select(VerificationCode)
        .where(
            VerificationCode.email == email,
            VerificationCode.code == code,
            VerificationCode.code_type == "reset",
            VerificationCode.expires_at > datetime.now(timezone.utc),
        )
        .order_by(VerificationCode.created_at.desc())
    )).scalar_one_or_none()

    if not vc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired verification code")

    user.password_hash = _hash_password(new_password)
    await db.execute(delete(VerificationCode).where(VerificationCode.email == email))
    await db.commit()

    return {"message": "Password reset successfully"}


# ─── Refresh Token ────────────────────────────────────────

async def refresh_access_token(refresh_token_str: str, db: AsyncSession) -> dict:
    payload = decode_token(refresh_token_str)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired refresh token")

    stored = (await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == refresh_token_str,
            RefreshToken.is_revoked == False,
        )
    )).scalar_one_or_none()

    if not stored:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired refresh token")

    user = (await db.execute(select(User).where(User.id == stored.user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")

    # revoke old token
    stored.is_revoked = True

    # issue new tokens
    new_access = create_access_token(user.id, user.email)
    new_refresh, new_refresh_exp = create_refresh_token(user.id)
    db.add(RefreshToken(user_id=user.id, token=new_refresh, expires_at=new_refresh_exp))
    await db.commit()

    return {"token": new_access, "refreshToken": new_refresh}


# ─── Logout ──────────────────────────────────────────────

async def logout(user_id, db: AsyncSession) -> dict:
    # revoke all refresh tokens for this user
    tokens = (await db.execute(
        select(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.is_revoked == False)
    )).scalars().all()
    for t in tokens:
        t.is_revoked = True
    await db.commit()

    return {"message": "Logged out successfully"}


# ─── Get Current User ────────────────────────────────────

async def get_me(user_id, db: AsyncSession) -> dict:
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return {"id": str(user.id), "email": user.email, "name": user.name}
