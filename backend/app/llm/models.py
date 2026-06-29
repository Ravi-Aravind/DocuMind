from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class LLMRequest:
    prompt: str
    temperature: float = 0.0
    max_tokens: Optional[int] = None


@dataclass
class LLMResponse:
    content: str
    usage: Optional[TokenUsage] = None
    model: Optional[str] = None
    provider: Optional[str] = None
    raw: Optional[Any] = None
