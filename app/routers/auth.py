from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import (
    get_current_user_id,
    get_current_user_payload,
    get_user_id_jwt_or_dev_query,
    security,
)
from app.schemas.auth import MessageResponse, UpsertProfileRequest, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=UserResponse)
async def me(
    user_id=Depends(get_user_id_jwt_or_dev_query),
    db: AsyncSession = Depends(get_db),
):
    return await auth_service.get_me(user_id, db)


@router.post("/profile", response_model=UserResponse)
async def upsert_profile(
    payload: UpsertProfileRequest,
    user_id=Depends(get_current_user_id),
    jwt_payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db),
):
    email = jwt_payload.get("email")
    return await auth_service.upsert_profile(user_id, email, payload.name, db)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    user_id=Depends(get_current_user_id),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    return await auth_service.logout(user_id, credentials.credentials)
