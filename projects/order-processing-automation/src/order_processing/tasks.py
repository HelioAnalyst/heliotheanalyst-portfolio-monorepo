"""Celery tasks for order processing pipeline."""

import logging
from typing import Optional

from order_processing.celery_app import celery_app
from order_processing.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@celery_app.task(bind=True, max_retries=settings.max_retries)
def process_order(
    self,
    order_id: str,
    provider: Optional[str] = None,
) -> dict:
    """Process an order asynchronously.
    
    This is the main task used by the demo pipeline to process orders.
    It simulates provider routing and order fulfillment.
    
    Args:
        order_id: Unique order identifier
        provider: Optional provider to route to (auto-selected if not provided)
        
    Returns:
        Processing result with status and details
    """
    try:
        logger.info(f"Processing order {order_id}")
        
        # Simulate provider selection if not specified
        if provider is None:
            provider = _select_provider(order_id)
        
        # Simulate order processing
        result = {
            "order_id": order_id,
            "status": "processing",
            "provider": provider,
            "message": f"Order routed to {provider}",
        }
        
        logger.info(f"Order {order_id} processed successfully via {provider}")
        return result
        
    except Exception as exc:
        logger.error(f"Failed to process order {order_id}: {exc}")
        # Retry with exponential backoff
        retry_count = self.request.retries
        retry_delay = settings.retry_delay_seconds * (2 ** retry_count)
        raise self.retry(exc=exc, countdown=retry_delay)


@celery_app.task(bind=True, max_retries=settings.max_retries)
def update_order_status(
    self,
    order_id: str,
    status: str,
    metadata: Optional[dict] = None,
) -> dict:
    """Update order status asynchronously.
    
    Args:
        order_id: Unique order identifier
        status: New status (pending, processing, completed, failed)
        metadata: Optional additional data
        
    Returns:
        Update result
    """
    try:
        logger.info(f"Updating order {order_id} status to {status}")
        
        result = {
            "order_id": order_id,
            "status": status,
            "updated": True,
            "metadata": metadata or {},
        }
        
        return result
        
    except Exception as exc:
        logger.error(f"Failed to update order {order_id} status: {exc}")
        retry_count = self.request.retries
        retry_delay = settings.retry_delay_seconds * (2 ** retry_count)
        raise self.retry(exc=exc, countdown=retry_delay)


@celery_app.task
def generate_daily_report(date_str: Optional[str] = None) -> dict:
    """Generate daily order processing report.
    
    Args:
        date_str: Date string in YYYY-MM-DD format (defaults to today)
        
    Returns:
        Report summary
    """
    from datetime import datetime
    
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    logger.info(f"Generating daily report for {date_str}")
    
    # Simulate report generation
    report = {
        "date": date_str,
        "total_orders": 150,
        "completed": 142,
        "failed": 3,
        "pending": 5,
        "generated_at": datetime.now().isoformat(),
    }
    
    return report


def _select_provider(order_id: str) -> str:
    """Select a provider based on order_id hash for demo purposes.
    
    Args:
        order_id: Order identifier
        
    Returns:
        Selected provider name
    """
    providers = ["provider_a", "provider_b", "provider_c"]
    # Simple hash-based selection for demo
    provider_index = hash(order_id) % len(providers)
    return providers[provider_index]
