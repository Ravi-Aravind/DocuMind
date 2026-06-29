from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Sequence

from backend.app.rag.prompts.models import (
    Prompt,
    HistoryMessage,
)
from backend.app.rag.retrieval.base import RetrievedChunk


class PromptBuildError(Exception):
    """Base exception for all prompt building errors."""


class PromptTooLargeError(PromptBuildError):
    """Raised when prompt cannot fit within token budget."""


class InvalidPromptInputError(PromptBuildError):
    """Raised when inputs to a builder are invalid."""


class BasePromptBuilder(ABC):
    """Abstract base for all prompt builders."""

    @abstractmethod
    def build(
        self,
        question: str,
        chunks: Sequence[RetrievedChunk],
        history: Optional[Sequence[HistoryMessage]] = None,
        system_instructions: Optional[str] = None,
    ) -> Prompt:
        """Build a Prompt from a question and retrieved chunks."""
        raise NotImplementedError