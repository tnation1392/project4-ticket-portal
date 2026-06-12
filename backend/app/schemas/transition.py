from pydantic import BaseModel

from app.constants import TicketStatus


class TicketTransitionRequest(BaseModel):
    to_status: TicketStatus