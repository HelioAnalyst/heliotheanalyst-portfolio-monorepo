"""Celery application configuration for order processing."""

from celery import Celery

from order_processing.config import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "order_processing",
    broker=settings.celery_broker_url,
    backend=settings.celery_broker_url,
    include=["order_processing.tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# Task routing (optional - for future scaling)
celery_app.conf.task_routes = {
    "order_processing.tasks.process_order": {"queue": "orders"},
    "order_processing.tasks.update_order_status": {"queue": "orders"},
}
