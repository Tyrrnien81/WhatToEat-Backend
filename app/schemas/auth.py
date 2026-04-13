from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    id: str
    email: Optional[str] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}


class UpsertProfileRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)


class MessageResponse(BaseModel):
    message: str
