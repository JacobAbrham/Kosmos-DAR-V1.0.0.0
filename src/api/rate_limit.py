"""
Rate Limiting Middleware for KOSMOS API.
Uses Redis for distributed rate limiting.
"""
import os
import time
import logging
from typing import Optional, Callable
from dataclasses import dataclass

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_size: int = 10  # Allow burst of requests


class RateLimiter:
    """Redis-based rate limiter using sliding window."""

    def __init__(self, redis_client=None, config: Optional[RateLimitConfig] = None):
        self._redis = redis_client
        self.config = config or RateLimitConfig(
            requests_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
            requests_per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", "1000")),
            burst_size=int(os.getenv("RATE_LIMIT_BURST", "10")),
        )

    async def _get_redis(self):
        """Lazy load Redis client."""
        if self._redis is None:
            try:
                from src.services.cache_service import get_cache_service
                cache = await get_cache_service()
                self._redis = cache._client
            except Exception as e:
                logger.warning(f"Redis unavailable for rate limiting: {e}")
        return self._redis

    async def is_rate_limited(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> tuple[bool, int, int]:
        """
        Check if request is rate limited using sliding window.
        Returns: (is_limited, remaining, reset_time)
        """
        redis = await self._get_redis()
        if redis is None:
            # No Redis, allow all requests
            return False, limit, 0

        now = time.time()
        window_start = now - window_seconds

        try:
            pipe = redis.pipeline()

            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)

            # Count current requests
            pipe.zcard(key)

            # Add current request
            pipe.zadd(key, {str(now): now})

            # Set expiry
            pipe.expire(key, window_seconds)

            results = await pipe.execute()
            current_count = results[1]

            remaining = max(0, limit - current_count - 1)
            reset_time = int(window_start + window_seconds)

            if current_count >= limit:
                return True, 0, reset_time

            return False, remaining, reset_time

        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return False, limit, 0

    async def check_rate_limit(self, identifier: str) -> tuple[bool, dict]:
        """
        Check rate limits for an identifier.
        Returns: (is_limited, headers_dict)
        """
        # Check per-minute limit
        minute_key = f"ratelimit:minute:{identifier}"
        minute_limited, minute_remaining, minute_reset = await self.is_rate_limited(
            minute_key,
            self.config.requests_per_minute,
            60,
        )

        if minute_limited:
            return True, {
                "X-RateLimit-Limit": str(self.config.requests_per_minute),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(minute_reset),
                "Retry-After": str(60 - int(time.time()) % 60),
            }

        # Check per-hour limit
        hour_key = f"ratelimit:hour:{identifier}"
        hour_limited, hour_remaining, hour_reset = await self.is_rate_limited(
            hour_key,
            self.config.requests_per_hour,
            3600,
        )

        if hour_limited:
            return True, {
                "X-RateLimit-Limit": str(self.config.requests_per_hour),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(hour_reset),
                "Retry-After": str(3600 - int(time.time()) % 3600),
            }

        return False, {
            "X-RateLimit-Limit": str(self.config.requests_per_minute),
            "X-RateLimit-Remaining": str(minute_remaining),
            "X-RateLimit-Reset": str(minute_reset),
        }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting."""

    def __init__(
        self,
        app,
        limiter: Optional[RateLimiter] = None,
        key_func: Optional[Callable[[Request], str]] = None,
        exclude_paths: Optional[list] = None,
    ):
        super().__init__(app)
        self.limiter = limiter or RateLimiter()
        self.key_func = key_func or self._default_key_func
        self.exclude_paths = exclude_paths or [
            "/health", "/metrics", "/docs", "/openapi.json"]

    def _default_key_func(self, request: Request) -> str:
        """Default key function using IP address."""
        # Try to get real IP from proxy headers
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Fall back to client host
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Get identifier for rate limiting
        identifier = self.key_func(request)

        # Check rate limit
        is_limited, headers = await self.limiter.check_rate_limit(identifier)

        if is_limited:
            response = Response(
                content='{"detail": "Rate limit exceeded"}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
            )
            for key, value in headers.items():
                response.headers[key] = value
            return response

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        for key, value in headers.items():
            response.headers[key] = value

        return response


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get or create the global rate limiter."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter
