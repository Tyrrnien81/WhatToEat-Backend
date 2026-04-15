from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_user_id_jwt_or_dev_query
from app.schemas.questionnaire import (
    PreferencesResponse,
    PreferencesUpdateRequest,
    QuestionnaireSubmitRequest,
)
from app.services import questionnaire_service

router = APIRouter(tags=["questionnaire"])


@router.post("/questionnaire", status_code=201)
async def submit_questionnaire(
    payload: QuestionnaireSubmitRequest,
    user_id=Depends(get_user_id_jwt_or_dev_query),
    db: AsyncSession = Depends(get_db),
):
    return await questionnaire_service.submit_questionnaire(user_id, payload, db)


@router.get("/users/me/preferences", response_model=PreferencesResponse)
async def get_preferences(
    user_id=Depends(get_user_id_jwt_or_dev_query),
    db: AsyncSession = Depends(get_db),
):
    return await questionnaire_service.get_preferences(user_id, db)


@router.patch("/users/me/preferences")
async def update_preferences(
    payload: PreferencesUpdateRequest,
    user_id=Depends(get_user_id_jwt_or_dev_query),
    db: AsyncSession = Depends(get_db),
):
    return await questionnaire_service.update_preferences(user_id, payload, db)
