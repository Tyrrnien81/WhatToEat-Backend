from typing import Optional
from pydantic import BaseModel, Field, EmailStr


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


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)


class ResendCodeRequest(BaseModel):
    email: EmailStr


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"