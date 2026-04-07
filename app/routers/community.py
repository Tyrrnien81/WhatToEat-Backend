import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.community import (
    CommunityLikeResponse,
    CommunityPostDetailResponse,
    CommunityPostsResponse,
    CreateCommunityPostRequest,
    CreateCommunityPostResponse,
    CreateReplyRequest,
    CreateReplyResponse,
    DeleteCommunityPostResponse,
)
from app.services import community_service

router = APIRouter(prefix="/community", tags=["community"])


@router.get("/posts", response_model=CommunityPostsResponse)
async def list_posts(
    q: str | None = Query(None),
    hallTag: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    user_id: uuid.UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await community_service.get_posts(page, limit, q, hallTag, user_id, db)


@router.post("/posts", response_model=CreateCommunityPostResponse, status_code=201)
async def create_post(
    body: CreateCommunityPostRequest,
    user_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    return await community_service.create_post(user_id, body.content, body.hallTag, body.imageUrl, db)


@router.get("/posts/{post_id}", response_model=CommunityPostDetailResponse)
async def get_post_detail(
    post_id: uuid.UUID,
    user_id: uuid.UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await community_service.get_post_detail(post_id, user_id, db)


@router.delete("/posts/{post_id}", response_model=DeleteCommunityPostResponse)
async def delete_post(
    post_id: uuid.UUID,
    user_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    return await community_service.delete_post(post_id, user_id, db)


@router.post("/posts/{post_id}/likes", response_model=CommunityLikeResponse)
async def like_post(
    post_id: uuid.UUID,
    user_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    return await community_service.like_post(post_id, user_id, db)


@router.delete("/posts/{post_id}/likes", response_model=CommunityLikeResponse)
async def unlike_post(
    post_id: uuid.UUID,
    user_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    return await community_service.unlike_post(post_id, user_id, db)


@router.post("/posts/{post_id}/replies", response_model=CreateReplyResponse, status_code=201)
async def create_post_reply(
    post_id: uuid.UUID,
    body: CreateReplyRequest,
    user_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    return await community_service.create_post_reply(post_id, user_id, body.content, db)


@router.post("/replies/{reply_id}/replies", response_model=CreateReplyResponse, status_code=201)
async def create_reply_reply(
    reply_id: uuid.UUID,
    body: CreateReplyRequest,
    user_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    return await community_service.create_reply_reply(reply_id, user_id, body.content, db)


@router.post("/replies/{reply_id}/likes", response_model=CommunityLikeResponse)
async def like_reply(
    reply_id: uuid.UUID,
    user_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    return await community_service.like_reply(reply_id, user_id, db)


@router.delete("/replies/{reply_id}/likes", response_model=CommunityLikeResponse)
async def unlike_reply(
    reply_id: uuid.UUID,
    user_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    return await community_service.unlike_reply(reply_id, user_id, db)