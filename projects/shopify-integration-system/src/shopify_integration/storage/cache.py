"""Redis cache repository for rate limiting and session storage."""

import json
from typing import Any, Optional

import redis.asyncio as redis

from shopify_integration.config import Settings


class CacheRepository:
    """Redis-based cache repository."""

    def __init__(self, settings: Settings) -> None:
        """Initialize cache repository.

        Args:
            settings: Application settings.
        """
        self.settings = settings
        self._redis: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Establish Redis connection."""
        self._redis = redis.from_url(
            self.settings.redis_url,
            decode_responses=True,
        )

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key.

        Returns:
            Cached value or None.
        """
        if not self._redis:
            raise RuntimeError("Cache not connected")

        value = await self._redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> None:
        """Set value in cache.

        Args:
            key: Cache key.
            value: Value to cache.
            ttl: Time to live in seconds.
        """
        if not self._redis:
            raise RuntimeError("Cache not connected")

        serialized = json.dumps(value, default=str)
        await self._redis.set(key, serialized, ex=ttl)

    async def delete(self, key: str) -> None:
        """Delete value from cache.

        Args:
            key: Cache key.
        """
        if not self._redis:
            raise RuntimeError("Cache not connected")

        await self._redis.delete(key)

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter in cache.

        Args:
            key: Counter key.
            amount: Amount to increment.

        Returns:
            New counter value.
        """
        if not self._redis:
            raise RuntimeError("Cache not connected")

        return await self._redis.incrby(key, amount)

    async def expire(self, key: str, seconds: int) -> None:
        """Set expiration on key.

        Args:
            key: Cache key.
            seconds: Expiration time in seconds.
        """
        if not self._redis:
            raise RuntimeError("Cache not connected")

        await self._redis.expire(key, seconds)

    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
    ) -> tuple[bool, int]:
        """Check if request is within rate limit.

        Args:
            key: Rate limit key.
            max_requests: Maximum requests allowed.
            window_seconds: Time window in seconds.

        Returns:
            Tuple of (allowed, remaining_requests).
        """
        if not self._redis:
            # Allow if cache not available
            return True, max_requests

        current = await self._redis.get(key)
        if current is None:
            await self._redis.set(key, 1, ex=window_seconds)
            return True, max_requests - 1

        count = int(current)
        if count >= max_requests:
            return False, 0

        await self._redis.incr(key)
        return True, max_requests - count - 1
