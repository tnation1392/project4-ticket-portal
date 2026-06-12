from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.assignment import TicketAssignRequest
from app.schemas.ticket import TicketCreate, TicketRead
from app.schemas.transition import TicketTransitionRequest
from app.services.ticket_service import (
    assign_ticket,
    create_ticket,
    get_ticket_for_user,
    list_tickets_for_user,
    transition_ticket_status,
)

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
def create_ticket_route(
    payload: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_ticket(db, payload, current_user)


@router.get("", response_model=list[TicketRead])
def get_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_tickets_for_user(db, current_user)


@router.get("/{ticket_id}", response_model=TicketRead)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_ticket_for_user(db, ticket_id, current_user)


@router.post("/{ticket_id}/assign", response_model=TicketRead)
def assign_ticket_route(
    ticket_id: int,
    payload: TicketAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return assign_ticket(db, ticket_id, payload, current_user)


@router.post("/{ticket_id}/transition", response_model=TicketRead)
def transition_ticket_route(
    ticket_id: int,
    payload: TicketTransitionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return transition_ticket_status(db, ticket_id, payload, current_user)
