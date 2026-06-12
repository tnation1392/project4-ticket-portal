async def login_and_get_headers(client, email: str, password: str) -> dict[str, str]:
    response = await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200, response.text

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}