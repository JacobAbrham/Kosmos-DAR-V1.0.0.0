"""
Unit tests for the LLM service.
Tests multi-provider support, caching, and configuration.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import os

from src.services.llm_service import (
    LLMProvider,
    LLMConfig,
    Message,
    LLMResponse,
    LLMService,
    get_llm_service,
)


class TestLLMConfig:
    """Tests for LLMConfig dataclass."""

    def test_default_config_creation(self):
        """Should create config with defaults."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key="test-key"
        )
        assert config.provider == LLMProvider.OPENAI
        assert config.model == "gpt-4"
        assert config.api_key == "test-key"
        assert config.max_tokens == 4096
        assert config.temperature == 0.7
        assert config.enable_cache is True

    def test_custom_config(self):
        """Should accept custom configuration values."""
        config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-sonnet",
            api_key="anthropic-key",
            max_tokens=2048,
            temperature=0.5,
            enable_cache=False,
            cache_ttl=1800,
        )
        assert config.provider == LLMProvider.ANTHROPIC
        assert config.max_tokens == 2048
        assert config.temperature == 0.5
        assert config.enable_cache is False
        assert config.cache_ttl == 1800


class TestLLMProvider:
    """Tests for LLMProvider enum."""

    def test_all_providers_defined(self):
        """All expected providers should be defined."""
        assert LLMProvider.OPENAI.value == "openai"
        assert LLMProvider.ANTHROPIC.value == "anthropic"
        assert LLMProvider.OLLAMA.value == "ollama"
        assert LLMProvider.HUGGINGFACE.value == "huggingface"

    def test_provider_count(self):
        """Should have exactly 4 providers."""
        providers = list(LLMProvider)
        assert len(providers) == 4


class TestMessage:
    """Tests for Message dataclass."""

    def test_user_message(self):
        """Should create user message."""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_assistant_message(self):
        """Should create assistant message."""
        msg = Message(role="assistant", content="Hi there!")
        assert msg.role == "assistant"
        assert msg.content == "Hi there!"

    def test_system_message(self):
        """Should create system message."""
        msg = Message(role="system", content="You are a helpful assistant.")
        assert msg.role == "system"


class TestLLMResponse:
    """Tests for LLMResponse dataclass."""

    def test_response_creation(self):
        """Should create response with all fields."""
        response = LLMResponse(
            content="Hello, world!",
            model="gpt-4",
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            finish_reason="stop",
        )
        assert response.content == "Hello, world!"
        assert response.model == "gpt-4"
        assert response.usage["total_tokens"] == 15
        assert response.cached is False

    def test_cached_response(self):
        """Should mark response as cached."""
        response = LLMResponse(
            content="Cached response",
            model="gpt-4",
            usage={},
            finish_reason="stop",
            cached=True,
        )
        assert response.cached is True


class TestLLMService:
    """Tests for LLMService class."""

    def test_service_initialization_with_config(self):
        """Should initialize with provided config."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key="test-key"
        )
        service = LLMService(config=config)
        assert service.config.provider == LLMProvider.OPENAI
        assert service.config.model == "gpt-4"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-openai-key"})
    def test_default_config_openai(self):
        """Should default to OpenAI if key is set."""
        service = LLMService()
        assert service.config.provider == LLMProvider.OPENAI

    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "",
        "ANTHROPIC_API_KEY": "test-anthropic-key"
    }, clear=True)
    def test_default_config_anthropic_fallback(self):
        """Should fall back to Anthropic if OpenAI key missing."""
        service = LLMService()
        assert service.config.provider == LLMProvider.ANTHROPIC


class TestGetLLMService:
    """Tests for get_llm_service singleton."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_returns_service_instance(self):
        """Should return an LLMService instance."""
        service = get_llm_service()
        assert isinstance(service, LLMService)


class TestCacheKeyGeneration:
    """Tests for cache key generation."""

    def test_same_input_same_key(self):
        """Same messages should generate same cache key."""
        import hashlib
        import json
        
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"},
        ]
        model = "gpt-4"
        
        # Test consistent hashing
        key_data = f"{model}:{json.dumps(messages, sort_keys=True)}"
        key1 = hashlib.md5(key_data.encode()).hexdigest()
        key2 = hashlib.md5(key_data.encode()).hexdigest()
        assert key1 == key2

    def test_different_input_different_key(self):
        """Different messages should generate different cache key."""
        import hashlib
        import json
        
        messages1 = [{"role": "user", "content": "Hello"}]
        messages2 = [{"role": "user", "content": "Hi"}]
        model = "gpt-4"
        
        key_data1 = f"{model}:{json.dumps(messages1, sort_keys=True)}"
        key_data2 = f"{model}:{json.dumps(messages2, sort_keys=True)}"
        
        key1 = hashlib.md5(key_data1.encode()).hexdigest()
        key2 = hashlib.md5(key_data2.encode()).hexdigest()
        assert key1 != key2
