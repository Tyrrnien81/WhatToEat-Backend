import uuid

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.scan import ScanLogRequest, ScanLogResponse, ScanResponse
from app.services import scan_service

router = APIRouter(tags=["scan"])


@router.post("/scan", response_model=ScanResponse)
async def upload_scan(
    image: UploadFile = File(...),
    user_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    return await scan_service.scan_image(user_id, image, db)


@router.post("/scan/log", response_model=ScanLogResponse, status_code=201)
async def log_scan(
    body: ScanLogRequest,
    user_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    items = [item.model_dump() for item in body.items]
    return await scan_service.log_scan_result(user_id, body.scanId, items, body.mealType, body.date, db)
