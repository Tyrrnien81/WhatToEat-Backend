import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.favorite import Favorite


async def save_favorite(
    user_id: uuid.UUID,
    combo_id: uuid.UUID,
    recommendation_snapshot: dict,
    db: AsyncSession,
) -> dict:
    favorite = Favorite(
        user_id=user_id,
        combo_id=combo_id,
        recommendation_snapshot=recommendation_snapshot,
    )
    db.add(favorite)
    try:
        await db.commit()
        await db.refresh(favorite)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "This combo is already in the user's favorites",
        )
    return {"id": favorite.id, "message": "Combo saved to favorites"}


async def delete_favorite(
    favorite_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> dict:
    result = await db.execute(select(Favorite).where(Favorite.id == favorite_id))
    favorite = result.scalar_one_or_none()

    if not favorite:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Favorite not found")

    if favorite.user_id != user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Cannot delete another user's favorite")

    await db.delete(favorite)
    await db.commit()
    return {"message": "Favorite removed successfully"}
