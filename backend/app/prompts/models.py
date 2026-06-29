from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class PromptType(str, Enum):
    QA = "qa"
    MCQ = "mcq"


@dataclass
class PromptMetadata:
    prompt_type: PromptType
    num_chunks: int
    estimated_context_length: int
    template_name: str
    extra: Dict[str, str] = field(default_factory=dict)


@dataclass
class Prompt:
    """Provider-independent prompt representation."""

    system_prompt: str
    user_prompt: str
    metadata: Optional[PromptMetadata] = None