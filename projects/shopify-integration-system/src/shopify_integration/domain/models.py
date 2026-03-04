"""Domain models for Shopify Integration System."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class SyncStatus(str, Enum):
    """Synchronization status values."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class Money(BaseModel):
    """Money amount with currency."""

    model_config = ConfigDict(frozen=True)

    amount: Decimal
    currency_code: str = "USD"


class ProductVariant(BaseModel):
    """Product variant model."""

    model_config = ConfigDict(frozen=True)

    id: str
    product_id: str
    sku: str
    title: str
    price: Money
    compare_at_price: Optional[Money] = None
    inventory_quantity: int = 0
    weight: Optional[float] = None
    weight_unit: str = "kg"
    barcode: Optional[str] = None
    position: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Product(BaseModel):
    """Product model."""

    model_config = ConfigDict(frozen=True)

    id: str
    title: str
    description: Optional[str] = None
    vendor: str
    product_type: str
    tags: list[str] = Field(default_factory=list)
    status: str = "active"
    variants: list[ProductVariant] = Field(default_factory=list)
    options: list[dict[str, Any]] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class InventoryItem(BaseModel):
    """Inventory item model."""

    model_config = ConfigDict(frozen=True)

    id: str
    variant_id: str
    sku: str
    location_id: str
    available: int = 0
    incoming: int = 0
    reserved: int = 0
    committed: int = 0
    damaged: int = 0
    safety_stock: int = 0
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class OrderItem(BaseModel):
    """Order line item model."""

    model_config = ConfigDict(frozen=True)

    id: str
    variant_id: str
    product_id: str
    sku: str
    title: str
    quantity: int
    price: Money
    total_discount: Money = Field(default_factory=lambda: Money(amount=Decimal("0")))
    tax_lines: list[dict[str, Any]] = Field(default_factory=list)
    properties: dict[str, Any] = Field(default_factory=dict)


class Customer(BaseModel):
    """Customer model."""

    model_config = ConfigDict(frozen=True)

    id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    addresses: list[dict[str, Any]] = Field(default_factory=list)
    accepts_marketing: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Order(BaseModel):
    """Order model."""

    model_config = ConfigDict(frozen=True)

    id: str
    order_number: str
    name: str
    customer: Optional[Customer] = None
    line_items: list[OrderItem] = Field(default_factory=list)
    subtotal_price: Money
    total_tax: Money
    total_price: Money
    total_discounts: Money = Field(default_factory=lambda: Money(amount=Decimal("0")))
    shipping_address: Optional[dict[str, Any]] = None
    billing_address: Optional[dict[str, Any]] = None
    shipping_lines: list[dict[str, Any]] = Field(default_factory=list)
    payment_gateway_names: list[str] = Field(default_factory=list)
    financial_status: str = "pending"
    fulfillment_status: Optional[str] = None
    note: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None


class SyncResult(BaseModel):
    """Result of a synchronization operation."""

    model_config = ConfigDict(frozen=True)

    status: SyncStatus
    operation: str
    items_processed: int = 0
    items_succeeded: int = 0
    items_failed: int = 0
    errors: list[str] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    details: dict[str, Any] = Field(default_factory=dict)

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate operation duration in seconds."""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.items_processed == 0:
            return 100.0
        return (self.items_succeeded / self.items_processed) * 100


class ReconciliationResult(BaseModel):
    """Result of inventory reconciliation."""

    model_config = ConfigDict(frozen=True)

    status: SyncStatus
    discrepancies_found: int = 0
    discrepancies_resolved: int = 0
    shopify_total: int = 0
    bc365_total: int = 0
    mismatched_items: list[dict[str, Any]] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
