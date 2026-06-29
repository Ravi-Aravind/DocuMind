from __future__ import annotations


class LLMProviderError(Exception):
    """Base exception for LLM provider failures."""


class LLMAuthenticationError(LLMProviderError):
    """Authentication or authorization failure."""


class LLMRateLimitError(LLMProviderError):
    """Rate limit exceeded."""


class LLMTimeoutError(LLMProviderError):
    """Request timed out."""


class LLMUnavailableError(LLMProviderError):
    """Provider unavailable or internal error."""