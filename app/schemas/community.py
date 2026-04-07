from __future__ import annotations

from pydantic import BaseModel, Field


class CommunityAuthor(BaseModel):
    id: str
    name: str


class CommunityPostItem(BaseModel):
    id: str
    author: CommunityAuthor
    content: str
    hallTag: str | None = None
    imageUrl: str | None = None
    likeCount: int
    replyCount: int
    createdAt: str
    likedByMe: bool = False


class CommunityPostsResponse(BaseModel):
    page: int
    limit: int
    hasMore: bool
    posts: list[CommunityPostItem]


class CreateCommunityPostRequest(BaseModel):
    content: str = Field(min_length=1, max_length=2000)
    hallTag: str | None = Field(default=None, max_length=50)
    imageUrl: str | None = Field(default=None, max_length=500)


class CreateCommunityPostResponse(BaseModel):
    id: str
    message: str


class DeleteCommunityPostResponse(BaseModel):
    message: str


class CommunityReplyItem(BaseModel):
    id: str
    postId: str
    parentReplyId: str | None = None
    author: CommunityAuthor
    content: str
    likeCount: int
    likedByMe: bool = False
    createdAt: str
    replies: list[CommunityReplyItem] = Field(default_factory=list)


class CommunityPostDetailResponse(BaseModel):
    post: CommunityPostItem
    replies: list[CommunityReplyItem]


class CreateReplyRequest(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class CreateReplyResponse(BaseModel):
    id: str
    message: str


class CommunityLikeResponse(BaseModel):
    liked: bool
    likeCount: int
    message: str


CommunityReplyItem.model_rebuild()