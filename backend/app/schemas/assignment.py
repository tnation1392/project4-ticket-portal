from pydantic import BaseModel


class TicketAssignRequest(BaseModel):
    assigned_to_user_id: int
