from __future__ import annotations

from typing import List, Optional, Sequence

from backend.app.rag.prompts.base import (
    BasePromptBuilder,
    InvalidPromptInputError,
)
from backend.app.rag.prompts.models import (
    Prompt,
    PromptMetadata,
    PromptType,
    Citation,
    HistoryMessage,
)
from backend.app.rag.prompts.tokenizer import (
    MAX_CONTEXT_TOKENS,
    MAX_HISTORY_MESSAGES,
    estimate_tokens,
    truncate_context,
    truncate_history,
)
from backend.app.rag.prompts.templates import (
    strict_qa_user_prompt,
    mcq_user_prompt,
    conversation_user_prompt,
    system_prompt_for_type,
    current_template_version,
)
from backend.app.rag.retrieval.base import RetrievedChunk


def _build_citations(chunks: Sequence[RetrievedChunk]) -> List[Citation]:
    citations: List[Citation] = []
    for idx, c in enumerate(chunks, start=1):
        citation_id = f"C{idx}"
        snippet = c.text[:500]
        citations.append(
            Citation(
                citation_id=citation_id,
                document_id=c.document_id,
                document_title=c.document_title,
                page=c.page,
                section=c.section,
                score=c.score,
                snippet=snippet,
            )
        )
    return citations


class StrictRAGPromptBuilder(BasePromptBuilder):
    def build(
        self,
        question: str,
        chunks: Sequence[RetrievedChunk],
        history: Optional[Sequence[HistoryMessage]] = None,
        system_instructions: Optional[str] = None,
    ) -> Prompt:
        if not question.strip():
            raise InvalidPromptInputError("Question must not be empty")

        # Token budgeting for context
        kept_chunks, _removed = truncate_context(chunks, max_tokens=MAX_CONTEXT_TOKENS)

        citations = _build_citations(kept_chunks)
        user_prompt = strict_qa_user_prompt(question, citations)
        system_prompt = system_instructions or system_prompt_for_type(PromptType.STRICT_QA)

        context_texts = [c.text for c in kept_chunks]
        context_tokens = sum(estimate_tokens(t) for t in context_texts)
        history_tokens = 0  # Strict QA ignores history
        total_tokens = estimate_tokens(system_prompt) + estimate_tokens(user_prompt) + context_tokens

        metadata = PromptMetadata(
            prompt_type=PromptType.STRICT_QA,
            num_chunks=len(kept_chunks),
            context_token_count=context_tokens,
            history_token_count=history_tokens,
            total_token_count=total_tokens,
            truncated=len(kept_chunks) < len(chunks),
            template_version=current_template_version(),
            max_context_tokens=MAX_CONTEXT_TOKENS,
            max_history_messages=MAX_HISTORY_MESSAGES,
        )

        return Prompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            context=context_texts,
            citations=citations,
            metadata=metadata,
        )


class MCQPromptBuilder(BasePromptBuilder):
    def build(
        self,
        question: str,
        chunks: Sequence[RetrievedChunk],
        history: Optional[Sequence[HistoryMessage]] = None,
        system_instructions: Optional[str] = None,
        options: Optional[List[str]] = None,
    ) -> Prompt:
        if not question.strip():
            raise InvalidPromptInputError("Question must not be empty")

        kept_chunks, _removed = truncate_context(chunks, max_tokens=MAX_CONTEXT_TOKENS)
        citations = _build_citations(kept_chunks)

        options_text = ""
        if options:
            options_text = "\n".join(options)

        user_prompt = mcq_user_prompt(question, citations, options_text)
        system_prompt = system_instructions or system_prompt_for_type(PromptType.MCQ)

        context_texts = [c.text for c in kept_chunks]
        context_tokens = sum(estimate_tokens(t) for t in context_texts)
        history_tokens = 0
        total_tokens = estimate_tokens(system_prompt) + estimate_tokens(user_prompt) + context_tokens

        metadata = PromptMetadata(
            prompt_type=PromptType.MCQ,
            num_chunks=len(kept_chunks),
            context_token_count=context_tokens,
            history_token_count=history_tokens,
            total_token_count=total_tokens,
            truncated=len(kept_chunks) < len(chunks),
            template_version=current_template_version(),
            max_context_tokens=MAX_CONTEXT_TOKENS,
            max_history_messages=MAX_HISTORY_MESSAGES,
        )

        return Prompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            context=context_texts,
            citations=citations,
            metadata=metadata,
        )


class ConversationPromptBuilder(BasePromptBuilder):
    def build(
        self,
        question: str,
        chunks: Sequence[RetrievedChunk],
        history: Optional[Sequence[HistoryMessage]] = None,
        system_instructions: Optional[str] = None,
    ) -> Prompt:
        if not question.strip():
            raise InvalidPromptInputError("Question must not be empty")

        kept_chunks, _removed = truncate_context(chunks, max_tokens=MAX_CONTEXT_TOKENS)
        citations = _build_citations(kept_chunks)

        history_seq = list(history or [])
        # Truncate history by messages and tokens (we use same MAX_CONTEXT_TOKENS for simplicity)
        truncated_history = truncate_history(
            history_seq,
            max_messages=MAX_HISTORY_MESSAGES,
            max_tokens=MAX_CONTEXT_TOKENS,
        )

        user_prompt = conversation_user_prompt(question, citations, truncated_history)
        system_prompt = system_instructions or system_prompt_for_type(PromptType.CONVERSATION)

        context_texts = [c.text for c in kept_chunks]
        context_tokens = sum(estimate_tokens(t) for t in context_texts)
        history_tokens = sum(estimate_tokens(m.content) for m in truncated_history)
        total_tokens = (
            estimate_tokens(system_prompt)
            + estimate_tokens(user_prompt)
            + context_tokens
            + history_tokens
        )

        metadata = PromptMetadata(
            prompt_type=PromptType.CONVERSATION,
            num_chunks=len(kept_chunks),
            context_token_count=context_tokens,
            history_token_count=history_tokens,
            total_token_count=total_tokens,
            truncated=len(kept_chunks) < len(chunks) or len(truncated_history) < len(history_seq),
            template_version=current_template_version(),
            max_context_tokens=MAX_CONTEXT_TOKENS,
            max_history_messages=MAX_HISTORY_MESSAGES,
        )

        return Prompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            context=context_texts,
            citations=citations,
            metadata=metadata,
        )