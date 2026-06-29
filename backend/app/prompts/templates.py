from __future__ import annotations

from typing import List

from backend.app.prompts.models import PromptType


QA_SYSTEM_PROMPT = """You are an academic RAG assistant.

You must answer using ONLY the provided document context. Do not use outside knowledge.
If the context is insufficient to answer the question reliably, say you cannot find the answer.
Always cite sources with document, page, and section information.
"""

QA_USER_TEMPLATE = """You are given multiple source excerpts from academic or knowledge documents.

Context:
{context_blocks}

Question:
{question}

Instructions:
- Base your answer only on the context.
- If you cannot answer confidently from the context, say you cannot answer from the documents.
- Provide a concise, well-structured answer suitable for a student or researcher.
- Do not mention that you were given 'context'; just answer normally.
"""

MCQ_SYSTEM_PROMPT = QA_SYSTEM_PROMPT

MCQ_USER_TEMPLATE = """You are given multiple source excerpts from academic or knowledge documents.

Context:
{context_blocks}

Question:
{question}

Options:
{options_block}

Instructions:
- For each option, assess how well it is supported by the context.
- Choose the single best option.
- Provide a short justification for your choice.
- If none can be supported, say that explicitly.
"""


def format_context_blocks(
    context_blocks: List[str],
) -> str:
    """Join preformatted context blocks into a single string."""
    return "\n\n".join(context_blocks)


def qa_system_prompt() -> str:
    return QA_SYSTEM_PROMPT


def qa_user_prompt(context_blocks: List[str], question: str) -> str:
    return QA_USER_TEMPLATE.format(
        context_blocks=format_context_blocks(context_blocks),
        question=question,
    )


def mcq_system_prompt() -> str:
    return MCQ_SYSTEM_PROMPT


def mcq_user_prompt(context_blocks: List[str], question: str, options_block: str) -> str:
    return MCQ_USER_TEMPLATE.format(
        context_blocks=format_context_blocks(context_blocks),
        question=question,
        options_block=options_block,
    )


def template_name_for_type(prompt_type: PromptType) -> str:
    if prompt_type == PromptType.QA:
        return "qa_v1"
    if prompt_type == PromptType.MCQ:
        return "mcq_v1"
    return "unknown"