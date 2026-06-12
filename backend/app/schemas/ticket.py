from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.constants import TicketPriority, TicketStatus


class TicketCreate(BaseModel):
    title: str
    description: str
    category_id: int
    priority: TicketPriority


class TicketRead(BaseModel):
    id: int
    title: str
    description: str
    category_id: int
    priority: TicketPriority
    status: TicketStatus
    created_by_user_id: int
    assigned_to_user_id: int | None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None
    closed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)