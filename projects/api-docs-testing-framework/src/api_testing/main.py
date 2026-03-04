"""FastAPI application with comprehensive testing."""

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest

from api_testing.models import Item, ItemCreate, User, UserCreate

# Metrics
REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total requests",
    ["method", "endpoint", "status"],
)
REQUEST_DURATION = Histogram(
    "api_request_duration_seconds",
    "Request duration",
    ["method", "endpoint"],
)

# In-memory storage (replace with database in production)
users_db: dict[str, User] = {}
items_db: dict[str, Item] = {}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager."""
    # Startup
    print("API starting up...")
    yield
    # Shutdown
    print("API shutting down...")


app = FastAPI(
    title="API Testing Framework",
    description="Production-ready API with comprehensive testing",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Track request metrics."""
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    method = request.method
    endpoint = request.url.path
    status = str(response.status_code)

    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

    return response


# Health endpoints
@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "users_count": len(users_db),
        "items_count": len(items_db),
    }


@app.get("/ready")
async def readiness_check() -> dict:
    """Readiness probe."""
    return {"ready": True}


@app.get("/metrics")
async def metrics() -> Response:
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type="text/plain",
    )


# User endpoints
@app.get("/users", response_model=list[User])
async def list_users() -> list[User]:
    """List all users."""
    return list(users_db.values())


@app.post("/users", response_model=User, status_code=201)
async def create_user(user: UserCreate) -> User:
    """Create a new user."""
    user_id = str(uuid4())
    new_user = User(id=user_id, **user.model_dump())
    users_db[user_id] = new_user
    return new_user


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str) -> User:
    """Get user by ID."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[user_id]


@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user: UserCreate) -> User:
    """Update user by ID."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    updated = User(id=user_id, **user.model_dump())
    users_db[user_id] = updated
    return updated


@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: str) -> None:
    """Delete user by ID."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    del users_db[user_id]


# Item endpoints
@app.get("/items", response_model=list[Item])
async def list_items() -> list[Item]:
    """List all items."""
    return list(items_db.values())


@app.post("/items", response_model=Item, status_code=201)
async def create_item(item: ItemCreate) -> Item:
    """Create a new item."""
    item_id = str(uuid4())
    new_item = Item(id=item_id, **item.model_dump())
    items_db[item_id] = new_item
    return new_item


@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: str) -> Item:
    """Get item by ID."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]


@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, item: ItemCreate) -> Item:
    """Update item by ID."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")

    updated = Item(id=item_id, **item.model_dump())
    items_db[item_id] = updated
    return updated


@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: str) -> None:
    """Delete item by ID."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
