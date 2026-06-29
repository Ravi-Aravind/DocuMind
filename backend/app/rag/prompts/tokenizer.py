from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

from backend.app.rag.retrieval.base import RetrievedChunk
from backend.app.rag.prompts.models import HistoryMessage

# Simple config; wire into Settings later if desired
MAX_CONTEXT_TOKENS = 2048
MAX_HISTORY_MESSAGES = 10
PROMPT_TEMPLATE_VERSION = "v1"


def estimate_tokens(text: str) -> int:
    """Heuristic token estimator: whitespace-based word count."""
    if not text:
        return 0
    return len(text.split())


def _estimate_chunks_tokens(chunks: Sequence[RetrievedChunk]) -> int:
    return sum(estimate_tokens(c.text) for c in chunks)


def _estimate_history_tokens(history: Sequence[HistoryMessage]) -> int:
    return sum(estimate_tokens(m.content) for m in history)


def truncate_context(
    chunks: Sequence[RetrievedChunk],
    max_tokens: int = MAX_CONTEXT_TOKENS,
) -> Tuple[List[RetrievedChunk], List[RetrievedChunk]]:
    """Return chunks truncated to max_tokens, preserving ordering.

    Chunks are atomic; they are either fully included or excluded.
    """
    kept: List[RetrievedChunk] = []
    removed: List[RetrievedChunk] = []
    total = 0

    for chunk in chunks:
        tokens = estimate_tokens(chunk.text)
        if total + tokens <= max_tokens:
            kept.append(chunk)
            total += tokens
        else:
            removed.append(chunk)

    return kept, removed


def truncate_history(
    history: Sequence[HistoryMessage],
    max_messages: int = MAX_HISTORY_MESSAGES,
    max_tokens: int | None = None,
) -> List[HistoryMessage]:
    """Truncate history to the last `max_messages`, then enforce token budget."""
    if not history:
        return []

    # Keep most recent max_messages
    trimmed = list(history[-max_messages:])

    if max_tokens is None:
        return trimmed

    # Enforce token budget by dropping older messages first
    result: List[HistoryMessage] = []
    total = 0
    # Iterate from newest to oldest, but build reversed to keep chronological order
    for msg in reversed(trimmed):
        tokens = estimate_tokens(msg.content)
        if total + tokens <= max_tokens:
            result.append(msg)
            total += tokens
        else:
            # stop once we hit token budget
            break

    # result currently newest-first, so reverse it back to chronological order
    return list(reversed(result))