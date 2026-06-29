from __future__ import annotations

import logging
from typing import Iterable, List, Optional, Sequence

from backend.app.prompts.models import Prompt, PromptMetadata, PromptType
from backend.app.prompts.templates import (
    qa_system_prompt,
    qa_user_prompt,
    mcq_system_prompt,
    mcq_user_prompt,
    template_name_for_type,
)
from backend.app.rag.retrieval.base import RetrievedChunk
from backend.app.schemas.qa import MCQOption

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Builds provider-independent prompts for QA and MCQ tasks."""

    def __init__(self) -> None:
        # Future: accept config, token limits, etc.
        pass

    @staticmethod
    def _deduplicate_and_preserve_order(chunks: Sequence[RetrievedChunk]) -> List[RetrievedChunk]:
        """Remove duplicate chunks while preserving document/page/chunk ordering."""
        seen = set()
        result: List[RetrievedChunk] = []
        for c in chunks:
            key = (c.document_id, c.page, c.section, c.chunk_index, c.text)
            if key in seen:
                continue
            seen.add(key)
            result.append(c)
        return result

    @staticmethod
    def _build_context_blocks(chunks: Sequence[RetrievedChunk]) -> List[str]:
        """Build preformatted context blocks from retrieved chunks.

        Preserves document ordering, chunk ordering, page numbers, and section titles.
        """
        blocks: List[str] = []
        for i, c in enumerate(chunks):
            blocks.append(
                f"--- Source {i + 1} ---\n"
                f"Document ID: {c.document_id}\n"
                f"Title: {c.document_title or 'Unknown'}\n"
                f"Page: {c.page}\n"
                f"Section: {c.section or 'N/A'}\n"
                f"Score: {c.score:.4f}\n"
                f"Content: {c.text}"
            )
        return blocks

    @staticmethod
    def _estimate_context_length(chunks: Iterable[RetrievedChunk]) -> int:
        """Estimate context length by simple character count."""
        return sum(len(c.text) for c in chunks)

    @staticmethod
    def _build_mcq_options_block(options: Sequence[MCQOption]) -> str:
        lines: List[str] = []
        for opt in options:
            lines.append(f"{opt.id}. {opt.text}")
        return "\n".join(lines)

    def build_qa_prompt(
        self,
        question: str,
        chunks: Sequence[RetrievedChunk],
        history: Optional[Sequence[str]] = None,
    ) -> Prompt:
        """Build QA prompt from question and retrieved chunks."""
        deduped = self._deduplicate_and_preserve_order(chunks)
        context_blocks = self._build_context_blocks(deduped)
        est_len = self._estimate_context_length(deduped)

        logger.info(
            "PromptBuilder QA",
            extra={
                "prompt_type": "qa",
                "chunk_count": len(deduped),
                "estimated_context_length": est_len,
            },
        )

        system = qa_system_prompt()
        user = qa_user_prompt(context_blocks=context_blocks, question=question)

        metadata = PromptMetadata(
            prompt_type=PromptType.QA,
            num_chunks=len(deduped),
            estimated_context_length=est_len,
            template_name=template_name_for_type(PromptType.QA),
            extra={},
        )
        return Prompt(system_prompt=system, user_prompt=user, metadata=metadata)

    def build_mcq_prompt(
        self,
        question: str,
        chunks: Sequence[RetrievedChunk],
        options: Sequence[MCQOption],
        history: Optional[Sequence[str]] = None,
    ) -> Prompt:
        """Build MCQ prompt from question, retrieved chunks, and options."""
        deduped = self._deduplicate_and_preserve_order(chunks)
        context_blocks = self._build_context_blocks(deduped)
        est_len = self._estimate_context_length(deduped)

        logger.info(
            "PromptBuilder MCQ",
            extra={
                "prompt_type": "mcq",
                "chunk_count": len(deduped),
                "estimated_context_length": est_len,
            },
        )

        options_block = self._build_mcq_options_block(options)
        system = mcq_system_prompt()
        user = mcq_user_prompt(
            context_blocks=context_blocks,
            question=question,
            options_block=options_block,
        )

        metadata = PromptMetadata(
            prompt_type=PromptType.MCQ,
            num_chunks=len(deduped),
            estimated_context_length=est_len,
            template_name=template_name_for_type(PromptType.MCQ),
            extra={},
        )
        return Prompt(system_prompt=system, user_prompt=user, metadata=metadata)