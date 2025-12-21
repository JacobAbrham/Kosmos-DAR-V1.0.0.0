"""
Redis Cache Service for KOSMOS.
Provides caching for LLM responses and expensive computations.
"""
import os
import json
import hashlib
import logging
from typing import Optional, Any
from datetime import timedelta

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based caching service."""

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv(
            "REDIS_URL", "redis://localhost:6379")
        self._client: Optional[redis.Redis] = None
        self.default_ttl = int(
            os.getenv("CACHE_TTL_SECONDS", 3600))  # 1 hour default

    async def connect(self) -> None:
        """Establish Redis connection with retry logic."""
        if self._client is None:
            max_retries = 3
            retry_delay = 1.0

            for attempt in range(max_retries):
                try:
                    self._client = redis.from_url(
                        self.redis_url,
                        encoding="utf-8",
                        decode_responses=True
                    )
                    await self._client.ping()
                    logger.info(f"Connected to Redis at {self.redis_url}")
                    return
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Redis connection attempt {attempt + 1}/{max_retries} failed: {e}. "
                            f"Retrying in {retry_delay}s..."
                        )
                        import asyncio
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        logger.error(
                            f"Failed to connect to Redis after {max_retries} attempts: {e}")
                        self._client = None
                        # Don't raise - allow graceful degradation

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Disconnected from Redis")

    @staticmethod
    def _generate_key(prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from prefix and arguments."""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()[:16]
        return f"{prefix}:{key_hash}"

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if not self._client:
            return None

        try:
            value = await self._client.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache with optional TTL."""
        if not self._client:
            return False

        try:
            ttl = ttl or self.default_ttl
            await self._client.setex(
                key,
                timedelta(seconds=ttl),
                json.dumps(value)
            )
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        if not self._client:
            return False

        try:
            await self._client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
            return False

    async def clear_prefix(self, prefix: str) -> int:
        """Clear all keys with a given prefix."""
        if not self._client:
            return 0

        try:
            cursor = 0
            deleted = 0
            while True:
                cursor, keys = await self._client.scan(cursor, match=f"{prefix}:*", count=100)
                if keys:
                    await self._client.delete(*keys)
                    deleted += len(keys)
                if cursor == 0:
                    break
            logger.info(f"Cleared {deleted} keys with prefix '{prefix}'")
            return deleted
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")
            return 0


# Global cache service instance
_cache_service: Optional[CacheService] = None


async def get_cache_service() -> CacheService:
    """Get or create the global cache service."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
        await _cache_service.connect()
    return _cache_service


async def close_cache_service() -> None:
    """Close the global cache service."""
    global _cache_service
    if _cache_service:
        await _cache_service.disconnect()
        _cache_service = None
