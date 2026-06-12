import pytest

from app.constants import UserRole
from app.core.security import get_password_hash
from app.models import Ticket
from app.models.user import User
from tests.helpers.auth import login_and_get_headers
from app.models.category import Category


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


def create_ticket_for_user(
    db_session,
    category: Category,
    created_by_user_id: int,
    title: str = "Test Ticket",
    assigned_to_user_id: int | None = None,
) -> Ticket:
    ticket = Ticket(
        title=title,
        description="Ticket description",
        category_id=category.id,
        priority="medium",
        status="new",
        created_by_user_id=created_by_user_id,
        assigned_to_user_id=assigned_to_user_id,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)
    return ticket


@pytest.mark.asyncio
async def test_agent_can_self_assign_unassigned_ticket(client, seeded_users, db_session):
    category = create_active_category(db_session)
    ticket = create_ticket_for_user(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        title="Unassigned Ticket",
    )

    headers = await login_and_get_headers(
        client,
        email="agent1@example.com",
        password="password123",
    )

    response = await client.post(
        f"/tickets/{ticket.id}/assign",
        headers=headers,
        json={"assigned_to_user_id": seeded_users["agent"].id},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["id"] == ticket.id
    assert body["assigned_to_user_id"] == seeded_users["agent"].id


@pytest.mark.asyncio
async def test_agent_cannot_assign_ticket_to_another_agent(client, seeded_users, db_session):
    category = create_active_category(db_session)
    other_agent = create_user(
        db_session,
        email="agent2@example.com",
        full_name="Agent Two",
        role=UserRole.AGENT.value,
    )
    ticket = create_ticket_for_user(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        title="Unassigned Ticket",
    )

    headers = await login_and_get_headers(
        client,
        email="agent1@example.com",
        password="password123",
    )

    response = await client.post(
        f"/tickets/{ticket.id}/assign",
        headers=headers,
        json={"assigned_to_user_id": other_agent.id},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Agents can only assign tickets to themselves"


@pytest.mark.asyncio
async def test_agent_cannot_self_assign_already_assigned_ticket(client, seeded_users, db_session):
    category = create_active_category(db_session)
    other_agent = create_user(
        db_session,
        email="agent2@example.com",
        full_name="Agent Two",
        role=UserRole.AGENT.value,
    )
    ticket = create_ticket_for_user(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        title="Already Assigned Ticket",
        assigned_to_user_id=other_agent.id,
    )

    headers = await login_and_get_headers(
        client,
        email="agent1@example.com",
        password="password123",
    )

    response = await client.post(
        f"/tickets/{ticket.id}/assign",
        headers=headers,
        json={"assigned_to_user_id": seeded_users["agent"].id},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Ticket is already assigned"


@pytest.mark.asyncio
async def test_admin_can_assign_ticket_to_any_agent(client, seeded_users, db_session):
    category = create_active_category(db_session)
    other_agent = create_user(
        db_session,
        email="agent2@example.com",
        full_name="Agent Two",
        role=UserRole.AGENT.value,
    )
    ticket = create_ticket_for_user(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        title="Admin Assignment Ticket",
    )

    headers = await login_and_get_headers(
        client,
        email="admin1@example.com",
        password="password123",
    )

    response = await client.post(
        f"/tickets/{ticket.id}/assign",
        headers=headers,
        json={"assigned_to_user_id": other_agent.id},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["id"] == ticket.id
    assert body["assigned_to_user_id"] == other_agent.id


@pytest.mark.asyncio
async def test_employee_cannot_assign_ticket(client, seeded_users, db_session):
    category = create_active_category(db_session)
    ticket = create_ticket_for_user(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        title="Employee Assignment Attempt",
    )

    headers = await login_and_get_headers(
        client,
        email="employee1@example.com",
        password="password123",
    )

    response = await client.post(
        f"/tickets/{ticket.id}/assign",
        headers=headers,
        json={"assigned_to_user_id": seeded_users["agent"].id},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to assign tickets"


@pytest.mark.asyncio
async def test_cannot_assign_ticket_to_nonexistent_user(client, seeded_users, db_session):
    category = create_active_category(db_session)
    ticket = create_ticket_for_user(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        title="Nonexistent Assignee Ticket",
    )

    headers = await login_and_get_headers(
        client,
        email="admin1@example.com",
        password="password123",
    )

    response = await client.post(
        f"/tickets/{ticket.id}/assign",
        headers=headers,
        json={"assigned_to_user_id": 99999},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Assigned user not found"


@pytest.mark.asyncio
async def test_cannot_assign_ticket_to_employee_user(client, seeded_users, db_session):
    category = create_active_category(db_session)
    other_employee = create_user(
        db_session,
        email="employee2@example.com",
        full_name="Employee Two",
        role=UserRole.EMPLOYEE.value,
    )
    ticket = create_ticket_for_user(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        title="Invalid Assignee Role Ticket",
    )

    headers = await login_and_get_headers(
        client,
        email="admin1@example.com",
        password="password123",
    )

    response = await client.post(
        f"/tickets/{ticket.id}/assign",
        headers=headers,
        json={"assigned_to_user_id": other_employee.id},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Assigned user must have agent role"
from app.models.category import Category
