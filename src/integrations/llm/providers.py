"""
LLM Provider Integration Layer
Unified interface for multiple LLM providers with fallback support.
"""
import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, AsyncIterator

from pydantic import BaseModel, Field

from src.core.logging import get_logger
from src.core.tracing import traced, add_span_attributes

logger = get_logger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"


class LLMMessage(BaseModel):
    """Unified message format for LLM interactions."""
    role: str  # "system", "user", "assistant"
    content: str
    name: str | None = None
    tool_calls: list[dict] | None = None
    tool_call_id: str | None = None


class LLMResponse(BaseModel):
    """Unified response format from LLM providers."""
    content: str
    model: str
    provider: LLMProvider
    usage: dict[str, int] = Field(default_factory=dict)
    finish_reason: str | None = None
    tool_calls: list[dict] | None = None
    raw_response: dict[str, Any] | None = None


class LLMConfig(BaseModel):
    """Configuration for LLM provider."""
    provider: LLMProvider
    model: str
    api_key: str | None = None
    base_url: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 60
    retry_attempts: int = 3
    retry_delay: float = 1.0


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = None

    @abstractmethod
    async def complete(
        self,
        messages: list[LLMMessage],
        **kwargs,
    ) -> LLMResponse:
        """Generate a completion from messages."""
        pass

    @abstractmethod
    async def stream(
        self,
        messages: list[LLMMessage],
        **kwargs,
    ) -> AsyncIterator[str]:
        """Stream a completion from messages."""
        pass

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Generate embeddings for text."""
        pass

    async def close(self):
        """Clean up resources."""
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI API client implementation."""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
        )
        logger.info(f"OpenAI client initialized with model {config.model}")

    @traced(name="openai_complete")
    async def complete(
        self,
        messages: list[LLMMessage],
        **kwargs,
    ) -> LLMResponse:
        """Generate completion using OpenAI API."""
        openai_messages = [
            {"role": m.role, "content": m.content}
            for m in messages
        ]

        response = await self._client.chat.completions.create(
            model=self.config.model,
            messages=openai_messages,
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            **{k: v for k, v in kwargs.items() if k not in ("temperature", "max_tokens")},
        )

        add_span_attributes({
            "llm.provider": "openai",
            "llm.model": self.config.model,
            "llm.tokens.prompt": response.usage.prompt_tokens,
            "llm.tokens.completion": response.usage.completion_tokens,
        })

        return LLMResponse(
            content=response.choices[0].message.content or "",
            model=response.model,
            provider=LLMProvider.OPENAI,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            finish_reason=response.choices[0].finish_reason,
            tool_calls=[tc.model_dump() for tc in (
                response.choices[0].message.tool_calls or [])],
        )

    async def stream(
        self,
        messages: list[LLMMessage],
        **kwargs,
    ) -> AsyncIterator[str]:
        """Stream completion using OpenAI API."""
        openai_messages = [
            {"role": m.role, "content": m.content}
            for m in messages
        ]

        stream = await self._client.chat.completions.create(
            model=self.config.model,
            messages=openai_messages,
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def embed(self, text: str) -> list[float]:
        """Generate embeddings using OpenAI API."""
        response = await self._client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding


class AnthropicClient(BaseLLMClient):
    """Anthropic API client implementation."""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        from anthropic import AsyncAnthropic

        self._client = AsyncAnthropic(
            api_key=config.api_key,
            timeout=config.timeout,
        )
        logger.info(f"Anthropic client initialized with model {config.model}")

    @traced(name="anthropic_complete")
    async def complete(
        self,
        messages: list[LLMMessage],
        **kwargs,
    ) -> LLMResponse:
        """Generate completion using Anthropic API."""
        # Extract system message if present
        system = None
        anthropic_messages = []

        for m in messages:
            if m.role == "system":
                system = m.content
            else:
                anthropic_messages.append({
                    "role": m.role,
                    "content": m.content,
                })

        response = await self._client.messages.create(
            model=self.config.model,
            messages=anthropic_messages,
            system=system,
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
        )

        add_span_attributes({
            "llm.provider": "anthropic",
            "llm.model": self.config.model,
            "llm.tokens.input": response.usage.input_tokens,
            "llm.tokens.output": response.usage.output_tokens,
        })

        return LLMResponse(
            content=response.content[0].text if response.content else "",
            model=response.model,
            provider=LLMProvider.ANTHROPIC,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            },
            finish_reason=response.stop_reason,
        )

    async def stream(
        self,
        messages: list[LLMMessage],
        **kwargs,
    ) -> AsyncIterator[str]:
        """Stream completion using Anthropic API."""
        system = None
        anthropic_messages = []

        for m in messages:
            if m.role == "system":
                system = m.content
            else:
                anthropic_messages.append({
                    "role": m.role,
                    "content": m.content,
                })

        async with self._client.messages.stream(
            model=self.config.model,
            messages=anthropic_messages,
            system=system,
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def embed(self, text: str) -> list[float]:
        """Anthropic doesn't have native embeddings, use placeholder."""
        raise NotImplementedError("Anthropic does not provide embeddings API")


class GoogleClient(BaseLLMClient):
    """Google Gemini API client implementation."""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        import google.generativeai as genai

        genai.configure(api_key=config.api_key)
        self._client = genai.GenerativeModel(config.model)
        logger.info(f"Google client initialized with model {config.model}")

    @traced(name="google_complete")
    async def complete(
        self,
        messages: list[LLMMessage],
        **kwargs,
    ) -> LLMResponse:
        """Generate completion using Google Gemini API."""
        # Convert messages to Gemini format
        history = []
        prompt = ""

        for m in messages:
            if m.role == "user":
                prompt = m.content
            elif m.role == "assistant":
                history.append({
                    "role": "model",
                    "parts": [m.content],
                })
            elif m.role == "system":
                # Prepend system message to first user message
                prompt = f"{m.content}\n\n{prompt}"

        chat = self._client.start_chat(history=history)
        response = await asyncio.to_thread(
            chat.send_message,
            prompt,
            generation_config={
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_output_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            },
        )

        add_span_attributes({
            "llm.provider": "google",
            "llm.model": self.config.model,
        })

        return LLMResponse(
            content=response.text,
            model=self.config.model,
            provider=LLMProvider.GOOGLE,
            usage={},
        )

    async def stream(
        self,
        messages: list[LLMMessage],
        **kwargs,
    ) -> AsyncIterator[str]:
        """Stream completion using Google Gemini API."""
        # Similar conversion logic
        prompt = ""
        for m in messages:
            if m.role == "user":
                prompt = m.content
            elif m.role == "system":
                prompt = f"{m.content}\n\n{prompt}"

        response = await asyncio.to_thread(
            self._client.generate_content,
            prompt,
            stream=True,
        )

        for chunk in response:
            if chunk.text:
                yield chunk.text

    async def embed(self, text: str) -> list[float]:
        """Generate embeddings using Google API."""
        import google.generativeai as genai

        result = await asyncio.to_thread(
            genai.embed_content,
            model="models/embedding-001",
            content=text,
        )
        return result["embedding"]


class HuggingFaceClient(BaseLLMClient):
    """Hugging Face Inference Endpoint client implementation."""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        import httpx

        # If base_url is provided, use it. Otherwise default to public API.
        base_url = config.base_url or "https://api-inference.huggingface.co/models"

        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {config.api_key}"} if config.api_key else {},
            timeout=config.timeout,
        )
        logger.info(
            f"Hugging Face client initialized with model {config.model}")

    @traced(name="huggingface_complete")
    async def complete(
        self,
        messages: list[LLMMessage],
        **kwargs,
    ) -> LLMResponse:
        """Generate completion using Hugging Face API."""
        # Simple chat template fallback
        prompt = ""
        for m in messages:
            role = m.role
            if role == "user":
                prompt += f"User: {m.content}\n"
            elif role == "assistant":
                prompt += f"Assistant: {m.content}\n"
            elif role == "system":
                prompt += f"System: {m.content}\n"
        prompt += "Assistant: "

        url = ""
        if not self.config.base_url:
            url = f"/{self.config.model}"

        payload = {
            "inputs": prompt,
            "parameters": {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_new_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "return_full_text": False,
            }
        }

        response = await self._client.post(url, json=payload)
        response.raise_for_status()
        result = response.json()

        # Handle different response formats (TGI vs standard)
        content = ""
        if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
            content = result[0]["generated_text"]
        elif isinstance(result, dict) and "generated_text" in result:
            content = result["generated_text"]
        else:
            content = str(result)

        return LLMResponse(
            content=content,
            model=self.config.model,
            provider=LLMProvider.HUGGINGFACE,
        )

    async def stream(
        self,
        messages: list[LLMMessage],
        **kwargs,
    ) -> AsyncIterator[str]:
        """Stream completion using Hugging Face API."""
        # Basic non-streaming fallback for now
        response = await self.complete(messages, **kwargs)
        yield response.content

    async def embed(self, text: str) -> list[float]:
        """Generate embeddings using Hugging Face API."""
        url = ""
        if not self.config.base_url:
            url = f"/{self.config.model}"

        response = await self._client.post(
            url,
            json={"inputs": text, "options": {"wait_for_model": True}}
        )
        response.raise_for_status()
        result = response.json()

        if isinstance(result, list) and len(result) > 0:
            # Handle nested list for batch or single
            if isinstance(result[0], list):
                return result[0]
            return result
        return []

    async def close(self):
        await self._client.aclose()


class LLMManager:
    """
    Manager for LLM providers with fallback and load balancing.
    """

    def __init__(self):
        self._clients: dict[LLMProvider, BaseLLMClient] = {}
        self._primary_provider: LLMProvider | None = None
        self._fallback_order: list[LLMProvider] = []

    def register_provider(
        self,
        config: LLMConfig,
        primary: bool = False,
    ) -> None:
        """Register an LLM provider."""
        client = self._create_client(config)
        self._clients[config.provider] = client

        if primary or self._primary_provider is None:
            self._primary_provider = config.provider

        if config.provider not in self._fallback_order:
            self._fallback_order.append(config.provider)

        logger.info(
            f"Registered {config.provider.value} provider "
            f"(primary={primary})"
        )

    def _create_client(self, config: LLMConfig) -> BaseLLMClient:
        """Create appropriate client based on provider."""
        if config.provider == LLMProvider.OPENAI:
            return OpenAIClient(config)
        elif config.provider == LLMProvider.ANTHROPIC:
            return AnthropicClient(config)
        elif config.provider == LLMProvider.GOOGLE:
            return GoogleClient(config)
        elif config.provider == LLMProvider.HUGGINGFACE:
            return HuggingFaceClient(config)
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")

    @traced(name="llm_complete")
    async def complete(
        self,
        messages: list[LLMMessage],
        provider: LLMProvider | None = None,
        fallback: bool = True,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate completion with optional fallback.

        Args:
            messages: List of messages for the conversation
            provider: Specific provider to use (optional)
            fallback: Whether to try fallback providers on failure
            **kwargs: Additional arguments passed to the client

        Returns:
            LLMResponse with the completion
        """
        providers_to_try = []

        if provider:
            providers_to_try = [provider]
            if fallback:
                providers_to_try.extend(
                    p for p in self._fallback_order if p != provider
                )
        else:
            providers_to_try = [self._primary_provider] + [
                p for p in self._fallback_order if p != self._primary_provider
            ]

        last_error = None
        for p in providers_to_try:
            if p not in self._clients:
                continue

            try:
                return await self._clients[p].complete(messages, **kwargs)
            except Exception as e:
                logger.warning(f"Provider {p.value} failed: {e}")
                last_error = e
                if not fallback:
                    raise

        raise RuntimeError(f"All providers failed. Last error: {last_error}")

    async def stream(
        self,
        messages: list[LLMMessage],
        provider: LLMProvider | None = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        """Stream completion from specified or primary provider."""
        p = provider or self._primary_provider
        if p not in self._clients:
            raise ValueError(f"Provider {p} not registered")

        async for chunk in self._clients[p].stream(messages, **kwargs):
            yield chunk

    async def embed(
        self,
        text: str,
        provider: LLMProvider | None = None,
    ) -> list[float]:
        """Generate embeddings from specified or primary provider."""
        p = provider or self._primary_provider
        if p not in self._clients:
            raise ValueError(f"Provider {p} not registered")

        return await self._clients[p].embed(text)

    async def close(self):
        """Close all client connections."""
        for client in self._clients.values():
            await client.close()


# Global manager instance
_llm_manager: LLMManager | None = None


def get_llm_manager() -> LLMManager:
    """Get or create the global LLM manager."""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager


async def initialize_llm_providers(
    openai_key: str | None = None,
    anthropic_key: str | None = None,
    google_key: str | None = None,
    huggingface_key: str | None = None,
    huggingface_url: str | None = None,
) -> LLMManager:
    """Initialize LLM providers from API keys."""
    manager = get_llm_manager()

    if openai_key:
        manager.register_provider(
            LLMConfig(
                provider=LLMProvider.OPENAI,
                model="gpt-4o",
                api_key=openai_key,
            ),
            primary=True,
        )

    if anthropic_key:
        manager.register_provider(
            LLMConfig(
                provider=LLMProvider.ANTHROPIC,
                model="claude-3-5-sonnet-20241022",
                api_key=anthropic_key,
            ),
        )

    if google_key:
        manager.register_provider(
            LLMConfig(
                provider=LLMProvider.GOOGLE,
                model="gemini-1.5-pro",
                api_key=google_key,
            ),
        )

    if huggingface_key:
        manager.register_provider(
            LLMConfig(
                provider=LLMProvider.HUGGINGFACE,
                model="tgi",
                api_key=huggingface_key,
                base_url=huggingface_url,
            ),
        )

    return manager

    return manager
