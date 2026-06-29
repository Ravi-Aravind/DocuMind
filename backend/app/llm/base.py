from __future__ import annotations

from abc import ABC, abstractmethod

from backend.app.llm.models import LLMRequest, LLMResponse


class BaseLLMProvider(ABC):
    """Provider-independent LLM interface."""

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a completion for the given request."""
        raise NotImplementedError

    @abstractmethod
    async def stream(self, request: LLMRequest):
        """Stream tokens for the given request (interface TBD)."""
        raise NotImplementedError

    @abstractmethod
    async def health(self) -> bool:
        """Return True if provider is healthy."""
        raise NotImplementedError