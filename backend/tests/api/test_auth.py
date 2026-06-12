import pytest

from tests.helpers.auth import login_and_get_headers


@pytest.mark.asyncio
async def test_login_returns_token_and_user(client, seeded_users):
    response = await client.post(
        "/auth/login",
        json={
            "email": "employee1@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "employee1@example.com"
    assert body["user"]["role"] == "employee"


@pytest.mark.asyncio
async def test_login_rejects_invalid_password(client, seeded_users):
    response = await client.post(
        "/auth/login",
        json={
            "email": "employee1@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_auth_me_requires_token(client, seeded_users):
    response = await client.get("/auth/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_auth_me_returns_current_user(client, seeded_users):
    headers = await login_and_get_headers(
        client,
        email="admin1@example.com",
        password="password123",
    )

    response = await client.get("/auth/me", headers=headers)

    assert response.status_code == 200
    body = response.json()

    assert body["email"] == "admin1@example.com"
    assert body["role"] == "admin"
    assert body["full_name"] == "Admin One"