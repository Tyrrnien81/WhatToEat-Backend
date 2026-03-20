import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.auth import (
    SignInRequest,
    SignUpRequest,
    GoogleAuthRequest,
    ForgotPasswordRequest,
    VerifyEmailRequest,
    ResendCodeRequest,
    ResetPasswordRequest,
    RefreshTokenRequest,
    AuthResponse,
    SignUpResponse,
    MessageResponse,
    TokenRefreshResponse,
    UserResponse,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signin", response_model=AuthResponse)
async def signin(body: SignInRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.sign_in(body.email, body.password, db)


@router.post("/signup", response_model=SignUpResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: SignUpRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.sign_up(body.email, body.password, body.name, db)


@router.post("/google", response_model=AuthResponse)
async def google_login(body: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.google_auth(body.idToken, db)


@router.post("/forgot-pw", response_model=MessageResponse)
async def forgot_password(body: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.forgot_password(body.email, db)


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(body: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.verify_email(body.email, body.code, db)


@router.post("/resend-code", response_model=MessageResponse)
async def resend_code(body: ResendCodeRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.resend_code(body.email, db)


@router.post("/reset-pw", response_model=MessageResponse)
async def reset_password(body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.reset_password(body.email, body.code, body.newPassword, db)


@router.post("/refresh-token", response_model=TokenRefreshResponse)
async def refresh_token(body: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.refresh_access_token(body.refreshToken, db)


@router.post("/logout", response_model=MessageResponse)
async def logout(user_id: uuid.UUID = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await auth_service.logout(user_id, db)


@router.get("/me", response_model=UserResponse)
async def me(user_id: uuid.UUID = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await auth_service.get_me(user_id, db)
