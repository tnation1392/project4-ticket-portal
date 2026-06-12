from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.constants import ALLOWED_TICKET_TRANSITIONS, TicketStatus, UserRole
from app.db.base import utcnow
from app.models.category import Category
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.assignment import TicketAssignRequest
from app.schemas.ticket import TicketCreate
from app.schemas.transition import TicketTransitionRequest


def create_ticket(db: Session, payload: TicketCreate, current_user: User) -> Ticket:
    category = db.get(Category, payload.category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    if not category.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category is inactive",
        )

    ticket = Ticket(
        title=payload.title.strip(),
        description=payload.description.strip(),
        category_id=payload.category_id,
        priority=payload.priority.value,
        status=TicketStatus.NEW.value,
        created_by_user_id=current_user.id,
        assigned_to_user_id=None,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def list_tickets_for_user(db: Session, current_user: User) -> list[Ticket]:
    stmt = select(Ticket)

    if current_user.role == UserRole.EMPLOYEE.value:
        stmt = stmt.where(Ticket.created_by_user_id == current_user.id)

    stmt = stmt.order_by(Ticket.created_at.desc())

    return list(db.execute(stmt).scalars().all())


def get_ticket_for_user(db: Session, ticket_id: int, current_user: User) -> Ticket:
    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    if current_user.role == UserRole.EMPLOYEE.value:
        if ticket.created_by_user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this ticket",
            )

    return ticket


def assign_ticket(
    db: Session,
    ticket_id: int,
    payload: TicketAssignRequest,
    current_user: User,
) -> Ticket:
    ticket = get_ticket_for_user(db, ticket_id, current_user)

    if current_user.role == UserRole.EMPLOYEE.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to assign tickets",
        )

    assigned_user = db.get(User, payload.assigned_to_user_id)
    if assigned_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found",
        )

    if assigned_user.role != UserRole.AGENT.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assigned user must have agent role",
        )

    if current_user.role == UserRole.AGENT.value:
        if payload.assigned_to_user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Agents can only assign tickets to themselves",
            )

        if ticket.assigned_to_user_id is not None and ticket.assigned_to_user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Ticket is already assigned",
            )

    ticket.assigned_to_user_id = assigned_user.id

    db.commit()
    db.refresh(ticket)
    return ticket


def transition_ticket_status(
    db: Session,
    ticket_id: int,
    payload: TicketTransitionRequest,
    current_user: User,
) -> Ticket:
    ticket = get_ticket_for_user(db, ticket_id, current_user)

    current_status = TicketStatus(ticket.status)
    target_status = payload.to_status

    allowed_targets = ALLOWED_TICKET_TRANSITIONS.get(current_status, set())
    if target_status not in allowed_targets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition ticket from {current_status.value} to {target_status.value}",
        )

    if current_user.role == UserRole.EMPLOYEE.value:
        allowed_employee_transitions = {
            (TicketStatus.RESOLVED, TicketStatus.CLOSED),
            (TicketStatus.RESOLVED, TicketStatus.IN_PROGRESS),
        }

        if (current_status, target_status) not in allowed_employee_transitions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform this transition",
            )

    elif current_user.role == UserRole.AGENT.value:
        allowed_agent_transitions = {
            (TicketStatus.NEW, TicketStatus.TRIAGED),
            (TicketStatus.TRIAGED, TicketStatus.IN_PROGRESS),
            (TicketStatus.IN_PROGRESS, TicketStatus.WAITING_FOR_CUSTOMER),
            (TicketStatus.WAITING_FOR_CUSTOMER, TicketStatus.IN_PROGRESS),
            (TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED),
        }

        if (current_status, target_status) not in allowed_agent_transitions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform this transition",
            )

    elif current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this transition",
        )

    if target_status == TicketStatus.IN_PROGRESS and ticket.assigned_to_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket must be assigned before moving to in_progress",
        )

    ticket.status = target_status.value

    if target_status == TicketStatus.RESOLVED:
        ticket.resolved_at = utcnow()

    elif target_status == TicketStatus.CLOSED:
        ticket.closed_at = utcnow()

    elif current_status == TicketStatus.RESOLVED and target_status == TicketStatus.IN_PROGRESS:
        ticket.resolved_at = None
        ticket.closed_at = None

    db.commit()
    db.refresh(ticket)
    return ticket