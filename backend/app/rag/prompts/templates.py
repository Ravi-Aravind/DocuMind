from __future__ import annotations

from typing import List

from backend.app.rag.prompts.models import Citation, HistoryMessage, PromptType
from backend.app.rag.prompts.tokenizer import PROMPT_TEMPLATE_VERSION


STRICT_SYSTEM_PROMPT = """You are an academic RAG assistant.

You must answer using ONLY the provided document context. Do not use outside knowledge.
If the context is insufficient to answer the question reliably, say you cannot find the answer.
Always cite sources with document, page, and section information.
Never fabricate citations or information.
"""

STRICT_FALLBACK_USER_PROMPT = (
    "I could not find this in the provided documents. "
    "Can you share the relevant document?"
)

MCQ_SYSTEM_PROMPT = """You are an academic assistant that generates and evaluates multiple-choice questions
strictly from the provided document context. Do not use outside knowledge.
Never invent facts or options that are not supported by the context.
"""

CONVERSATION_SYSTEM_PROMPT = """You are a conversational academic assistant that must ground answers strictly
in the provided document context and relevant prior messages. Do not use outside knowledge.
If the documents do not contain enough information, say so explicitly.
"""


def _format_context_blocks(citations: List[Citation]) -> str:
    blocks: List[str] = []
    for i, c in enumerate(citations, start=1):
        blocks.append(
            f"--- Source {i} [{c.citation_id}] ---\n"
            f"Document ID: {c.document_id}\n"
            f"Title: {c.document_title or 'Unknown'}\n"
            f"Page: {c.page}\n"
            f"Section: {c.section or 'N/A'}\n"
            f"Snippet:\n{c.snippet}\n"
        )
    return "\n".join(blocks)


def strict_qa_user_prompt(question: str, citations: List[Citation]) -> str:
    if not citations:
        return STRICT_FALLBACK_USER_PROMPT

    context_blocks = _format_context_blocks(citations)
    return (
        f"You are given multiple source excerpts from academic or knowledge documents.\n\n"
        f"Context:\n{context_blocks}\n\n"
        f"Question:\n{question}\n\n"
        "Instructions:\n"
        "- Base your answer only on the context.\n"
        "- If you cannot answer confidently from the context, say you cannot answer from the documents.\n"
        "- Provide a concise, well-structured answer suitable for a student or researcher.\n"
        "- Do not mention that you were given 'context'; just answer normally.\n"
        "- When referring to sources, use citation IDs like [C1], [C2].\n"
    )


def mcq_user_prompt(question: str, citations: List[Citation], options_text: str) -> str:
    context_blocks = _format_context_blocks(citations) if citations else "No context provided."
    return (
        f"You are given multiple source excerpts from academic or knowledge documents.\n\n"
        f"Context:\n{context_blocks}\n\n"
        f"Question:\n{question}\n\n"
        f"Options:\n{options_text}\n\n"
        "Instructions:\n"
        "- For each option, assess how well it is supported by the context.\n"
        "- Choose the single best option.\n"
        "- Provide a short justification for your choice.\n"
        "- If none can be supported, say that explicitly.\n"
    )


def conversation_user_prompt(
    question: str,
    citations: List[Citation],
    history: List[HistoryMessage],
) -> str:
    context_blocks = _format_context_blocks(citations) if citations else "No context provided."
    history_text = "\n".join(
        f"{m.role.upper()}: {m.content}" for m in history
    ) or "No prior messages."
    return (
        f"Conversation history:\n{history_text}\n\n"
        f"Document context:\n{context_blocks}\n\n"
        f"Current question:\n{question}\n\n"
        "Instructions:\n"
        "- Use both the conversation history and the document context.\n"
        "- Base factual statements strictly on the documents.\n"
        "- If the documents do not contain enough information, say so explicitly.\n"
        "- When referring to sources, use citation IDs like [C1], [C2].\n"
    )


def system_prompt_for_type(prompt_type: PromptType) -> str:
    if prompt_type == PromptType.STRICT_QA:
        return STRICT_SYSTEM_PROMPT
    if prompt_type == PromptType.MCQ:
        return MCQ_SYSTEM_PROMPT
    if prompt_type == PromptType.CONVERSATION:
        return CONVERSATION_SYSTEM_PROMPT
    # Fallback
    return STRICT_SYSTEM_PROMPT


def current_template_version() -> str:
    return PROMPT_TEMPLATE_VERSION