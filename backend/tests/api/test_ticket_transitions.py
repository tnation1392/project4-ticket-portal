import pytest

from app.constants import TicketStatus, UserRole
from app.core.security import get_password_hash
from app.db.base import utcnow
from app.models.category import Category
from app.models.ticket import Ticket
from app.models.user import User
from tests.helpers.auth import login_and_get_headers


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


def create_user(
    db_session,
    email: str,
    full_name: str,
    role: str,
) -> User:
    user = User(
        email=email,
        password_hash=get_password_hash("password123"),
        full_name=full_name,
        role=role,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def create_ticket(
    db_session,
    category: Category,
    created_by_user_id: int,
    title: str = "Test Ticket",
    status: str = "new",
    assigned_to_user_id: int | None = None,
    resolved_at=None,
    closed_at=None,
) -> Ticket:
    ticket = Ticket(
        title=title,
        description="Ticket description",
        category_id=category.id,
        priority="medium",
        status=status,
        created_by_user_id=created_by_user_id,
        assigned_to_user_id=assigned_to_user_id,
        resolved_at=resolved_at,
        closed_at=closed_at,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)
    return ticket


@pytest.mark.asyncio
async def test_agent_can_transition_new_to_triaged(client, seeded_users, db_session):
    category = create_active_category(db_session)
    ticket = create_ticket(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        status=TicketStatus.NEW.value,
        title="New Ticket",
    )

    headers = await login_and_get_headers(
        client,
        email="agent1@example.com",
        password="password123",
    )

    response = await client.post(
        f"/tickets/{ticket.id}/transition",
        headers=headers,
        json={"to_status": TicketStatus.TRIAGED.value},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["id"] == ticket.id
    assert body["status"] == TicketStatus.TRIAGED.value


@pytest.mark.asyncio
async def test_invalid_transition_is_rejected(client, seeded_users, db_session):
    category = create_active_category(db_session)
    ticket = create_ticket(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        status=TicketStatus.NEW.value,
        title="Invalid Transition Ticket",
    )

    headers = await login_and_get_headers(
        client,
        email="agent1@example.com",
        password="password123",
    )

    response = await client.post(
        f"/tickets/{ticket.id}/transition",
        headers=headers,
        json={"to_status": TicketStatus.RESOLVED.value},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot transition ticket from new to resolved"


@pytest.mark.asyncio
async def test_employee_cannot_do_support_side_transition(client, seeded_users, db_session):
    category = create_active_category(db_session)
    ticket = create_ticket(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        status=TicketStatus.NEW.value,
        title="Employee Transition Attempt",
    )

    headers = await login_and_get_headers(
        client,
        email="employee1@example.com",
        password="password123",
    )

    response = await client.post(
        f"/tickets/{ticket.id}/transition",
        headers=headers,
        json={"to_status": TicketStatus.TRIAGED.value},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to perform this transition"


@pytest.mark.asyncio
async def test_in_progress_requires_assignment(client, seeded_users, db_session):
    category = create_active_category(db_session)
    ticket = create_ticket(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        status=TicketStatus.TRIAGED.value,
        assigned_to_user_id=None,
        title="Unassigned Triaged Ticket",
    )

    headers = await login_and_get_headers(
        client,
        email="agent1@example.com",
        password="password123",
    )

    response = await client.post(
        f"/tickets/{ticket.id}/transition",
        headers=headers,
        json={"to_status": TicketStatus.IN_PROGRESS.value},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Ticket must be assigned before moving to in_progress"


@pytest.mark.asyncio
async def test_agent_can_transition_assigned_ticket_to_in_progress(client, seeded_users, db_session):
    category = create_active_category(db_session)
    ticket = create_ticket(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        status=TicketStatus.TRIAGED.value,
        assigned_to_user_id=seeded_users["agent"].id,
        title="Assigned Triaged Ticket",
    )

    headers = await login_and_get_headers(
        client,
        email="agent1@example.com",
        password="password123",
    )

    response = await client.post(
        f"/tickets/{ticket.id}/transition",
        headers=headers,
        json={"to_status": TicketStatus.IN_PROGRESS.value},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == TicketStatus.IN_PROGRESS.value


@pytest.mark.asyncio
async def test_resolving_ticket_sets_resolved_at(client, seeded_users, db_session):
    category = create_active_category(db_session)
    ticket = create_ticket(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        status=TicketStatus.IN_PROGRESS.value,
        assigned_to_user_id=seeded_users["agent"].id,
        title="Resolvable Ticket",
    )

    headers = await login_and_get_headers(
        client,
        email="agent1@example.com",
        password="password123",
    )

    response = await client.post(
        f"/tickets/{ticket.id}/transition",
        headers=headers,
        json={"to_status": TicketStatus.RESOLVED.value},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == TicketStatus.RESOLVED.value
    assert body["resolved_at"] is not None


@pytest.mark.asyncio
async def test_employee_can_close_own_resolved_ticket_and_sets_closed_at(client, seeded_users, db_session):
    category = create_active_category(db_session)
    ticket = create_ticket(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        status=TicketStatus.RESOLVED.value,
        assigned_to_user_id=seeded_users["agent"].id,
        resolved_at=utcnow(),
        title="Resolved Ticket",
    )

    headers = await login_and_get_headers(
        client,
        email="employee1@example.com",
        password="password123",
    )

    response = await client.post(
        f"/tickets/{ticket.id}/transition",
        headers=headers,
        json={"to_status": TicketStatus.CLOSED.value},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == TicketStatus.CLOSED.value
    assert body["closed_at"] is not None


@pytest.mark.asyncio
async def test_employee_can_reopen_own_resolved_ticket(client, seeded_users, db_session):
    category = create_active_category(db_session)
    ticket = create_ticket(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        status=TicketStatus.RESOLVED.value,
        assigned_to_user_id=seeded_users["agent"].id,
        resolved_at=utcnow(),
        title="Reopenable Ticket",
    )

    headers = await login_and_get_headers(
        client,
        email="employee1@example.com",
        password="password123",
    )

    response = await client.post(
        f"/tickets/{ticket.id}/transition",
        headers=headers,
        json={"to_status": TicketStatus.IN_PROGRESS.value},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == TicketStatus.IN_PROGRESS.value
    assert body["resolved_at"] is None
    assert body["closed_at"] is None


@pytest.mark.asyncio
async def test_admin_can_perform_valid_transition(client, seeded_users, db_session):
    category = create_active_category(db_session)
    ticket = create_ticket(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        status=TicketStatus.NEW.value,
        title="Admin Transition Ticket",
    )

    headers = await login_and_get_headers(
        client,
        email="admin1@example.com",
        password="password123",
    )

    response = await client.post(
        f"/tickets/{ticket.id}/transition",
        headers=headers,
        json={"to_status": TicketStatus.TRIAGED.value},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == TicketStatus.TRIAGED.value


@pytest.mark.asyncio
async def test_employee_cannot_transition_another_employees_ticket(client, seeded_users, db_session):
    category = create_active_category(db_session)
    other_employee = create_user(
        db_session,
        email="employee2@example.com",
        full_name="Employee Two",
        role=UserRole.EMPLOYEE.value,
    )
    ticket = create_ticket(
        db_session,
        category=category,
        created_by_user_id=other_employee.id,
        status=TicketStatus.RESOLVED.value,
        assigned_to_user_id=seeded_users["agent"].id,
        resolved_at=utcnow(),
        title="Other Employee Resolved Ticket",
    )

    headers = await login_and_get_headers(
        client,
        email="employee1@example.com",
        password="password123",
    )

    response = await client.post(
        f"/tickets/{ticket.id}/transition",
        headers=headers,
        json={"to_status": TicketStatus.CLOSED.value},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to view this ticket"
