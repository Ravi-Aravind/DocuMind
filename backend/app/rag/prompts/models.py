from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class PromptType(str, Enum):
    STRICT_QA = "strict_qa"
    MCQ = "mcq"
    CONVERSATION = "conversation"


@dataclass
class Citation:
    citation_id: str
    document_id: str
    document_title: Optional[str]
    page: int
    section: Optional[str]
    score: float
    snippet: str


@dataclass
class HistoryMessage:
    role: str  # "user" | "assistant"
    content: str


@dataclass
class PromptMetadata:
    prompt_type: PromptType
    num_chunks: int
    context_token_count: int
    history_token_count: int
    total_token_count: int
    truncated: bool
    template_version: str
    max_context_tokens: int
    max_history_messages: int


@dataclass
class Prompt:
    system_prompt: str
    user_prompt: str
    context: List[str] = field(default_factory=list)
    citations: List[Citation] = field(default_factory=list)
    metadata: Optional[PromptMetadata] = None