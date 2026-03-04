"""Pydantic models for API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user model."""

    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    role: str = Field(default="user", pattern="^(admin|user|guest)$")


class UserCreate(UserBase):
    """User creation model."""

    pass


class User(UserBase):
    """User response model."""

    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class ItemBase(BaseModel):
    """Base item model."""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    price: float = Field(..., gt=0)
    quantity: int = Field(default=0, ge=0)
    category: str = Field(default="general")


class ItemCreate(ItemBase):
    """Item creation model."""

    pass


class Item(ItemBase):
    """Item response model."""

    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    users_count: int
    items_count: int


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str
