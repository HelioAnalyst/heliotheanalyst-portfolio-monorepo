"""Configuration for order processing."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="OrderProcessing", alias="APP_NAME")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    database_url: str = Field(
        default="postgresql+asyncpg://orders_user:orders_pass@localhost:5433/order_processing",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6380/0", alias="REDIS_URL")
    celery_broker_url: str = Field(
        default="redis://localhost:6380/1",
        alias="CELERY_BROKER_URL",
    )

    # Processing settings
    max_retries: int = Field(default=3, alias="MAX_RETRIES")
    retry_delay_seconds: int = Field(default=60, alias="RETRY_DELAY_SECONDS")
    processing_timeout_seconds: int = Field(default=300, alias="PROCESSING_TIMEOUT_SECONDS")

    # Provider settings
    provider_a_url: str = Field(default="https://api.provider-a.mock", alias="PROVIDER_A_URL")
    provider_b_url: str = Field(default="https://api.provider-b.mock", alias="PROVIDER_B_URL")
    provider_c_url: str = Field(default="https://api.provider-c.mock", alias="PROVIDER_C_URL")

    # Webhook settings
    webhook_secret: str = Field(default="demo-secret", alias="WEBHOOK_SECRET")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings()
