import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.favorite import SaveFavoriteRequest, SaveFavoriteResponse, MessageResponse
from app.services import favorite_service

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.post("", response_model=SaveFavoriteResponse, status_code=status.HTTP_201_CREATED)
async def save_favorite(
    body: SaveFavoriteRequest,
    user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await favorite_service.save_favorite(
        user_id, body.comboId, body.recommendationSnapshot, db
    )


@router.delete("/{favorite_id}", response_model=MessageResponse)
async def delete_favorite(
    favorite_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await favorite_service.delete_favorite(favorite_id, user_id, db)
