from typing import Optional
from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    id: str
    email: Optional[str] = None
    name: Optional[str] = None

    class Config:
        from_attributes = True


class UpsertProfileRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)


class MessageResponse(BaseModel):
    message: str