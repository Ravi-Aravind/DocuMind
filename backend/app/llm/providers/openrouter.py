from __future__ import annotations

import logging
import time
from typing import Optional

import httpx

from backend.app.config import settings
from backend.app.llm.base import BaseLLMProvider
from backend.app.llm.exceptions import (
    LLMAuthenticationError,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMUnavailableError,
)
from backend.app.llm.models import LLMRequest, LLMResponse, TokenUsage

logger = logging.getLogger(__name__)


class OpenRouterProvider(BaseLLMProvider):
    """Async LLM provider using OpenRouter."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        temperature: Optional[float] = None,
    ) -> None:
        self.api_key = api_key or settings.openrouter_api_key
        self.base_url = base_url or settings.openrouter_endpoint
        self.model = model or settings.openrouter_model
        self.timeout_seconds = timeout_seconds or settings.llm_timeout
        self.default_temperature = temperature if temperature is not None else settings.llm_temperature

        if not self.api_key:
            raise LLMAuthenticationError("OPENROUTER_API_KEY is not configured")

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a completion via OpenRouter."""

        temperature = request.temperature if request.temperature is not None else self.default_temperature
        max_tokens = request.max_tokens

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "temperature": temperature,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful academic assistant.",
                },
                {
                    "role": "user",
                    "content": request.prompt,
                },
            ],
        }
        if max_tokens is not None:
            body["max_tokens"] = max_tokens

        start = time.monotonic()
        status_code = None

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                resp = await client.post(self.base_url, json=body, headers=headers)
            status_code = resp.status_code

            if status_code == 401 or status_code == 403:
                raise LLMAuthenticationError(f"OpenRouter auth error (status={status_code})")
            if status_code == 429:
                raise LLMRateLimitError("OpenRouter rate limit exceeded")
            if status_code >= 500:
                raise LLMUnavailableError(f"OpenRouter server error (status={status_code})")

            resp.raise_for_status()
            data = resp.json()

        except httpx.TimeoutException as exc:
            logger.warning("OpenRouter timeout", extra={"provider": "openrouter"})
            raise LLMTimeoutError("OpenRouter request timed out") from exc
        except httpx.HTTPError as exc:
            logger.error(
                "OpenRouter HTTP error",
                extra={"provider": "openrouter", "status_code": status_code},
            )
            raise LLMProviderError(f"OpenRouter HTTP error: {exc}") from exc

        latency = time.monotonic() - start

        # OpenRouter follows OpenAI-style shape
        choices = data.get("choices") or []
        if not choices:
            raise LLMProviderError("OpenRouter response missing choices")

        message = choices[0].get("message") or {}
        content = message.get("content") or ""

        usage_data = data.get("usage") or {}
        usage = None
        if usage_data:
            usage = TokenUsage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
            )

        # Structured logging (no API keys, no full prompts)
        logger.info(
            "LLM call completed",
            extra={
                "provider": "openrouter",
                "model": self.model,
                "latency_ms": int(latency * 1000),
                "status_code": status_code,
                "prompt_tokens": usage.prompt_tokens if usage else None,
                "completion_tokens": usage.completion_tokens if usage else None,
                "total_tokens": usage.total_tokens if usage else None,
            },
        )

        return LLMResponse(
            content=content,
            usage=usage,
            model=self.model,
            provider="openrouter",
            raw=data,
        )

    async def stream(self, request: LLMRequest):
        """Streaming not implemented yet."""
        raise NotImplementedError("Streaming API not implemented for OpenRouterProvider")

    async def health(self) -> bool:
        """Basic health check: verifies we have API key and can construct client.

        Does not perform an external call.
        """
        return bool(self.api_key and self.base_url and self.model)