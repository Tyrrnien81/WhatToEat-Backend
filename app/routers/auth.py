from datetime import datetime, timedelta
import random
import uuid
import smtplib
from email.mime.text import MIMEText

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from supabase import create_client, Client

from app.database import get_db
from app.dependencies import get_current_user_id, get_current_user_payload
from app.models.user import Profile, PendingSignup
from app.schemas.auth import (
    UserResponse,
    UpsertProfileRequest,
    MessageResponse,
    SignUpRequest,
    VerifyEmailRequest,
    ResendCodeRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
)
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


def get_supabase_admin() -> Client:
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


def generate_verification_code() -> str:
    return f"{random.randint(0, 999999):06d}"


def send_verification_email(to_email: str, code: str):
    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        raise RuntimeError("SMTP is not configured")

    subject = "Your WhatToEat verification code"
    body = f"""Welcome to WhatToEat!

Your verification code is: {code}

This code will expire in 10 minutes.
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM_EMAIL
    msg["To"] = to_email

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)


@router.post("/signup", response_model=MessageResponse)
async def signup_route(
    payload: SignUpRequest,
    db: AsyncSession = Depends(get_db),
):
    admin = get_supabase_admin()

    existing_pending_result = await db.execute(
        select(PendingSignup).where(PendingSignup.email == payload.email)
    )
    existing_pending = existing_pending_result.scalar_one_or_none()

    if existing_pending and existing_pending.verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email is already verified. Please sign in.",
        )

    try:
        created = admin.auth.admin.create_user(
            {
                "email": payload.email,
                "password": payload.password,
                "email_confirm": False,
                "user_metadata": {
                    "name": payload.name or "",
                },
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create auth user: {str(e)}",
        )

    created_user = getattr(created, "user", None)
    if created_user is None or getattr(created_user, "id", None) is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase user creation returned no user id",
        )

    code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    if existing_pending:
        try:
            admin.auth.admin.delete_user(str(existing_pending.supabase_user_id))
        except Exception:
            pass

        existing_pending.name = payload.name
        existing_pending.supabase_user_id = uuid.UUID(str(created_user.id))
        existing_pending.verification_code = code
        existing_pending.expires_at = expires_at
        existing_pending.verified = False
    else:
        pending_signup = PendingSignup(
            email=payload.email,
            name=payload.name,
            supabase_user_id=uuid.UUID(str(created_user.id)),
            verification_code=code,
            expires_at=expires_at,
            verified=False,
        )
        db.add(pending_signup)

    await db.commit()

    try:
        send_verification_email(payload.email, code)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification email: {str(e)}",
        )

    return {"message": "Verification code sent"}


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email_route(
    payload: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
):
    admin = get_supabase_admin()

    result = await db.execute(
        select(PendingSignup).where(PendingSignup.email == payload.email)
    )
    pending = result.scalar_one_or_none()

    if not pending:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signup request not found",
        )

    if pending.verified:
        return {"message": "Email already verified"}

    if datetime.utcnow() > pending.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired",
        )

    if pending.verification_code != payload.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code",
        )

    try:
        admin.auth.admin.update_user_by_id(
            str(pending.supabase_user_id),
            {"email_confirm": True},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm auth user: {str(e)}",
        )

    pending.verified = True
    await db.commit()

    return {"message": "Email verified successfully"}


@router.post("/resend-code", response_model=MessageResponse)
async def resend_code_route(
    payload: ResendCodeRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PendingSignup).where(PendingSignup.email == payload.email)
    )
    pending = result.scalar_one_or_none()

    if not pending:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signup request not found",
        )

    if pending.verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified",
        )

    pending.verification_code = generate_verification_code()
    pending.expires_at = datetime.utcnow() + timedelta(minutes=10)

    await db.commit()

    try:
        send_verification_email(payload.email, pending.verification_code)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resend verification email: {str(e)}",
        )

    return {"message": "Verification code resent"}


@router.post("/refresh-token", response_model=RefreshTokenResponse)
async def refresh_token_route(payload: RefreshTokenRequest):
    """
    Supabase JS SDK가 보통 자동 갱신을 처리하지만,
    API 표를 맞추기 위해 백엔드 wrapper endpoint를 둡니다.
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase is not configured",
        )

    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

    try:
        refreshed = client.auth.refresh_session(payload.refresh_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to refresh token: {str(e)}",
        )

    session = getattr(refreshed, "session", None)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No refreshed session returned",
        )

    access_token = getattr(session, "access_token", None)
    refresh_token = getattr(session, "refresh_token", None)

    if not access_token or not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing refreshed tokens",
        )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout", response_model=MessageResponse)
async def logout_route(
    user_payload: dict = Depends(get_current_user_payload),
):
    """
    현재 구조에서는 프론트의 supabase.auth.signOut() 이 핵심이고,
    서버는 인증된 요청만 받았다는 확인용 응답을 반환합니다.
    필요 시 추후 서버측 세션 블랙리스트/감사 로그를 붙일 수 있습니다.
    """
    _ = user_payload
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def me_route(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Profile).where(Profile.id == user_id))
    profile = result.scalar_one_or_none()

    if not profile:
        return {
            "id": str(user_id),
            "email": None,
            "name": None,
        }

    return {
        "id": str(profile.id),
        "email": profile.email,
        "name": profile.name,
    }


@router.post("/profile", response_model=UserResponse)
async def upsert_profile_route(
    payload: UpsertProfileRequest,
    user_id=Depends(get_current_user_id),
    user_payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db),
):
    email = user_payload.get("email")

    result = await db.execute(select(Profile).where(Profile.id == user_id))
    profile = result.scalar_one_or_none()

    if not profile:
        profile = Profile(
            id=user_id,
            email=email,
            name=payload.name,
        )
        db.add(profile)
    else:
        profile.email = email
        if payload.name is not None:
            profile.name = payload.name

    await db.commit()
    await db.refresh(profile)

    return {
        "id": str(profile.id),
        "email": profile.email,
        "name": profile.name,
    }