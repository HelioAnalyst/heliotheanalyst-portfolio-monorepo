"""Base adapter interface for external APIs."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from shopify_integration.config import Settings


class RateLimitError(Exception):
    """Raised when API rate limit is exceeded."""

    pass


class APIError(Exception):
    """Raised when API returns an error."""

    pass


class BaseAdapter(ABC):
    """Base class for external API adapters."""

    def __init__(self, settings: Settings) -> None:
        """Initialize adapter with settings.

        Args:
            settings: Application settings.
        """
        self.settings = settings
        self._client: Optional[Any] = None

    @property
    @abstractmethod
    def name(self) -> str:
        """Return adapter name."""
        pass

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the API."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the API."""
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Check API health status.

        Returns:
            Health status dictionary.
        """
        pass

    def _get_retry_decorator(self) -> Any:
        """Get retry decorator with configured settings.

        Returns:
            Tenacity retry decorator.
        """
        return retry(
            stop=stop_after_attempt(self.settings.sync_max_retries),
            wait=wait_exponential(
                multiplier=self.settings.sync_retry_delay,
                min=1,
                max=60,
            ),
            retry=retry_if_exception_type((RateLimitError, APIError)),
            reraise=True,
        )
