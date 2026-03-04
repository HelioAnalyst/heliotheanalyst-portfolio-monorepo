#!/usr/bin/env python3
"""Demo script for API Docs & Testing Framework."""

import asyncio
import sys

sys.path.insert(0, "src")

import httpx

BASE_URL = "http://localhost:8000"


async def run_demo() -> None:
    """Run API demo."""
    print("=" * 60)
    print("API Docs & Testing Framework - Demo")
    print("=" * 60)
    print()

    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Health check
        print("1. Health Check")
        print("-" * 40)
        response = await client.get("/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()

        # Create users
        print("2. Create Users")
        print("-" * 40)
        users = [
            {"name": "Alice", "email": "alice@example.com", "role": "admin"},
            {"name": "Bob", "email": "bob@example.com", "role": "user"},
            {"name": "Charlie", "email": "charlie@example.com", "role": "user"},
        ]

        created_users = []
        for user in users:
            response = await client.post("/users", json=user)
            data = response.json()
            created_users.append(data)
            print(f"Created: {data['name']} (ID: {data['id'][:8]}...)")
        print()

        # List users
        print("3. List Users")
        print("-" * 40)
        response = await client.get("/users")
        data = response.json()
        print(f"Total users: {len(data)}")
        for user in data:
            print(f"  - {user['name']} ({user['email']})")
        print()

        # Create items
        print("4. Create Items")
        print("-" * 40)
        items = [
            {"name": "Laptop", "description": "High-performance laptop", "price": 999.99, "quantity": 10},
            {"name": "Mouse", "description": "Wireless mouse", "price": 29.99, "quantity": 50},
            {"name": "Keyboard", "description": "Mechanical keyboard", "price": 149.99, "quantity": 25},
        ]

        created_items = []
        for item in items:
            response = await client.post("/items", json=item)
            data = response.json()
            created_items.append(data)
            print(f"Created: {data['name']} - ${data['price']}")
        print()

        # List items
        print("5. List Items")
        print("-" * 40)
        response = await client.get("/items")
        data = response.json()
        print(f"Total items: {len(data)}")
        for item in data:
            print(f"  - {item['name']}: ${item['price']} (qty: {item['quantity']})")
        print()

        # Update user
        print("6. Update User")
        print("-" * 40)
        user_id = created_users[0]["id"]
        response = await client.put(f"/users/{user_id}", json={
            "name": "Alice Updated",
            "email": "alice.updated@example.com",
            "role": "admin",
        })
        print(f"Updated: {response.json()['name']}")
        print()

        # Get metrics
        print("7. Metrics")
        print("-" * 40)
        response = await client.get("/metrics")
        print(f"Status: {response.status_code}")
        print("Prometheus metrics available at /metrics")
        print()

        # Delete item
        print("8. Delete Item")
        print("-" * 40)
        item_id = created_items[0]["id"]
        response = await client.delete(f"/items/{item_id}")
        print(f"Deleted item (Status: {response.status_code})")
        print()

    print("=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)
    print()
    print("API Documentation:")
    print(f"  Swagger UI: {BASE_URL}/docs")
    print(f"  ReDoc: {BASE_URL}/redoc")
    print()
    print("To run tests:")
    print("  pytest tests/ -v --cov=src --cov-report=html")


if __name__ == "__main__":
    asyncio.run(run_demo())
