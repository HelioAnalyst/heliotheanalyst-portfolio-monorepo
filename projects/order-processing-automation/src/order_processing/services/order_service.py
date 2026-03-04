"""Order processing service."""

import asyncio
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from order_processing.config import Settings
from order_processing.domain.models import (
    DashboardMetrics,
    Order,
    OrderItem,
    OrderStatus,
    ProcessingResult,
    Provider,
    ShippingAddress,
)
from order_processing.storage.database import DatabaseRepository


class OrderService:
    """Service for order processing."""

    def __init__(self, db_repo: DatabaseRepository, settings: Settings) -> None:
        """Initialize order service.

        Args:
            db_repo: Database repository.
            settings: Application settings.
        """
        self.db_repo = db_repo
        self.settings = settings
        self._provider_handlers = {
            Provider.PROVIDER_A: self._process_with_provider_a,
            Provider.PROVIDER_B: self._process_with_provider_b,
            Provider.PROVIDER_C: self._process_with_provider_c,
            Provider.INTERNAL: self._process_internally,
        }

    def _select_provider(self, order: Order) -> Provider:
        """Select provider based on routing rules.

        Args:
            order: Order to route.

        Returns:
            Selected provider.
        """
        # Simple routing based on order total
        if order.total > Decimal("500"):
            return Provider.PROVIDER_A
        elif order.total > Decimal("100"):
            return Provider.PROVIDER_B
        else:
            return Provider.INTERNAL

    async def create_order(self, order: Order) -> Order:
        """Create new order.

        Args:
            order: Order to create.

        Returns:
            Created order with ID.
        """
        # Check idempotency
        existing = await self.db_repo.get_order_by_idempotency_key(order.idempotency_key)
        if existing:
            return existing

        # Generate order ID
        order_id = str(uuid.uuid4())
        order = Order(
            **order.model_dump(exclude={"id"}),
            id=order_id,
            status=OrderStatus.PENDING,
        )

        # Save to database
        await self.db_repo.save_order(order)

        # Queue for processing
        await self._queue_for_processing(order_id)

        return order

    async def _queue_for_processing(self, order_id: str) -> None:
        """Queue order for background processing.

        Args:
            order_id: Order ID to queue.
        """
        # In real implementation, this would use Celery
        # For demo, we'll process immediately
        asyncio.create_task(self._background_process(order_id))

    async def _background_process(self, order_id: str) -> None:
        """Background processing task.

        Args:
            order_id: Order ID to process.
        """
        await asyncio.sleep(0.5)  # Simulate queue delay
        await self.process_order(order_id)

    async def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID.

        Args:
            order_id: Order ID.

        Returns:
            Order or None.
        """
        return await self.db_repo.get_order(order_id)

    async def process_order(self, order_id: str) -> ProcessingResult:
        """Process an order.

        Args:
            order_id: Order ID to process.

        Returns:
            Processing result.
        """
        order = await self.db_repo.get_order(order_id)
        if not order:
            return ProcessingResult(
                order_id=order_id,
                success=False,
                status=OrderStatus.FAILED,
                message="Order not found",
            )

        # Update status
        order = await self.db_repo.update_order_status(
            order_id,
            OrderStatus.PROCESSING,
        )

        # Select provider
        provider = self._select_provider(order)
        order = await self.db_repo.update_order_provider(order_id, provider)

        # Process with provider
        handler = self._provider_handlers.get(provider, self._process_internally)

        try:
            result = await handler(order)
            if result.success:
                await self.db_repo.update_order_status(order_id, OrderStatus.COMPLETED)
            else:
                await self._handle_failure(order_id, result.message)
            return result
        except Exception as e:
            await self._handle_failure(order_id, str(e))
            return ProcessingResult(
                order_id=order_id,
                success=False,
                status=OrderStatus.FAILED,
                message=str(e),
            )

    async def _handle_failure(self, order_id: str, reason: str) -> None:
        """Handle order processing failure.

        Args:
            order_id: Order ID.
            reason: Failure reason.
        """
        order = await self.db_repo.get_order(order_id)
        if not order:
            return

        if order.retry_count < order.max_retries:
            await self.db_repo.update_order_status(
                order_id,
                OrderStatus.RETRYING,
                retry_count=order.retry_count + 1,
            )
            # Schedule retry
            await asyncio.sleep(self.settings.retry_delay_seconds)
            await self._queue_for_processing(order_id)
        else:
            await self.db_repo.update_order_status(
                order_id,
                OrderStatus.FAILED,
                failure_reason=reason,
            )

    async def _process_with_provider_a(self, order: Order) -> ProcessingResult:
        """Process with Provider A.

        Args:
            order: Order to process.

        Returns:
            Processing result.
        """
        await asyncio.sleep(0.1)  # Simulate API call
        provider_order_id = f"PA-{uuid.uuid4().hex[:8].upper()}"
        return ProcessingResult(
            order_id=order.id or "",
            success=True,
            status=OrderStatus.COMPLETED,
            provider=Provider.PROVIDER_A,
            provider_order_id=provider_order_id,
            message="Order processed successfully with Provider A",
        )

    async def _process_with_provider_b(self, order: Order) -> ProcessingResult:
        """Process with Provider B.

        Args:
            order: Order to process.

        Returns:
            Processing result.
        """
        await asyncio.sleep(0.1)
        provider_order_id = f"PB-{uuid.uuid4().hex[:8].upper()}"
        return ProcessingResult(
            order_id=order.id or "",
            success=True,
            status=OrderStatus.COMPLETED,
            provider=Provider.PROVIDER_B,
            provider_order_id=provider_order_id,
            message="Order processed successfully with Provider B",
        )

    async def _process_with_provider_c(self, order: Order) -> ProcessingResult:
        """Process with Provider C.

        Args:
            order: Order to process.

        Returns:
            Processing result.
        """
        await asyncio.sleep(0.1)
        provider_order_id = f"PC-{uuid.uuid4().hex[:8].upper()}"
        return ProcessingResult(
            order_id=order.id or "",
            success=True,
            status=OrderStatus.COMPLETED,
            provider=Provider.PROVIDER_C,
            provider_order_id=provider_order_id,
            message="Order processed successfully with Provider C",
        )

    async def _process_internally(self, order: Order) -> ProcessingResult:
        """Process order internally.

        Args:
            order: Order to process.

        Returns:
            Processing result.
        """
        await asyncio.sleep(0.05)
        return ProcessingResult(
            order_id=order.id or "",
            success=True,
            status=OrderStatus.COMPLETED,
            provider=Provider.INTERNAL,
            message="Order processed internally",
        )

    async def retry_order(self, order_id: str) -> ProcessingResult:
        """Retry failed order.

        Args:
            order_id: Order ID to retry.

        Returns:
            Processing result.
        """
        order = await self.db_repo.get_order(order_id)
        if not order:
            return ProcessingResult(
                order_id=order_id,
                success=False,
                status=OrderStatus.FAILED,
                message="Order not found",
            )

        if order.status not in [OrderStatus.FAILED, OrderStatus.RETRYING]:
            return ProcessingResult(
                order_id=order_id,
                success=False,
                status=order.status,
                message=f"Cannot retry order in status: {order.status}",
            )

        # Reset status and retry
        await self.db_repo.update_order_status(
            order_id,
            OrderStatus.PENDING,
            retry_count=0,
            failure_reason=None,
        )

        return await self.process_order(order_id)

    async def get_metrics(self) -> DashboardMetrics:
        """Get dashboard metrics.

        Returns:
            Processing metrics.
        """
        return await self.db_repo.get_metrics()

    async def handle_provider_webhook(self, payload: dict) -> None:
        """Handle provider webhook.

        Args:
            payload: Webhook payload.
        """
        # Extract order ID from payload
        order_id = payload.get("order_id")
        status = payload.get("status")

        if not order_id:
            return

        order = await self.db_repo.get_order(order_id)
        if not order:
            return

        # Update order status based on webhook
        if status == "shipped":
            await self.db_repo.update_order_status(order_id, OrderStatus.COMPLETED)
        elif status == "failed":
            await self._handle_failure(order_id, payload.get("reason", "Provider failed"))
