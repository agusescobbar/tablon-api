from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(max_length=140)
    # unique=True refuerza a nivel de base de datos la regla de
    # "un mensaje por sesión", además de la validación en el endpoint.
    session_id: str = Field(index=True, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
