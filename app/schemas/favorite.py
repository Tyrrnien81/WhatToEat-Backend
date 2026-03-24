import uuid

from pydantic import BaseModel


# --- Request Schemas ---

class SaveFavoriteRequest(BaseModel):
    comboId: uuid.UUID
    recommendationSnapshot: dict


# --- Response Schemas ---

class SaveFavoriteResponse(BaseModel):
    id: uuid.UUID
    message: str


class MessageResponse(BaseModel):
    message: str
