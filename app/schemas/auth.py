from typing import Optional
from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: str
    email: Optional[str] = None
    name: Optional[str] = None

    class Config:
        from_attributes = True


class UpsertProfileRequest(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None


class MessageResponse(BaseModel):
    message: str