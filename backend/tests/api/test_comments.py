import pytest

from app.constants import UserRole
from app.core.security import get_password_hash
from app.models.category import Category
from app.models.comment import Comment
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


def create_employee(db_session, email: str, full_name: str) -> User:
    user = User(
        email=email,
        password_hash=get_password_hash("password123"),
        full_name=full_name,
        role=UserRole.EMPLOYEE.value,
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
) -> Ticket:
    ticket = Ticket(
        title=title,
        description="Ticket description",
        category_id=category.id,
        priority="medium",
        status="new",
        created_by_user_id=created_by_user_id,
        assigned_to_user_id=None,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)
    return ticket


@pytest.mark.asyncio
async def test_employee_can_add_public_comment(client, seeded_users, db_session):
    category = create_active_category(db_session)
    ticket = create_ticket_for_user(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        title="Employee Ticket",
    )

    headers = await login_and_get_headers(
        client,
        email="employee1@example.com",
        password="password123",
    )

    response = await client.post(
        f"/tickets/{ticket.id}/comments",
        headers=headers,
        json={
            "body": "Here is more information about the issue.",
            "is_internal": False,
        },
    )

    assert response.status_code == 201
    body = response.json()

    assert body["ticket_id"] == ticket.id
    assert body["author_user_id"] == seeded_users["employee"].id
    assert body["body"] == "Here is more information about the issue."
    assert body["is_internal"] is False


@pytest.mark.asyncio
async def test_employee_cannot_add_internal_comment(client, seeded_users, db_session):
    category = create_active_category(db_session)
    ticket = create_ticket_for_user(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        title="Employee Ticket",
    )

    headers = await login_and_get_headers(
        client,
        email="employee1@example.com",
        password="password123",
    )

    response = await client.post(
        f"/tickets/{ticket.id}/comments",
        headers=headers,
        json={
            "body": "Internal note that should not be allowed.",
            "is_internal": True,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Employees cannot create internal comments"


@pytest.mark.asyncio
async def test_agent_can_add_internal_comment(client, seeded_users, db_session):
    category = create_active_category(db_session)
    ticket = create_ticket_for_user(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        title="Employee Ticket",
    )

    headers = await login_and_get_headers(
        client,
        email="agent1@example.com",
        password="password123",
    )

    response = await client.post(
        f"/tickets/{ticket.id}/comments",
        headers=headers,
        json={
            "body": "Internal troubleshooting note.",
            "is_internal": True,
        },
    )

    assert response.status_code == 201
    body = response.json()

    assert body["ticket_id"] == ticket.id
    assert body["author_user_id"] == seeded_users["agent"].id
    assert body["body"] == "Internal troubleshooting note."
    assert body["is_internal"] is True


@pytest.mark.asyncio
async def test_admin_can_add_internal_comment(client, seeded_users, db_session):
    category = create_active_category(db_session)
    ticket = create_ticket_for_user(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        title="Employee Ticket",
    )

    headers = await login_and_get_headers(
        client,
        email="admin1@example.com",
        password="password123",
    )

    response = await client.post(
        f"/tickets/{ticket.id}/comments",
        headers=headers,
        json={
            "body": "Admin internal note.",
            "is_internal": True,
        },
    )

    assert response.status_code == 201
    body = response.json()

    assert body["author_user_id"] == seeded_users["admin"].id
    assert body["is_internal"] is True


@pytest.mark.asyncio
async def test_employee_sees_only_public_comments(client, seeded_users, db_session):
    category = create_active_category(db_session)
    ticket = create_ticket_for_user(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        title="Employee Ticket",
    )

    public_comment = Comment(
        ticket_id=ticket.id,
        author_user_id=seeded_users["agent"].id,
        body="Public update for the employee.",
        is_internal=False,
    )
    internal_comment = Comment(
        ticket_id=ticket.id,
        author_user_id=seeded_users["agent"].id,
        body="Internal support note.",
        is_internal=True,
    )
    db_session.add_all([public_comment, internal_comment])
    db_session.commit()

    headers = await login_and_get_headers(
        client,
        email="employee1@example.com",
        password="password123",
    )

    response = await client.get(f"/tickets/{ticket.id}/comments", headers=headers)

    assert response.status_code == 200
    body = response.json()

    comment_bodies = [comment["body"] for comment in body]

    assert "Public update for the employee." in comment_bodies
    assert "Internal support note." not in comment_bodies


@pytest.mark.asyncio
async def test_agent_sees_public_and_internal_comments(client, seeded_users, db_session):
    category = create_active_category(db_session)
    ticket = create_ticket_for_user(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        title="Employee Ticket",
    )

    public_comment = Comment(
        ticket_id=ticket.id,
        author_user_id=seeded_users["employee"].id,
        body="Public comment from employee.",
        is_internal=False,
    )
    internal_comment = Comment(
        ticket_id=ticket.id,
        author_user_id=seeded_users["admin"].id,
        body="Internal admin note.",
        is_internal=True,
    )
    db_session.add_all([public_comment, internal_comment])
    db_session.commit()

    headers = await login_and_get_headers(
        client,
        email="agent1@example.com",
        password="password123",
    )

    response = await client.get(f"/tickets/{ticket.id}/comments", headers=headers)

    assert response.status_code == 200
    body = response.json()

    comment_bodies = [comment["body"] for comment in body]

    assert "Public comment from employee." in comment_bodies
    assert "Internal admin note." in comment_bodies


@pytest.mark.asyncio
async def test_admin_sees_public_and_internal_comments(client, seeded_users, db_session):
    category = create_active_category(db_session)
    ticket = create_ticket_for_user(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        title="Employee Ticket",
    )

    db_session.add_all(
        [
            Comment(
                ticket_id=ticket.id,
                author_user_id=seeded_users["employee"].id,
                body="Public comment",
                is_internal=False,
            ),
            Comment(
                ticket_id=ticket.id,
                author_user_id=seeded_users["agent"].id,
                body="Internal comment",
                is_internal=True,
            ),
        ]
    )
    db_session.commit()

    headers = await login_and_get_headers(
        client,
        email="admin1@example.com",
        password="password123",
    )

    response = await client.get(f"/tickets/{ticket.id}/comments", headers=headers)

    assert response.status_code == 200
    body = response.json()

    comment_bodies = [comment["body"] for comment in body]

    assert "Public comment" in comment_bodies
    assert "Internal comment" in comment_bodies


@pytest.mark.asyncio
async def test_employee_cannot_comment_on_another_employees_ticket(client, seeded_users, db_session):
    category = create_active_category(db_session)
    other_employee = create_employee(
        db_session,
        email="employee2@example.com",
        full_name="Employee Two",
    )
    ticket = create_ticket_for_user(
        db_session,
        category=category,
        created_by_user_id=other_employee.id,
        title="Other Employee Ticket",
    )

    headers = await login_and_get_headers(
        client,
        email="employee1@example.com",
        password="password123",
    )

    response = await client.post(
        f"/tickets/{ticket.id}/comments",
        headers=headers,
        json={
            "body": "I should not be able to post here.",
            "is_internal": False,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to view this ticket"


@pytest.mark.asyncio
async def test_employee_cannot_view_comments_on_another_employees_ticket(client, seeded_users, db_session):
    category = create_active_category(db_session)
    other_employee = create_employee(
        db_session,
        email="employee2@example.com",
        full_name="Employee Two",
    )
    ticket = create_ticket_for_user(
        db_session,
        category=category,
        created_by_user_id=other_employee.id,
        title="Other Employee Ticket",
    )

    db_session.add(
        Comment(
            ticket_id=ticket.id,
            author_user_id=seeded_users["agent"].id,
            body="Agent note on another employee ticket.",
            is_internal=False,
        )
    )
    db_session.commit()

    headers = await login_and_get_headers(
        client,
        email="employee1@example.com",
        password="password123",
    )

    response = await client.get(f"/tickets/{ticket.id}/comments", headers=headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to view this ticket"


@pytest.mark.asyncio
async def test_comment_body_cannot_be_empty(client, seeded_users, db_session):
    category = create_active_category(db_session)
    ticket = create_ticket_for_user(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        title="Employee Ticket",
    )

    headers = await login_and_get_headers(
        client,
        email="employee1@example.com",
        password="password123",
    )

    response = await client.post(
        f"/tickets/{ticket.id}/comments",
        headers=headers,
        json={
            "body": "   ",
            "is_internal": False,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Comment body cannot be empty"
