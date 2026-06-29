from __future__ import annotations

import logging
import time
from typing import Optional

import httpx

from backend.app.config import settings

logger = logging.getLogger(__name__)


class OpenRouterError(Exception):
    """Base exception for OpenRouter LLM errors."""


class OpenRouterAuthenticationError(OpenRouterError):
    """Authentication or authorization failure."""


class OpenRouterTimeoutError(OpenRouterError):
    """Request timed out."""


class OpenRouterUnavailableError(OpenRouterError):
    """Provider unavailable or internal error."""


class OpenRouterRateLimitError(OpenRouterError):
    """Rate limit exceeded."""


class OpenRouterResponseError(OpenRouterError):
    """Malformed or unexpected response from provider."""


class OpenRouterService:
    """Service responsible for all LLM communication via OpenRouter.

    Encapsulates endpoint, headers, payloads, response parsing, and error handling.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        temperature: Optional[float] = None,
        max_retries: int = 1,
    ) -> None:
        self.api_key: str = api_key or settings.openrouter_api_key
        self.endpoint: str = endpoint or settings.openrouter_endpoint
        self.model: str = model or settings.openrouter_model
        self.timeout_seconds: float = timeout_seconds or settings.llm_timeout
        self.temperature: float = temperature if temperature is not None else settings.llm_temperature
        self.max_retries: int = max_retries

        if not self.api_key:
            raise OpenRouterAuthenticationError("OPENROUTER_API_KEY is not configured")

    async def generate(self, prompt: str) -> str:
        """Generate a completion for the given prompt using OpenRouter."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "temperature": self.temperature,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful academic assistant.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        }

        attempt = 0
        last_error: Optional[Exception] = None

        while attempt <= self.max_retries:
            start = time.monotonic()
            status_code: Optional[int] = None

            try:
                async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                    resp = await client.post(self.endpoint, json=body, headers=headers)
                status_code = resp.status_code

                if status_code in (401, 403):
                    raise OpenRouterAuthenticationError(
                        f"OpenRouter authentication failed (status={status_code})"
                    )
                if status_code == 429:
                    raise OpenRouterRateLimitError("OpenRouter rate limit exceeded")
                if status_code >= 500:
                    raise OpenRouterUnavailableError(
                        f"OpenRouter provider unavailable (status={status_code})"
                    )

                resp.raise_for_status()
                data = resp.json()
            except httpx.TimeoutException as exc:
                logger.warning(
                    "OpenRouter timeout",
                    extra={
                        "provider": "openrouter",
                        "model": self.model,
                        "timeout_seconds": self.timeout_seconds,
                        "attempt": attempt,
                    },
                )
                last_error = OpenRouterTimeoutError("OpenRouter request timed out")
            except httpx.HTTPError as exc:
                logger.error(
                    "OpenRouter HTTP error",
                    extra={
                        "provider": "openrouter",
                        "model": self.model,
                        "status_code": status_code,
                        "attempt": attempt,
                    },
                )
                last_error = OpenRouterError(f"OpenRouter HTTP error: {exc}")
            else:
                latency = time.monotonic() - start

                choices = data.get("choices") or []
                if not choices:
                    logger.error(
                        "OpenRouter response missing choices",
                        extra={
                            "provider": "openrouter",
                            "model": self.model,
                            "status_code": status_code,
                        },
                    )
                    raise OpenRouterResponseError("OpenRouter response missing choices")

                message = choices[0].get("message") or {}
                content = message.get("content") or ""

                usage_data = data.get("usage") or {}
                prompt_tokens = usage_data.get("prompt_tokens")
                completion_tokens = usage_data.get("completion_tokens")
                total_tokens = usage_data.get("total_tokens")

                # Structured logging (no prompts, no API keys, no full responses)
                logger.info(
                    "OpenRouter LLM call completed",
                    extra={
                        "provider": "openrouter",
                        "model": self.model,
                        "latency_ms": int(latency * 1000),
                        "status_code": status_code,
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": total_tokens,
                        "attempt": attempt,
                    },
                )

                return content

            # If we get here, we had an error
            attempt += 1
            if attempt > self.max_retries:
                # Exhausted retries: raise last error
                if isinstance(last_error, OpenRouterError):
                    raise last_error
                raise OpenRouterError("OpenRouter request failed")  # safety fallback

        # Should not reach here
        raise OpenRouterError("OpenRouter request failed")