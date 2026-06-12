import pytest

from app.models.category import Category
from tests.helpers.auth import login_and_get_headers


@pytest.mark.asyncio
async def test_authenticated_user_can_list_active_categories(client, seeded_users, db_session):
    db_session.add_all(
        [
            Category(name="Hardware", description="Hardware issues", is_active=True),
            Category(name="Software", description="Software issues", is_active=True),
            Category(name="Old Category", description="Inactive", is_active=False),
        ]
    )
    db_session.commit()

    headers = await login_and_get_headers(
        client,
        email="employee1@example.com",
        password="password123",
    )

    response = await client.get("/categories", headers=headers)

    assert response.status_code == 200
    body = response.json()

    names = [item["name"] for item in body]

    assert "Hardware" in names
    assert "Software" in names
    assert "Old Category" not in names


@pytest.mark.asyncio
async def test_admin_can_create_category(client, seeded_users):
    headers = await login_and_get_headers(
        client,
        email="admin1@example.com",
        password="password123",
    )

    response = await client.post(
        "/categories",
        headers=headers,
        json={
            "name": "Network",
            "description": "Network-related issues",
        },
    )

    assert response.status_code == 201
    body = response.json()

    assert body["name"] == "Network"
    assert body["description"] == "Network-related issues"
    assert body["is_active"] is True


@pytest.mark.asyncio
async def test_employee_cannot_create_category(client, seeded_users):
    headers = await login_and_get_headers(
        client,
        email="employee1@example.com",
        password="password123",
    )

    response = await client.post(
        "/categories",
        headers=headers,
        json={
            "name": "Access Request",
            "description": "Permissions and access issues",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


@pytest.mark.asyncio
async def test_admin_can_deactivate_category(client, seeded_users, db_session):
    category = Category(
        name="Temporary Category",
        description="Will be deactivated",
        is_active=True,
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    headers = await login_and_get_headers(
        client,
        email="admin1@example.com",
        password="password123",
    )

    response = await client.patch(
        f"/categories/{category.id}",
        headers=headers,
        json={"is_active": False},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["id"] == category.id
    assert body["is_active"] is False


@pytest.mark.asyncio
async def test_inactive_category_no_longer_shows_in_list(client, seeded_users, db_session):
    active_category = Category(
        name="Hardware",
        description="Hardware issues",
        is_active=True,
    )
    inactive_category = Category(
        name="Archived Category",
        description="Should not appear",
        is_active=False,
    )
    db_session.add_all([active_category, inactive_category])
    db_session.commit()

    headers = await login_and_get_headers(
        client,
        email="agent1@example.com",
        password="password123",
    )

    response = await client.get("/categories", headers=headers)

    assert response.status_code == 200
    body = response.json()

    names = [item["name"] for item in body]

    assert "Hardware" in names
    assert "Archived Category" not in names