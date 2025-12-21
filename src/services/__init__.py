"""
Business logic services for KOSMOS.
This package contains service layer implementations.
"""

from .llm_service import LLMService, get_llm_service, Message, LLMResponse
from .retry import (
    RetryConfig,
    CircuitBreaker,
    retry_async,
    with_retry,
    LLM_RETRY_CONFIG,
    CACHE_RETRY_CONFIG,
    DATABASE_RETRY_CONFIG,
)

__all__ = [
    "LLMService",
    "get_llm_service",
    "Message",
    "LLMResponse",
    # Retry utilities
    "RetryConfig",
    "CircuitBreaker",
    "retry_async",
    "with_retry",
    "LLM_RETRY_CONFIG",
    "CACHE_RETRY_CONFIG",
    "DATABASE_RETRY_CONFIG",
]
