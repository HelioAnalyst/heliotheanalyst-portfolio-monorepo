"""Tests for order service."""

import pytest
import pytest_asyncio
import uuid
from decimal import Decimal

from order_processing.config import Settings
from order_processing.domain.models import (
    Order,
    OrderItem,
    OrderStatus,
    ShippingAddress,
)
from order_processing.services.order_service import OrderService
from order_processing.storage.database import DatabaseRepository


@pytest_asyncio.fixture
async def db_repo():
    """Create database repository."""
    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
    )
    repo = DatabaseRepository(settings)
    await repo.connect()
    yield repo
    await repo.disconnect()


@pytest_asyncio.fixture
async def order_service(db_repo):
    """Create order service."""
    settings = Settings()
    service = OrderService(db_repo, settings)
    return service


@pytest_asyncio.fixture
async def sample_order():
    """Create sample order."""
    return Order(
        idempotency_key=str(uuid.uuid4()),
        customer_id="cust_1",
        customer_email="test@example.com",
        items=[
            OrderItem(
                product_id="prod_1",
                sku="SKU-0001",
                name="Test Product",
                quantity=2,
                unit_price=Decimal("29.99"),
                total_price=Decimal("59.98"),
            ),
        ],
        shipping_address=ShippingAddress(
            name="Test Customer",
            line1="123 Main St",
            city="New York",
            state="NY",
            postal_code="10001",
        ),
        subtotal=Decimal("59.98"),
        tax=Decimal("5.00"),
        shipping_cost=Decimal("10.00"),
        total=Decimal("74.98"),
    )


@pytest.mark.asyncio
async def test_create_order(order_service, sample_order):
    """Test creating an order."""
    created = await order_service.create_order(sample_order)

    assert created.id is not None
    assert created.idempotency_key == sample_order.idempotency_key
    assert created.status == OrderStatus.PENDING


@pytest.mark.asyncio
async def test_get_order(order_service, sample_order):
    """Test getting an order."""
    created = await order_service.create_order(sample_order)

    fetched = await order_service.get_order(created.id or "")
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.customer_email == sample_order.customer_email


@pytest.mark.asyncio
async def test_idempotency(order_service, sample_order):
    """Test idempotency key prevents duplicates."""
    first = await order_service.create_order(sample_order)
    second = await order_service.create_order(sample_order)

    assert first.id == second.id


@pytest.mark.asyncio
async def test_process_order(order_service, sample_order):
    """Test processing an order."""
    created = await order_service.create_order(sample_order)

    # Wait for background processing
    import asyncio
    await asyncio.sleep(1)

    result = await order_service.process_order(created.id or "")

    assert result.order_id == created.id
    assert result.success is True
    assert result.status == OrderStatus.COMPLETED
    assert result.provider is not None


@pytest.mark.asyncio
async def test_get_metrics(order_service, sample_order):
    """Test getting metrics."""
    await order_service.create_order(sample_order)

    metrics = await order_service.get_metrics()

    assert metrics.total_orders >= 1
    assert metrics.success_rate_percent >= 0


@pytest.mark.asyncio
async def test_provider_selection(order_service):
    """Test provider selection based on order total."""
    from order_processing.domain.models import Provider

    # High value order -> Provider A
    high_value = Order(
        idempotency_key=str(uuid.uuid4()),
        customer_id="cust_1",
        customer_email="test@example.com",
        items=[],
        shipping_address=ShippingAddress(
            name="Test",
            line1="123 Main",
            city="NYC",
            state="NY",
            postal_code="10001",
        ),
        subtotal=Decimal("600"),
        tax=Decimal("0"),
        shipping_cost=Decimal("0"),
        total=Decimal("600"),
    )
    provider = order_service._select_provider(high_value)
    assert provider == Provider.PROVIDER_A

    # Medium value -> Provider B
    medium_value = Order(
        idempotency_key=str(uuid.uuid4()),
        customer_id="cust_2",
        customer_email="test2@example.com",
        items=[],
        shipping_address=ShippingAddress(
            name="Test",
            line1="123 Main",
            city="NYC",
            state="NY",
            postal_code="10001",
        ),
        subtotal=Decimal("200"),
        tax=Decimal("0"),
        shipping_cost=Decimal("0"),
        total=Decimal("200"),
    )
    provider = order_service._select_provider(medium_value)
    assert provider == Provider.PROVIDER_B

    # Low value -> Internal
    low_value = Order(
        idempotency_key=str(uuid.uuid4()),
        customer_id="cust_3",
        customer_email="test3@example.com",
        items=[],
        shipping_address=ShippingAddress(
            name="Test",
            line1="123 Main",
            city="NYC",
            state="NY",
            postal_code="10001",
        ),
        subtotal=Decimal("50"),
        tax=Decimal("0"),
        shipping_cost=Decimal("0"),
        total=Decimal("50"),
    )
    provider = order_service._select_provider(low_value)
    assert provider == Provider.INTERNAL
