from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CommentCreate(BaseModel):
    body: str
    is_internal: bool = False


class CommentRead(BaseModel):
    id: int
    ticket_id: int
    author_user_id: int
    body: str
    is_internal: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
