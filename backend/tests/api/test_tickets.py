import pytest

from app.constants import TicketStatus, UserRole
from app.models.category import Category
from app.models.ticket import Ticket
from app.models.user import User
from tests.helpers.auth import login_and_get_headers


@pytest.mark.asyncio
async def test_employee_can_create_ticket(client, seeded_users, db_session):
    category = Category(
        name="Hardware",
        description="Hardware issues",
        is_active=True,
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    headers = await login_and_get_headers(
        client,
        email="employee1@example.com",
        password="password123",
    )

    response = await client.post(
        "/tickets",
        headers=headers,
        json={
            "title": "Laptop screen flickering",
            "description": "The screen flickers when opening the laptop.",
            "category_id": category.id,
            "priority": "high",
        },
    )

    assert response.status_code == 201
    body = response.json()

    assert body["title"] == "Laptop screen flickering"
    assert body["description"] == "The screen flickers when opening the laptop."
    assert body["category_id"] == category.id
    assert body["priority"] == "high"
    assert body["status"] == "new"
    assert body["created_by_user_id"] == seeded_users["employee"].id
    assert body["assigned_to_user_id"] is None


@pytest.mark.asyncio
async def test_ticket_defaults_to_new_status(client, seeded_users, db_session):
    category = Category(
        name="Software",
        description="Software issues",
        is_active=True,
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    headers = await login_and_get_headers(
        client,
        email="employee1@example.com",
        password="password123",
    )

    response = await client.post(
        "/tickets",
        headers=headers,
        json={
            "title": "Application crashes",
            "description": "The application crashes on launch.",
            "category_id": category.id,
            "priority": "medium",
        },
    )

    assert response.status_code == 201
    body = response.json()

    assert body["status"] == TicketStatus.NEW.value


@pytest.mark.asyncio
async def test_cannot_create_ticket_with_missing_category(client, seeded_users):
    headers = await login_and_get_headers(
        client,
        email="employee1@example.com",
        password="password123",
    )

    response = await client.post(
        "/tickets",
        headers=headers,
        json={
            "title": "VPN issue",
            "description": "Cannot connect to VPN.",
            "category_id": 9999,
            "priority": "high",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


@pytest.mark.asyncio
async def test_cannot_create_ticket_with_inactive_category(client, seeded_users, db_session):
    category = Category(
        name="Old Category",
        description="Inactive category",
        is_active=False,
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    headers = await login_and_get_headers(
        client,
        email="employee1@example.com",
        password="password123",
    )

    response = await client.post(
        "/tickets",
        headers=headers,
        json={
            "title": "Printer issue",
            "description": "Printer is offline.",
            "category_id": category.id,
            "priority": "low",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Category is inactive"


@pytest.mark.asyncio
async def test_employee_list_shows_only_own_tickets(client, seeded_users, db_session):
    category = Category(
        name="Access Request",
        description="Access-related issues",
        is_active=True,
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    employee_user = seeded_users["employee"]

    other_employee = User(
        email="employee2@example.com",
        password_hash=seeded_users["employee"].password_hash,
        full_name="Employee Two",
        role=UserRole.EMPLOYEE.value,
        is_active=True,
    )
    db_session.add(other_employee)
    db_session.commit()
    db_session.refresh(other_employee)

    own_ticket = Ticket(
        title="Own Ticket",
        description="Visible to employee one.",
        category_id=category.id,
        priority="medium",
        status="new",
        created_by_user_id=employee_user.id,
        assigned_to_user_id=None,
    )
    other_ticket = Ticket(
        title="Other Ticket",
        description="Should not be visible to employee one.",
        category_id=category.id,
        priority="high",
        status="new",
        created_by_user_id=other_employee.id,
        assigned_to_user_id=None,
    )
    db_session.add_all([own_ticket, other_ticket])
    db_session.commit()

    headers = await login_and_get_headers(
        client,
        email="employee1@example.com",
        password="password123",
    )

    response = await client.get("/tickets", headers=headers)

    assert response.status_code == 200
    body = response.json()

    titles = [ticket["title"] for ticket in body]

    assert "Own Ticket" in titles
    assert "Other Ticket" not in titles


@pytest.mark.asyncio
async def test_admin_list_shows_all_tickets(client, seeded_users, db_session):
    category = Category(
        name="Network",
        description="Network issues",
        is_active=True,
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    other_employee = User(
        email="employee2@example.com",
        password_hash=seeded_users["employee"].password_hash,
        full_name="Employee Two",
        role=UserRole.EMPLOYEE.value,
        is_active=True,
    )
    db_session.add(other_employee)
    db_session.commit()
    db_session.refresh(other_employee)

    ticket_one = Ticket(
        title="Employee One Ticket",
        description="Created by employee one.",
        category_id=category.id,
        priority="low",
        status="new",
        created_by_user_id=seeded_users["employee"].id,
        assigned_to_user_id=None,
    )
    ticket_two = Ticket(
        title="Employee Two Ticket",
        description="Created by employee two.",
        category_id=category.id,
        priority="urgent",
        status="new",
        created_by_user_id=other_employee.id,
        assigned_to_user_id=None,
    )
    db_session.add_all([ticket_one, ticket_two])
    db_session.commit()

    headers = await login_and_get_headers(
        client,
        email="admin1@example.com",
        password="password123",
    )

    response = await client.get("/tickets", headers=headers)

    assert response.status_code == 200
    body = response.json()

    titles = [ticket["title"] for ticket in body]

    assert "Employee One Ticket" in titles
    assert "Employee Two Ticket" in titles


@pytest.mark.asyncio
async def test_employee_can_view_own_ticket_detail(client, seeded_users, db_session):
    category = Category(
        name="Hardware",
        description="Hardware issues",
        is_active=True,
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    ticket = Ticket(
        title="Keyboard issue",
        description="Some keys are not responding.",
        category_id=category.id,
        priority="medium",
        status="new",
        created_by_user_id=seeded_users["employee"].id,
        assigned_to_user_id=None,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    headers = await login_and_get_headers(
        client,
        email="employee1@example.com",
        password="password123",
    )

    response = await client.get(f"/tickets/{ticket.id}", headers=headers)

    assert response.status_code == 200
    body = response.json()

    assert body["id"] == ticket.id
    assert body["title"] == "Keyboard issue"


@pytest.mark.asyncio
async def test_employee_cannot_view_another_employees_ticket_detail(client, seeded_users, db_session):
    category = Category(
        name="Software",
        description="Software issues",
        is_active=True,
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    other_employee = User(
        email="employee2@example.com",
        password_hash=seeded_users["employee"].password_hash,
        full_name="Employee Two",
        role=UserRole.EMPLOYEE.value,
        is_active=True,
    )
    db_session.add(other_employee)
    db_session.commit()
    db_session.refresh(other_employee)

    ticket = Ticket(
        title="Other employee ticket",
        description="Should not be visible.",
        category_id=category.id,
        priority="high",
        status="new",
        created_by_user_id=other_employee.id,
        assigned_to_user_id=None,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    headers = await login_and_get_headers(
        client,
        email="employee1@example.com",
        password="password123",
    )

    response = await client.get(f"/tickets/{ticket.id}", headers=headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to view this ticket"


@pytest.mark.asyncio
async def test_admin_can_view_any_ticket_detail(client, seeded_users, db_session):
    category = Category(
        name="Access Request",
        description="Access issues",
        is_active=True,
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    ticket = Ticket(
        title="Payroll folder access",
        description="Access needed for payroll folder.",
        category_id=category.id,
        priority="high",
        status="new",
        created_by_user_id=seeded_users["employee"].id,
        assigned_to_user_id=None,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    headers = await login_and_get_headers(
        client,
        email="admin1@example.com",
        password="password123",
    )

    response = await client.get(f"/tickets/{ticket.id}", headers=headers)

    assert response.status_code == 200
    body = response.json()

    assert body["id"] == ticket.id
    assert body["title"] == "Payroll folder access"