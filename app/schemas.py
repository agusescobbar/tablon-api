from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=140, description="Texto del mensaje (máx. 140 caracteres).")


class MessagePublic(BaseModel):
    id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class MessageUpdate(BaseModel):
    content: Optional[str] = None