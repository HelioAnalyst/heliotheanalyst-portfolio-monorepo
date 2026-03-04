"""Configuration management for Shopify Integration System."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="ShopifyIntegration", alias="APP_NAME")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    mock_mode: bool = Field(default=True, alias="MOCK_MODE")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://shopify_user:shopify_pass@localhost:5432/shopify_integration",
        alias="DATABASE_URL",
    )
    database_url_sync: str = Field(
        default="postgresql://shopify_user:shopify_pass@localhost:5432/shopify_integration",
        alias="DATABASE_URL_SYNC",
    )

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # Shopify API
    shopify_shop_domain: Optional[str] = Field(default=None, alias="SHOPIFY_SHOP_DOMAIN")
    shopify_api_key: Optional[str] = Field(default=None, alias="SHOPIFY_API_KEY")
    shopify_api_password: Optional[str] = Field(default=None, alias="SHOPIFY_API_PASSWORD")
    shopify_api_version: str = Field(default="2024-01", alias="SHOPIFY_API_VERSION")
    shopify_rate_limit_requests: int = Field(default=40, alias="SHOPIFY_RATE_LIMIT_REQUESTS")
    shopify_rate_limit_window: float = Field(default=1.0, alias="SHOPIFY_RATE_LIMIT_WINDOW")

    # Business Central 365
    bc365_tenant_id: Optional[str] = Field(default=None, alias="BC365_TENANT_ID")
    bc365_client_id: Optional[str] = Field(default=None, alias="BC365_CLIENT_ID")
    bc365_client_secret: Optional[str] = Field(default=None, alias="BC365_CLIENT_SECRET")
    bc365_environment: str = Field(default="production", alias="BC365_ENVIRONMENT")
    bc365_company_id: Optional[str] = Field(default=None, alias="BC365_COMPANY_ID")

    # Sync Settings
    sync_batch_size: int = Field(default=100, alias="SYNC_BATCH_SIZE")
    sync_max_retries: int = Field(default=3, alias="SYNC_MAX_RETRIES")
    sync_retry_delay: float = Field(default=1.0, alias="SYNC_RETRY_DELAY")
    sync_timeout: int = Field(default=30, alias="SYNC_TIMEOUT")

    # Monitoring
    metrics_enabled: bool = Field(default=True, alias="METRICS_ENABLED")
    health_check_interval: int = Field(default=30, alias="HEALTH_CHECK_INTERVAL")

    @property
    def shopify_credentials_configured(self) -> bool:
        """Check if Shopify credentials are configured."""
        return all([
            self.shopify_shop_domain,
            self.shopify_api_key,
            self.shopify_api_password,
        ])

    @property
    def bc365_credentials_configured(self) -> bool:
        """Check if BC365 credentials are configured."""
        return all([
            self.bc365_tenant_id,
            self.bc365_client_id,
            self.bc365_client_secret,
        ])


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
