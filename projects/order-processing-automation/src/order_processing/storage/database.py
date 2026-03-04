"""Database repository for order processing."""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
    select,
)
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from order_processing.config import Settings
from order_processing.domain.models import (
    DashboardMetrics,
    Order,
    OrderItem,
    OrderStatus,
    Provider,
    ShippingAddress,
)

Base = declarative_base()


class OrderModel(Base):
    """Order database model."""

    __tablename__ = "orders"

    id = Column(String(36), primary_key=True)
    idempotency_key = Column(String(100), unique=True, nullable=False, index=True)
    customer_id = Column(String(36), nullable=False)
    customer_email = Column(String(255), nullable=False)

    items = Column(JSON, nullable=False)
    shipping_address = Column(JSON, nullable=False)

    subtotal = Column(Numeric(10, 2), nullable=False)
    tax = Column(Numeric(10, 2), nullable=False)
    shipping_cost = Column(Numeric(10, 2), nullable=False)
    total = Column(Numeric(10, 2), nullable=False)

    currency = Column(String(3), default="USD")
    status = Column(String(50), nullable=False, index=True)

    provider = Column(String(50))
    provider_order_id = Column(String(100))

    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    failure_reason = Column(String(500))

    # NOTE:
    # "metadata" is a reserved attribute name in SQLAlchemy Declarative models.
    # We keep the DB column name as "metadata" but use a safe Python attribute name.
    order_metadata = Column("metadata", JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime)


class DatabaseRepository:
    """PostgreSQL database repository."""

    def __init__(self, settings: Settings) -> None:
        """Initialize repository.

        Args:
            settings: Application settings.
        """
        self.settings = settings
        self._engine = None
        self._session_maker = None

    async def connect(self) -> None:
        """Establish database connection."""
        self._engine = create_async_engine(
            self.settings.database_url,
            echo=self.settings.debug,
        )
        self._session_maker = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
        )

        # Create tables
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def disconnect(self) -> None:
        """Close database connection."""
        if self._engine:
            await self._engine.dispose()

    def _order_to_model(self, order: Order) -> OrderModel:
        """Convert Order to database model.

        Args:
            order: Order domain model.

        Returns:
            Database model.
        """
        return OrderModel(
            id=order.id,
            idempotency_key=order.idempotency_key,
            customer_id=order.customer_id,
            customer_email=order.customer_email,
            items=[item.model_dump() for item in order.items],
            shipping_address=order.shipping_address.model_dump(),
            subtotal=order.subtotal,
            tax=order.tax,
            shipping_cost=order.shipping_cost,
            total=order.total,
            currency=order.currency,
            status=order.status.value,
            provider=order.provider.value if order.provider else None,
            provider_order_id=order.provider_order_id,
            retry_count=order.retry_count,
            max_retries=order.max_retries,
            failure_reason=order.failure_reason,
            order_metadata=order.metadata,  # domain field stays "metadata"
            created_at=order.created_at,
            updated_at=order.updated_at,
            processed_at=order.processed_at,
        )

    def _model_to_order(self, model: OrderModel) -> Order:
        """Convert database model to Order.

        Args:
            model: Database model.

        Returns:
            Order domain model.
        """
        return Order(
            id=model.id,
            idempotency_key=model.idempotency_key,
            customer_id=model.customer_id,
            customer_email=model.customer_email,
            items=[OrderItem(**item) for item in model.items],
            shipping_address=ShippingAddress(**model.shipping_address),
            subtotal=model.subtotal,
            tax=model.tax,
            shipping_cost=model.shipping_cost,
            total=model.total,
            currency=model.currency,
            status=OrderStatus(model.status),
            provider=Provider(model.provider) if model.provider else None,
            provider_order_id=model.provider_order_id,
            retry_count=model.retry_count,
            max_retries=model.max_retries,
            failure_reason=model.failure_reason,
            metadata=model.order_metadata,  # map back to domain "metadata"
            created_at=model.created_at,
            updated_at=model.updated_at,
            processed_at=model.processed_at,
        )

    async def save_order(self, order: Order) -> None:
        """Save order to database.

        Args:
            order: Order to save.
        """
        if not self._session_maker:
            raise RuntimeError("Database not connected")

        async with self._session_maker() as session:
            model = self._order_to_model(order)
            session.add(model)
            await session.commit()

    async def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID.

        Args:
            order_id: Order ID.

        Returns:
            Order or None.
        """
        if not self._session_maker:
            raise RuntimeError("Database not connected")

        async with self._session_maker() as session:
            result = await session.execute(
                select(OrderModel).where(OrderModel.id == order_id)
            )
            model = result.scalar_one_or_none()
            return self._model_to_order(model) if model else None

    async def get_order_by_idempotency_key(self, key: str) -> Optional[Order]:
        """Get order by idempotency key.

        Args:
            key: Idempotency key.

        Returns:
            Order or None.
        """
        if not self._session_maker:
            raise RuntimeError("Database not connected")

        async with self._session_maker() as session:
            result = await session.execute(
                select(OrderModel).where(OrderModel.idempotency_key == key)
            )
            model = result.scalar_one_or_none()
            return self._model_to_order(model) if model else None

    async def update_order_status(
        self,
        order_id: str,
        status: OrderStatus,
        **kwargs: Any,
    ) -> Order:
        """Update order status.

        Args:
            order_id: Order ID.
            status: New status.
            **kwargs: Additional fields to update.

        Returns:
            Updated order.
        """
        if not self._session_maker:
            raise RuntimeError("Database not connected")

        async with self._session_maker() as session:
            result = await session.execute(
                select(OrderModel).where(OrderModel.id == order_id)
            )
            model = result.scalar_one()

            model.status = status.value
            model.updated_at = datetime.utcnow()

            if status == OrderStatus.COMPLETED:
                model.processed_at = datetime.utcnow()

            # Guard: allow callers to pass metadata=... and map it safely.
            if "metadata" in kwargs:
                kwargs["order_metadata"] = kwargs.pop("metadata")

            for key, value in kwargs.items():
                setattr(model, key, value)

            await session.commit()
            return self._model_to_order(model)

    async def update_order_provider(
        self,
        order_id: str,
        provider: Provider,
    ) -> Order:
        """Update order provider.

        Args:
            order_id: Order ID.
            provider: Selected provider.

        Returns:
            Updated order.
        """
        if not self._session_maker:
            raise RuntimeError("Database not connected")

        async with self._session_maker() as session:
            result = await session.execute(
                select(OrderModel).where(OrderModel.id == order_id)
            )
            model = result.scalar_one()
            model.provider = provider.value
            model.updated_at = datetime.utcnow()
            await session.commit()
            return self._model_to_order(model)

    async def get_metrics(self) -> DashboardMetrics:
        """Get dashboard metrics.

        Returns:
            Processing metrics.
        """
        if not self._session_maker:
            return DashboardMetrics()

        async with self._session_maker() as session:
            from sqlalchemy import func

            # Count by status
            result = await session.execute(
                select(OrderModel.status, func.count(OrderModel.id)).group_by(
                    OrderModel.status
                )
            )
            status_counts = {status: count for status, count in result.all()}

            total = sum(status_counts.values())
            completed = status_counts.get(OrderStatus.COMPLETED.value, 0)

            # Provider distribution
            result = await session.execute(
                select(OrderModel.provider, func.count(OrderModel.id))
                .where(OrderModel.provider.isnot(None))
                .group_by(OrderModel.provider)
            )
            provider_dist = {
                provider or "unknown": count for provider, count in result.all()
            }

            return DashboardMetrics(
                total_orders=total,
                pending_orders=status_counts.get(OrderStatus.PENDING.value, 0),
                processing_orders=status_counts.get(OrderStatus.PROCESSING.value, 0),
                completed_orders=completed,
                failed_orders=status_counts.get(OrderStatus.FAILED.value, 0),
                retrying_orders=status_counts.get(OrderStatus.RETRYING.value, 0),
                success_rate_percent=(completed / total * 100) if total > 0 else 0,
                provider_distribution=provider_dist,
            )