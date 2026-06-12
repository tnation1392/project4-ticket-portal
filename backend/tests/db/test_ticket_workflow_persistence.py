from app.constants import TicketStatus
from app.models.category import Category
from app.models.ticket import Ticket
from app.schemas.assignment import TicketAssignRequest
from app.schemas.ticket import TicketCreate
from app.schemas.transition import TicketTransitionRequest
from app.services.ticket_service import (
    assign_ticket,
    create_ticket,
    transition_ticket_status,
)


def create_active_category(db_session, name: str = "Hardware") -> Category:
    category = Category(
        name=name,
        description=f"{name} issues",
        is_active=True,
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


def test_create_ticket_persists_default_fields(db_session, seeded_users):
    category = create_active_category(db_session)

    payload = TicketCreate(
        title="Laptop screen flickering",
        description="The laptop screen flickers when opening the lid.",
        category_id=category.id,
        priority="high",
    )

    created_ticket = create_ticket(
        db=db_session,
        payload=payload,
        current_user=seeded_users["employee"],
    )

    persisted_ticket = db_session.get(Ticket, created_ticket.id)

    assert persisted_ticket is not None
    assert persisted_ticket.title == "Laptop screen flickering"
    assert persisted_ticket.description == "The laptop screen flickers when opening the lid."
    assert persisted_ticket.category_id == category.id
    assert persisted_ticket.priority == "high"
    assert persisted_ticket.status == TicketStatus.NEW.value
    assert persisted_ticket.created_by_user_id == seeded_users["employee"].id
    assert persisted_ticket.assigned_to_user_id is None
    assert persisted_ticket.created_at is not None
    assert persisted_ticket.updated_at is not None


def test_assign_ticket_persists_assigned_agent(db_session, seeded_users):
    category = create_active_category(db_session)

    ticket = create_ticket(
        db=db_session,
        payload=TicketCreate(
            title="VPN issue",
            description="Cannot connect to VPN from home.",
            category_id=category.id,
            priority="medium",
        ),
        current_user=seeded_users["employee"],
    )

    updated_ticket = assign_ticket(
        db=db_session,
        ticket_id=ticket.id,
        payload=TicketAssignRequest(assigned_to_user_id=seeded_users["agent"].id),
        current_user=seeded_users["admin"],
    )

    persisted_ticket = db_session.get(Ticket, updated_ticket.id)

    assert persisted_ticket is not None
    assert persisted_ticket.assigned_to_user_id == seeded_users["agent"].id


def test_resolving_ticket_sets_resolved_at_in_db(db_session, seeded_users):
    category = create_active_category(db_session)

    ticket = create_ticket(
        db=db_session,
        payload=TicketCreate(
            title="Application crash",
            description="The application crashes on startup.",
            category_id=category.id,
            priority="high",
        ),
        current_user=seeded_users["employee"],
    )

    ticket = assign_ticket(
        db=db_session,
        ticket_id=ticket.id,
        payload=TicketAssignRequest(assigned_to_user_id=seeded_users["agent"].id),
        current_user=seeded_users["admin"],
    )

    ticket.status = TicketStatus.IN_PROGRESS.value
    db_session.commit()
    db_session.refresh(ticket)

    transitioned_ticket = transition_ticket_status(
        db=db_session,
        ticket_id=ticket.id,
        payload=TicketTransitionRequest(to_status=TicketStatus.RESOLVED),
        current_user=seeded_users["agent"],
    )

    persisted_ticket = db_session.get(Ticket, transitioned_ticket.id)

    assert persisted_ticket is not None
    assert persisted_ticket.status == TicketStatus.RESOLVED.value
    assert persisted_ticket.resolved_at is not None


def test_closing_ticket_sets_closed_at_in_db(db_session, seeded_users):
    category = create_active_category(db_session)

    ticket = create_ticket(
        db=db_session,
        payload=TicketCreate(
            title="Printer problem",
            description="Printer is offline and not responding.",
            category_id=category.id,
            priority="low",
        ),
        current_user=seeded_users["employee"],
    )

    ticket = assign_ticket(
        db=db_session,
        ticket_id=ticket.id,
        payload=TicketAssignRequest(assigned_to_user_id=seeded_users["agent"].id),
        current_user=seeded_users["admin"],
    )

    ticket.status = TicketStatus.RESOLVED.value
    ticket.resolved_at = ticket.created_at
    db_session.commit()
    db_session.refresh(ticket)

    transitioned_ticket = transition_ticket_status(
        db=db_session,
        ticket_id=ticket.id,
        payload=TicketTransitionRequest(to_status=TicketStatus.CLOSED),
        current_user=seeded_users["employee"],
    )

    persisted_ticket = db_session.get(Ticket, transitioned_ticket.id)

    assert persisted_ticket is not None
    assert persisted_ticket.status == TicketStatus.CLOSED.value
    assert persisted_ticket.closed_at is not None
    assert persisted_ticket.resolved_at is not None


def test_reopening_ticket_clears_resolution_fields_in_db(db_session, seeded_users):
    category = create_active_category(db_session)

    ticket = create_ticket(
        db=db_session,
        payload=TicketCreate(
            title="Intermittent network issue",
            description="Connection drops every couple of hours.",
            category_id=category.id,
            priority="medium",
        ),
        current_user=seeded_users["employee"],
    )

    ticket = assign_ticket(
        db=db_session,
        ticket_id=ticket.id,
        payload=TicketAssignRequest(assigned_to_user_id=seeded_users["agent"].id),
        current_user=seeded_users["admin"],
    )

    ticket.status = TicketStatus.RESOLVED.value
    ticket.resolved_at = ticket.created_at
    ticket.closed_at = ticket.created_at
    db_session.commit()
    db_session.refresh(ticket)

    transitioned_ticket = transition_ticket_status(
        db=db_session,
        ticket_id=ticket.id,
        payload=TicketTransitionRequest(to_status=TicketStatus.IN_PROGRESS),
        current_user=seeded_users["employee"],
    )

    persisted_ticket = db_session.get(Ticket, transitioned_ticket.id)

    assert persisted_ticket is not None
    assert persisted_ticket.status == TicketStatus.IN_PROGRESS.value
    assert persisted_ticket.resolved_at is None
    assert persisted_ticket.closed_at is None