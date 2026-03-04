"""Tests for API endpoints."""

import pytest
from httpx import AsyncClient

from api_testing.main import app, users_db, items_db


@pytest.fixture(autouse=True)
def clear_db():
    """Clear database before each test."""
    users_db.clear()
    items_db.clear()
    yield
    users_db.clear()
    items_db.clear()


@pytest.mark.asyncio
async def test_health_check():
    """Test health endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_ready_check():
    """Test readiness endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/ready")

    assert response.status_code == 200
    assert response.json()["ready"] is True


@pytest.mark.asyncio
async def test_metrics_endpoint():
    """Test metrics endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/metrics")

    assert response.status_code == 200
    assert "api_requests_total" in response.text


# User tests
@pytest.mark.asyncio
async def test_create_user():
    """Test creating a user."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/users", json={
            "name": "Test User",
            "email": "test@example.com",
            "role": "user",
        })

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_users():
    """Test listing users."""
    # Create a user first
    async with AsyncClient(app=app, base_url="http://test") as client:
        await client.post("/users", json={
            "name": "Test User",
            "email": "test@example.com",
        })

        response = await client.get("/users")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test User"


@pytest.mark.asyncio
async def test_get_user():
    """Test getting a user."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        create_resp = await client.post("/users", json={
            "name": "Test User",
            "email": "test@example.com",
        })
        user_id = create_resp.json()["id"]

        response = await client.get(f"/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["id"] == user_id


@pytest.mark.asyncio
async def test_get_user_not_found():
    """Test getting non-existent user."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/users/nonexistent")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_user():
    """Test updating a user."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        create_resp = await client.post("/users", json={
            "name": "Test User",
            "email": "test@example.com",
        })
        user_id = create_resp.json()["id"]

        response = await client.put(f"/users/{user_id}", json={
            "name": "Updated User",
            "email": "updated@example.com",
        })

    assert response.status_code == 200
    assert response.json()["name"] == "Updated User"


@pytest.mark.asyncio
async def test_delete_user():
    """Test deleting a user."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        create_resp = await client.post("/users", json={
            "name": "Test User",
            "email": "test@example.com",
        })
        user_id = create_resp.json()["id"]

        response = await client.delete(f"/users/{user_id}")

    assert response.status_code == 204

    # Verify deleted
    async with AsyncClient(app=app, base_url="http://test") as client:
        get_resp = await client.get(f"/users/{user_id}")
    assert get_resp.status_code == 404


# Item tests
@pytest.mark.asyncio
async def test_create_item():
    """Test creating an item."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/items", json={
            "name": "Test Item",
            "description": "A test item",
            "price": 29.99,
            "quantity": 10,
        })

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["price"] == 29.99


@pytest.mark.asyncio
async def test_list_items():
    """Test listing items."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        await client.post("/items", json={
            "name": "Test Item",
            "price": 29.99,
        })

        response = await client.get("/items")

    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_get_item():
    """Test getting an item."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        create_resp = await client.post("/items", json={
            "name": "Test Item",
            "price": 29.99,
        })
        item_id = create_resp.json()["id"]

        response = await client.get(f"/items/{item_id}")

    assert response.status_code == 200
    assert response.json()["id"] == item_id


@pytest.mark.asyncio
async def test_update_item():
    """Test updating an item."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        create_resp = await client.post("/items", json={
            "name": "Test Item",
            "price": 29.99,
        })
        item_id = create_resp.json()["id"]

        response = await client.put(f"/items/{item_id}", json={
            "name": "Updated Item",
            "price": 39.99,
        })

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Item"
    assert response.json()["price"] == 39.99


@pytest.mark.asyncio
async def test_delete_item():
    """Test deleting an item."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        create_resp = await client.post("/items", json={
            "name": "Test Item",
            "price": 29.99,
        })
        item_id = create_resp.json()["id"]

        response = await client.delete(f"/items/{item_id}")

    assert response.status_code == 204
