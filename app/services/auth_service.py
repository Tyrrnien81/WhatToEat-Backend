import random
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import RefreshToken, User, VerificationCode
from app.utils.email import send_verification_email
from app.utils.google_oauth import verify_google_token
from app.utils.jwt import create_access_token, create_refresh_token, decode_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def _generate_code() -> str:
    return f"{random.randint(0, 999999):06d}"


def _user_response(user: User) -> dict:
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
    }


async def _create_and_store_refresh_token(user_id: uuid.UUID, db: AsyncSession) -> str:
    token, expires_at = create_refresh_token(user_id)

    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
        is_revoked=False,
    )
    db.add(refresh_token)
    await db.commit()

    return token


async def _replace_refresh_token(user_id: uuid.UUID, old_token: str, db: AsyncSession) -> tuple[str, str]:
    now = datetime.now(timezone.utc)

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == old_token,
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked.is_(False),
        )
    )
    stored_token = result.scalar_one_or_none()

    if not stored_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    expires_at = stored_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at <= now:
        stored_token.is_revoked = True
        await db.commit()
        raise HTTPException(status_code=401, detail="Refresh token expired")

    stored_token.is_revoked = True

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        await db.commit()
        raise HTTPException(status_code=404, detail="User not found")

    new_access_token = create_access_token(user.id, user.email)
    new_refresh_token, new_refresh_exp = create_refresh_token(user.id)

    db.add(
        RefreshToken(
            user_id=user.id,
            token=new_refresh_token,
            expires_at=new_refresh_exp,
            is_revoked=False,
        )
    )

    await db.commit()
    return new_access_token, new_refresh_token


async def _create_verification_code(email: str, code_type: str, db: AsyncSession) -> str:
    await db.execute(
        delete(VerificationCode).where(
            VerificationCode.email == email,
            VerificationCode.code_type == code_type,
        )
    )

    code = _generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=6)

    db.add(
        VerificationCode(
            email=email,
            code=code,
            code_type=code_type,
            expires_at=expires_at,
        )
    )
    await db.commit()
    return code


async def sign_up(email: str, password: str, name: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user and existing_user.is_verified:
        raise HTTPException(status_code=400, detail="Email already registered")

    if existing_user and existing_user.provider == "google":
        raise HTTPException(
            status_code=400,
            detail="This email is already registered with Google sign-in",
        )

    if existing_user:
        existing_user.name = name
        existing_user.password_hash = _hash_password(password)
        existing_user.provider = "email"
    else:
        existing_user = User(
            email=email,
            name=name,
            password_hash=_hash_password(password),
            provider="email",
            is_verified=False,
        )
        db.add(existing_user)

    await db.commit()
    await db.refresh(existing_user)

    code = await _create_verification_code(email, "signup", db)
    send_verification_email(email, code)

    return {
        "message": "Sign-up successful. Verification code sent to your email.",
        "user": _user_response(existing_user),
    }


async def sign_in(email: str, password: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if user.provider != "email":
        raise HTTPException(status_code=400, detail="Use Google sign-in for this account")

    if not user.password_hash or not _verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email is not verified")

    access_token = create_access_token(user.id, user.email)
    refresh_token = await _create_and_store_refresh_token(user.id, db)

    return {
        "token": access_token,
        "refreshToken": refresh_token,
        "user": _user_response(user),
    }


async def google_auth(id_token: str, db: AsyncSession):
    google_user = verify_google_token(id_token)
    if not google_user:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    email = google_user["email"]
    name = google_user.get("name") or email.split("@")[0]

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user:
        if user.provider == "email":
            if not user.is_verified:
                user.is_verified = True
            if not user.name:
                user.name = name
        else:
            user.name = name or user.name
    else:
        user = User(
            email=email,
            name=name,
            password_hash=None,
            provider="google",
            is_verified=True,
        )
        db.add(user)

    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(user.id, user.email)
    refresh_token = await _create_and_store_refresh_token(user.id, db)

    return {
        "token": access_token,
        "refreshToken": refresh_token,
        "user": _user_response(user),
    }


async def forgot_password(email: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    # 이메일 존재 여부 노출 방지
    if not user:
        return {"message": "If the email exists, a verification code has been sent."}

    if user.provider != "email":
        return {"message": "If the email exists, a verification code has been sent."}

    code = await _create_verification_code(email, "reset", db)
    send_verification_email(email, code)

    return {"message": "If the email exists, a verification code has been sent."}


async def verify_email(email: str, code: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
        select(VerificationCode).where(
            VerificationCode.email == email,
            VerificationCode.code == code,
            VerificationCode.code_type == "signup",
        )
    )
    verification = result.scalar_one_or_none()

    if not verification:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    expires_at = verification.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Verification code expired")

    user.is_verified = True
    await db.delete(verification)
    await db.commit()

    return {"message": "Email verified successfully"}


async def resend_code(email: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.provider != "email":
        raise HTTPException(status_code=400, detail="Google accounts do not require email verification")

    if user.is_verified:
        return {"message": "Email is already verified"}

    code = await _create_verification_code(email, "signup", db)
    send_verification_email(email, code)

    return {"message": "Verification code resent successfully"}


async def reset_password(email: str, code: str, new_password: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.provider != "email":
        raise HTTPException(status_code=400, detail="Password reset is only available for email accounts")

    result = await db.execute(
        select(VerificationCode).where(
            VerificationCode.email == email,
            VerificationCode.code == code,
            VerificationCode.code_type == "reset",
        )
    )
    reset_code = result.scalar_one_or_none()

    if not reset_code:
        raise HTTPException(status_code=400, detail="Invalid reset code")

    expires_at = reset_code.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset code expired")

    user.password_hash = _hash_password(new_password)
    await db.delete(reset_code)

    # 기존 refresh token들 전부 revoke
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user.id, RefreshToken.is_revoked.is_(False))
        .values(is_revoked=True)
    )

    await db.commit()

    return {"message": "Password has been reset successfully"}


async def refresh_access_token(refresh_token: str, db: AsyncSession):
    payload = decode_token(refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid refresh token payload")

    new_access_token, new_refresh_token = await _replace_refresh_token(user_id, refresh_token, db)

    return {
        "token": new_access_token,
        "refreshToken": new_refresh_token,
    }


async def logout(user_id: uuid.UUID, db: AsyncSession):
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.is_revoked.is_(False))
        .values(is_revoked=True)
    )
    await db.commit()

    return {"message": "Logged out successfully"}


async def get_me(user_id: uuid.UUID, db: AsyncSession):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return _user_response(user)