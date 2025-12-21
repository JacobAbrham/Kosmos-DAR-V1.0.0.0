"""
Retry utilities for KOSMOS services.
Provides exponential backoff and circuit breaker patterns.
"""

import asyncio
import logging
import functools
from typing import TypeVar, Callable, Any, Optional, Type, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
        non_retryable_exceptions: Tuple[Type[Exception], ...] = (),
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retryable_exceptions = retryable_exceptions
        self.non_retryable_exceptions = non_retryable_exceptions


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.
    Prevents cascading failures by stopping requests after consecutive failures.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_requests: int = 3,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_requests = half_open_requests

        self._failure_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._state = "closed"  # closed, open, half-open
        self._half_open_successes = 0

    @property
    def is_open(self) -> bool:
        """Check if circuit is open (blocking requests)."""
        if self._state == "closed":
            return False

        if self._state == "open":
            # Check if we should transition to half-open
            if self._last_failure_time:
                elapsed = (datetime.now() -
                           self._last_failure_time).total_seconds()
                if elapsed >= self.recovery_timeout:
                    self._state = "half-open"
                    self._half_open_successes = 0
                    logger.info("Circuit breaker transitioning to half-open")
                    return False
            return True

        return False  # half-open allows requests

    def record_success(self) -> None:
        """Record a successful request."""
        if self._state == "half-open":
            self._half_open_successes += 1
            if self._half_open_successes >= self.half_open_requests:
                self._state = "closed"
                self._failure_count = 0
                logger.info("Circuit breaker closed - service recovered")
        else:
            self._failure_count = 0

    def record_failure(self) -> None:
        """Record a failed request."""
        self._failure_count += 1
        self._last_failure_time = datetime.now()

        if self._state == "half-open":
            self._state = "open"
            logger.warning("Circuit breaker opened from half-open state")
        elif self._failure_count >= self.failure_threshold:
            self._state = "open"
            logger.warning(
                f"Circuit breaker opened after {self._failure_count} failures"
            )


async def retry_async(
    func: Callable[..., T],
    config: Optional[RetryConfig] = None,
    circuit_breaker: Optional[CircuitBreaker] = None,
    *args,
    **kwargs,
) -> T:
    """
    Execute an async function with retry logic.

    Args:
        func: Async function to execute
        config: Retry configuration
        circuit_breaker: Optional circuit breaker
        *args, **kwargs: Arguments to pass to func

    Returns:
        Result of the function

    Raises:
        Last exception if all retries fail
    """
    config = config or RetryConfig()
    last_exception: Optional[Exception] = None

    for attempt in range(config.max_retries + 1):
        # Check circuit breaker
        if circuit_breaker and circuit_breaker.is_open:
            raise RuntimeError("Circuit breaker is open - service unavailable")

        try:
            result = await func(*args, **kwargs)
            if circuit_breaker:
                circuit_breaker.record_success()
            return result

        except config.non_retryable_exceptions as e:
            logger.error(f"Non-retryable error: {e}")
            if circuit_breaker:
                circuit_breaker.record_failure()
            raise

        except config.retryable_exceptions as e:
            last_exception = e

            if attempt < config.max_retries:
                delay = min(
                    config.initial_delay *
                    (config.exponential_base ** attempt),
                    config.max_delay
                )
                logger.warning(
                    f"Attempt {attempt + 1}/{config.max_retries + 1} failed: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    f"All {config.max_retries + 1} attempts failed: {e}")
                if circuit_breaker:
                    circuit_breaker.record_failure()

    raise last_exception


def with_retry(
    config: Optional[RetryConfig] = None,
    circuit_breaker: Optional[CircuitBreaker] = None,
):
    """
    Decorator for adding retry logic to async functions.

    Example:
        @with_retry(RetryConfig(max_retries=3))
        async def fetch_data():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await retry_async(func, config, circuit_breaker, *args, **kwargs)
        return wrapper
    return decorator


# Default configurations for common use cases
LLM_RETRY_CONFIG = RetryConfig(
    max_retries=3,
    initial_delay=1.0,
    max_delay=30.0,
    retryable_exceptions=(
        ConnectionError,
        TimeoutError,
        IOError,
    ),
)

CACHE_RETRY_CONFIG = RetryConfig(
    max_retries=2,
    initial_delay=0.5,
    max_delay=5.0,
    retryable_exceptions=(
        ConnectionError,
        TimeoutError,
    ),
)

DATABASE_RETRY_CONFIG = RetryConfig(
    max_retries=3,
    initial_delay=0.5,
    max_delay=10.0,
    retryable_exceptions=(
        ConnectionError,
        TimeoutError,
        IOError,
    ),
)
