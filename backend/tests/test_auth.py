import pytest
from app.core.security import hash_password

@pytest.mark.asyncio
async def test_register_user(client, mock_db):
    # Principal/Admin role check is enforced via require_roles
    # For testing simpler, we might need to mock the get_current_user dependency or provide a token
    # But let's first test the response when no auth is provided (should be 403 or 401)
    response = await client.post("/api/auth/register", json={
        "email": "test@example.com",
        "name": "Test User",
        "password": "Password123",
        "role": "student"
    })
    # Since we restricted it to principal/admin in previous steps
    assert response.status_code in [401, 403]

@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    response = await client.post("/api/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword",
        "role": "student"
    })
    print(f"DEBUG LOGIN: {response.status_code} {response.json()}")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
