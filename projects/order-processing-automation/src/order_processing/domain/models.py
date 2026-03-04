"""Domain models for order processing."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class OrderStatus(str, Enum):
    """Order processing status."""

    PENDING = "pending"
    VALIDATING = "validating"
    VALIDATED = "validated"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class Provider(str, Enum):
    """Fulfillment providers."""

    PROVIDER_A = "provider_a"
    PROVIDER_B = "provider_b"
    PROVIDER_C = "provider_c"
    INTERNAL = "internal"


class OrderItem(BaseModel):
    """Order line item."""

    model_config = ConfigDict(frozen=True)

    product_id: str
    sku: str
    name: str
    quantity: int = Field(ge=1)
    unit_price: Decimal
    total_price: Decimal
    metadata: dict[str, Any] = Field(default_factory=dict)


class ShippingAddress(BaseModel):
    """Shipping address."""

    model_config = ConfigDict(frozen=True)

    name: str
    line1: str
    line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str = "US"
    phone: Optional[str] = None


class Order(BaseModel):
    """Order model."""

    model_config = ConfigDict(frozen=True)

    id: Optional[str] = None
    idempotency_key: str
    customer_id: str
    customer_email: str
    items: list[OrderItem]
    shipping_address: ShippingAddress
    subtotal: Decimal
    tax: Decimal
    shipping_cost: Decimal
    total: Decimal
    currency: str = "USD"
    status: OrderStatus = OrderStatus.PENDING
    provider: Optional[Provider] = None
    provider_order_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    failure_reason: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None


class ProcessingResult(BaseModel):
    """Order processing result."""

    model_config = ConfigDict(frozen=True)

    order_id: str
    success: bool
    status: OrderStatus
    provider: Optional[Provider] = None
    provider_order_id: Optional[str] = None
    message: str
    processed_at: datetime = Field(default_factory=datetime.utcnow)


class JobStatus(BaseModel):
    """Background job status."""

    model_config = ConfigDict(frozen=True)

    job_id: str
    order_id: str
    status: str  # pending, started, success, failure, retry
    task_name: str
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class DashboardMetrics(BaseModel):
    """Dashboard metrics."""

    model_config = ConfigDict(frozen=True)

    total_orders: int = 0
    pending_orders: int = 0
    processing_orders: int = 0
    completed_orders: int = 0
    failed_orders: int = 0
    retrying_orders: int = 0
    average_processing_time_seconds: float = 0.0
    success_rate_percent: float = 0.0
    provider_distribution: dict[str, int] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
