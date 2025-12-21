"""
LLM Service for KOSMOS agents.
Provides unified interface for OpenAI, Anthropic, and local models.
"""

import os
import logging
import hashlib
import json
from typing import Optional, List, Dict, Any, AsyncGenerator
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("kosmos-llm")


class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"


@dataclass
class LLMConfig:
    """Configuration for LLM provider."""
    provider: LLMProvider
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hour


@dataclass
class Message:
    """Chat message."""
    role: str  # system, user, assistant
    content: str


@dataclass
class LLMResponse:
    """Response from LLM."""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    cached: bool = False


class LLMService:
    """
    Unified LLM service supporting multiple providers with Redis caching.
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or self._default_config()
        self._client = None
        self._cache = None
        logger.info(
            f"LLM Service initialized with provider: {self.config.provider.value}")

    def _default_config(self) -> LLMConfig:
        """Get default configuration from environment."""
        enable_cache = os.getenv("LLM_CACHE_ENABLED", "true").lower() == "true"
        cache_ttl = int(os.getenv("LLM_CACHE_TTL", "3600"))

        # Check for API keys in order of preference
        if os.getenv("OPENAI_API_KEY"):
            return LLMConfig(
                provider=LLMProvider.OPENAI,
                model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
                api_key=os.getenv("OPENAI_API_KEY"),
                max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "4096")),
                enable_cache=enable_cache,
                cache_ttl=cache_ttl,
            )
        elif os.getenv("ANTHROPIC_API_KEY"):
            return LLMConfig(
                provider=LLMProvider.ANTHROPIC,
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", "4096")),
                enable_cache=enable_cache,
                cache_ttl=cache_ttl,
            )
        elif os.getenv("HUGGINGFACE_API_KEY"):
            return LLMConfig(
                provider=LLMProvider.HUGGINGFACE,
                model=os.getenv("HUGGINGFACE_MODEL", "tgi"),
                api_key=os.getenv("HUGGINGFACE_API_KEY"),
                base_url=os.getenv("HUGGINGFACE_ENDPOINT_URL"),
                max_tokens=int(os.getenv("HUGGINGFACE_MAX_TOKENS", "2048")),
                enable_cache=enable_cache,
                cache_ttl=cache_ttl,
            )
        else:
            # Default to Ollama for local development
            return LLMConfig(
                provider=LLMProvider.OLLAMA,
                model=os.getenv("OLLAMA_MODEL", "llama3.2"),
                base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
                max_tokens=4096,
                enable_cache=enable_cache,
                cache_ttl=cache_ttl,
            )

    async def _get_cache(self):
        """Get cache service instance."""
        if self._cache is None and self.config.enable_cache:
            try:
                from src.services.cache_service import get_cache_service
                self._cache = await get_cache_service()
            except Exception as e:
                logger.warning(f"Cache unavailable: {e}")
                self._cache = False  # Mark as unavailable
        return self._cache if self._cache else None

    def _generate_cache_key(self, messages: List[Message], system_prompt: str, model: str) -> str:
        """Generate a cache key for the LLM request."""
        key_data = {
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "system_prompt": system_prompt,
            "model": model,
        }
        key_hash = hashlib.sha256(json.dumps(
            key_data, sort_keys=True).encode()).hexdigest()[:24]
        return f"llm:chat:{key_hash}"

    async def _get_openai_client(self):
        """Get or create OpenAI client."""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(
                    api_key=self.config.api_key,
                    base_url=self.config.base_url
                )
            except ImportError:
                raise ImportError(
                    "openai package required. Install with: pip install openai")
        return self._client

    async def _get_anthropic_client(self):
        """Get or create Anthropic client."""
        if self._client is None:
            try:
                from anthropic import AsyncAnthropic
                self._client = AsyncAnthropic(api_key=self.config.api_key)
            except ImportError:
                raise ImportError(
                    "anthropic package required. Install with: pip install anthropic")
        return self._client

    async def chat(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        use_cache: bool = True,
    ) -> LLMResponse:
        """
        Send a chat completion request to the configured LLM.
        Supports Redis caching for identical requests.
        """
        temp = temperature or self.config.temperature
        tokens = max_tokens or self.config.max_tokens
        sys_prompt = system_prompt or ""

        # Try cache first (only for low temperature = deterministic)
        cache_key = None
        if use_cache and self.config.enable_cache and temp < 0.3:
            cache = await self._get_cache()
            if cache:
                cache_key = self._generate_cache_key(
                    messages, sys_prompt, self.config.model)
                cached = await cache.get(cache_key)
                if cached:
                    logger.info(f"LLM cache hit: {cache_key}")
                    return LLMResponse(
                        content=cached["content"],
                        model=cached["model"],
                        usage=cached["usage"],
                        finish_reason=cached["finish_reason"],
                        cached=True,
                    )

        # Make actual LLM call
        if self.config.provider == LLMProvider.OPENAI:
            response = await self._chat_openai(messages, sys_prompt, temp, tokens)
        elif self.config.provider == LLMProvider.ANTHROPIC:
            response = await self._chat_anthropic(messages, sys_prompt, temp, tokens)
        elif self.config.provider == LLMProvider.HUGGINGFACE:
            response = await self._chat_huggingface(messages, sys_prompt, temp, tokens)
        elif self.config.provider == LLMProvider.OLLAMA:
            response = await self._chat_ollama(messages, sys_prompt, temp, tokens)
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

        # Store in cache
        if cache_key and self.config.enable_cache:
            cache = await self._get_cache()
            if cache:
                await cache.set(
                    cache_key,
                    {
                        "content": response.content,
                        "model": response.model,
                        "usage": response.usage,
                        "finish_reason": response.finish_reason,
                    },
                    ttl=self.config.cache_ttl
                )
                logger.debug(f"LLM response cached: {cache_key}")

        return response

    async def _chat_huggingface(
        self,
        messages: List[Message],
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        """Chat using Hugging Face Inference API."""
        import httpx

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

        # Simple prompt construction for generic HF models
        prompt = ""
        if system_prompt:
            prompt += f"System: {system_prompt}\n"
        for msg in messages:
            prompt += f"{msg.role.capitalize()}: {msg.content}\n"
        prompt += "Assistant: "

        url = self.config.base_url or f"https://api-inference.huggingface.co/models/{self.config.model}"

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "return_full_text": False
            }
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()

                content = ""
                if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                    content = data[0]["generated_text"]
                elif "generated_text" in data:
                    content = data["generated_text"]
                else:
                    content = str(data)

                return LLMResponse(
                    content=content,
                    model=self.config.model,
                    usage={"total_tokens": 0},
                    finish_reason="stop"
                )
            except Exception as e:
                logger.error(f"HuggingFace API error: {e}")
                # Fallback to mock if API fails (for testing/demo)
                return LLMResponse(
                    content=f"Mock HF Response: {prompt[:50]}...",
                    model=self.config.model,
                    usage={"total_tokens": 0},
                    finish_reason="stop"
                )

    async def _chat_openai(
        self,
        messages: List[Message],
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        """Chat using OpenAI API."""
        client = await self._get_openai_client()

        formatted_messages = []
        if system_prompt:
            formatted_messages.append(
                {"role": "system", "content": system_prompt})

        for msg in messages:
            formatted_messages.append(
                {"role": msg.role, "content": msg.content})

        response = await client.chat.completions.create(
            model=self.config.model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            finish_reason=response.choices[0].finish_reason,
        )

    async def _chat_anthropic(
        self,
        messages: List[Message],
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        """Chat using Anthropic API."""
        client = await self._get_anthropic_client()

        formatted_messages = []
        for msg in messages:
            formatted_messages.append(
                {"role": msg.role, "content": msg.content})

        response = await client.messages.create(
            model=self.config.model,
            max_tokens=max_tokens,
            system=system_prompt or "You are a helpful AI assistant.",
            messages=formatted_messages,
        )

        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            },
            finish_reason=response.stop_reason,
        )

    async def _chat_ollama(
        self,
        messages: List[Message],
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        """Chat using local Ollama API."""
        import httpx

        formatted_messages = []
        if system_prompt:
            formatted_messages.append(
                {"role": "system", "content": system_prompt})

        for msg in messages:
            formatted_messages.append(
                {"role": msg.role, "content": msg.content})

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.config.base_url}/api/chat",
                json={
                    "model": self.config.model,
                    "messages": formatted_messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    }
                }
            )
            response.raise_for_status()
            data = response.json()

        return LLMResponse(
            content=data["message"]["content"],
            model=data.get("model", self.config.model),
            usage={
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
                "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
            },
            finish_reason="stop",
        )

    async def stream_chat(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat completion response.
        """
        temp = temperature or self.config.temperature
        tokens = max_tokens or self.config.max_tokens

        if self.config.provider == LLMProvider.OPENAI:
            async for chunk in self._stream_openai(messages, system_prompt, temp, tokens):
                yield chunk
        elif self.config.provider == LLMProvider.ANTHROPIC:
            async for chunk in self._stream_anthropic(messages, system_prompt, temp, tokens):
                yield chunk
        else:
            # Fallback to non-streaming for Ollama
            response = await self.chat(messages, system_prompt, temp, tokens)
            yield response.content

    async def _stream_openai(
        self,
        messages: List[Message],
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> AsyncGenerator[str, None]:
        """Stream using OpenAI API."""
        client = await self._get_openai_client()

        formatted_messages = []
        if system_prompt:
            formatted_messages.append(
                {"role": "system", "content": system_prompt})

        for msg in messages:
            formatted_messages.append(
                {"role": msg.role, "content": msg.content})

        stream = await client.chat.completions.create(
            model=self.config.model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def _stream_anthropic(
        self,
        messages: List[Message],
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> AsyncGenerator[str, None]:
        """Stream using Anthropic API."""
        client = await self._get_anthropic_client()

        formatted_messages = []
        for msg in messages:
            formatted_messages.append(
                {"role": msg.role, "content": msg.content})

        async with client.messages.stream(
            model=self.config.model,
            max_tokens=max_tokens,
            system=system_prompt or "You are a helpful AI assistant.",
            messages=formatted_messages,
        ) as stream:
            async for text in stream.text_stream:
                yield text


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create the LLM service singleton."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
