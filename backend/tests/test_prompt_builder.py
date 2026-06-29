from __future__ import annotations

import pytest

from backend.app.prompts import PromptBuilder, PromptType
from backend.app.prompts.models import Prompt, PromptMetadata
from backend.app.rag.retrieval.base import RetrievedChunk
from backend.app.schemas.qa import MCQOption


def make_chunk(
    text: str,
    document_id: str = "doc-1",
    page: int = 1,
    section: str | None = None,
    score: float = 0.9,
    document_title: str | None = None,
    chunk_index: int | None = None,
) -> RetrievedChunk:
    return RetrievedChunk(
        text=text,
        page=page,
        section=section,
        score=score,
        document_id=document_id,
        document_title=document_title,
        chunk_index=chunk_index,
    )


def make_mcq_options() -> list[MCQOption]:
    return [
        MCQOption(id="A", text="Option A"),
        MCQOption(id="B", text="Option B"),
        MCQOption(id="C", text="Option C"),
    ]


@pytest.fixture
def prompt_builder() -> PromptBuilder:
    return PromptBuilder()


# ---------------------------------------------------------------------------
# 1. QA prompt generation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_qa_prompt_generation(prompt_builder: PromptBuilder):
    chunks = [
        make_chunk("Some context about X.", document_title="Doc X", chunk_index=0),
        make_chunk("Additional details.", document_title="Doc X", chunk_index=1),
    ]
    prompt: Prompt = prompt_builder.build_qa_prompt(question="What is X?", chunks=chunks)

    assert isinstance(prompt, Prompt)
    assert "What is X?" in prompt.user_prompt
    assert "Some context about X." in prompt.user_prompt
    assert "Additional details." in prompt.user_prompt

    assert prompt.metadata is not None
    assert isinstance(prompt.metadata, PromptMetadata)
    assert prompt.metadata.prompt_type == PromptType.QA
    assert prompt.metadata.num_chunks == 2
    assert prompt.metadata.estimated_context_length >= len("Some context about X.")
    assert prompt.metadata.template_name == "qa_v1"


# ---------------------------------------------------------------------------
# 2. MCQ prompt generation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mcq_prompt_generation(prompt_builder: PromptBuilder):
    chunks = [
        make_chunk("Context for MCQ.", document_title="Doc MCQ", chunk_index=0),
    ]
    options = make_mcq_options()
    prompt: Prompt = prompt_builder.build_mcq_prompt(
        question="Which option is correct?",
        chunks=chunks,
        options=options,
    )

    assert isinstance(prompt, Prompt)
    assert "Which option is correct?" in prompt.user_prompt
    for opt in options:
        assert opt.text in prompt.user_prompt

    assert prompt.metadata is not None
    assert prompt.metadata.prompt_type == PromptType.MCQ
    assert prompt.metadata.template_name == "mcq_v1"
    assert prompt.metadata.num_chunks == 1


# ---------------------------------------------------------------------------
# 3. Empty context
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_empty_context(prompt_builder: PromptBuilder):
    prompt: Prompt = prompt_builder.build_qa_prompt(
        question="What is X?",
        chunks=[],
    )

    # Prompt should be generated even with no chunks
    assert isinstance(prompt, Prompt)
    assert "What is X?" in prompt.user_prompt
    assert prompt.metadata is not None
    assert prompt.metadata.num_chunks == 0
    assert prompt.metadata.estimated_context_length == 0


# ---------------------------------------------------------------------------
# 4. Duplicate chunks
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_duplicate_chunks_removed(prompt_builder: PromptBuilder):
    c1 = make_chunk(
        "Same text",
        document_id="doc-1",
        page=1,
        section=None,
        score=0.9,
        document_title="Doc 1",
        chunk_index=0,
    )
    # Duplicate in all fields
    c2 = make_chunk(
        "Same text",
        document_id="doc-1",
        page=1,
        section=None,
        score=0.9,
        document_title="Doc 1",
        chunk_index=0,
    )

    prompt: Prompt = prompt_builder.build_qa_prompt(question="Q?", chunks=[c1, c2])

    assert prompt.metadata is not None
    assert prompt.metadata.num_chunks == 1
    # Only one "Same text" occurrence in prompt body
    assert prompt.user_prompt.count("Same text") == 1


# ---------------------------------------------------------------------------
# 5. Multiple documents
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_multiple_documents_metadata(prompt_builder: PromptBuilder):
    chunks = [
        make_chunk(
            "From doc1 page1 intro",
            document_id="doc-1",
            page=1,
            section="Intro",
            score=0.9,
            document_title="Document One",
            chunk_index=0,
        ),
        make_chunk(
            "From doc2 page2 body",
            document_id="doc-2",
            page=2,
            section="Body",
            score=0.8,
            document_title="Document Two",
            chunk_index=1,
        ),
    ]

    prompt: Prompt = prompt_builder.build_qa_prompt(question="Summarize docs", chunks=chunks)

    assert "Document One" in prompt.user_prompt
    assert "Document Two" in prompt.user_prompt
    assert "Page: 1" in prompt.user_prompt
    assert "Page: 2" in prompt.user_prompt
    assert "Section: Intro" in prompt.user_prompt
    assert "Section: Body" in prompt.user_prompt


# ---------------------------------------------------------------------------
# 6. Chunk ordering
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_chunk_ordering_preserved(prompt_builder: PromptBuilder):
    chunks = [
        make_chunk("First chunk", document_id="doc-1", chunk_index=0),
        make_chunk("Second chunk", document_id="doc-1", chunk_index=1),
        make_chunk("Third chunk", document_id="doc-1", chunk_index=2),
    ]

    prompt: Prompt = prompt_builder.build_qa_prompt(question="Order?", chunks=chunks)

    # Ensure order in user_prompt body
    body = prompt.user_prompt
    first_index = body.find("First chunk")
    second_index = body.find("Second chunk")
    third_index = body.find("Third chunk")

    assert first_index != -1
    assert second_index != -1
    assert third_index != -1

    assert first_index < second_index < third_index


# ---------------------------------------------------------------------------
# 7. Metadata fields
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_metadata_fields_present(prompt_builder: PromptBuilder):
    chunks = [
        make_chunk("Metadata test", chunk_index=0),
    ]
    prompt: Prompt = prompt_builder.build_qa_prompt(question="Meta?", chunks=chunks)

    meta = prompt.metadata
    assert meta is not None
    assert isinstance(meta.prompt_type, PromptType)
    assert isinstance(meta.template_name, str)
    assert isinstance(meta.estimated_context_length, int)
    assert isinstance(meta.num_chunks, int)


# ---------------------------------------------------------------------------
# 8. Prompt templates used correctly
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_correct_template_for_qa(prompt_builder: PromptBuilder):
    chunks = [
        make_chunk("QA template", chunk_index=0),
    ]
    prompt: Prompt = prompt_builder.build_qa_prompt(question="Q?", chunks=chunks)

    assert prompt.metadata is not None
    assert prompt.metadata.template_name == "qa_v1"
    # QA-specific instructions should appear
    assert "Provide a concise, well-structured answer" in prompt.user_prompt


@pytest.mark.asyncio
async def test_correct_template_for_mcq(prompt_builder: PromptBuilder):
    chunks = [
        make_chunk("MCQ template", chunk_index=0),
    ]
    options = make_mcq_options()
    prompt: Prompt = prompt_builder.build_mcq_prompt(
        question="Q?",
        chunks=chunks,
        options=options,
    )

    assert prompt.metadata is not None
    assert prompt.metadata.template_name == "mcq_v1"
    # MCQ-specific instructions should appear
    assert "For each option, assess how well it is supported by the context" in prompt.user_prompt


# ---------------------------------------------------------------------------
# 9. Special characters
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_special_characters(prompt_builder: PromptBuilder):
    text = "Unicode ☺, quotes \"'\", markdown **bold**, newlines\nline2\nline3"
    chunks = [
        make_chunk(text, document_title="Doc ✨", chunk_index=0),
    ]
    prompt: Prompt = prompt_builder.build_qa_prompt(question="Special?", chunks=chunks)

    # Ensure special characters are preserved
    assert "Unicode ☺" in prompt.user_prompt
    assert "quotes \"" in prompt.user_prompt
    assert "markdown **bold**" in prompt.user_prompt
    assert "line2" in prompt.user_prompt
    assert "line3" in prompt.user_prompt
    assert "Doc ✨" in prompt.user_prompt


# ---------------------------------------------------------------------------
# 10. Very large context
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_very_large_context(prompt_builder: PromptBuilder):
    # Build many chunks
    chunks = []
    for i in range(100):
        chunks.append(
            make_chunk(
                text=f"Chunk {i} " + "x" * 100,
                document_id="doc-1",
                page=i % 5 + 1,
                section=None,
                score=0.5 + (i % 10) * 0.01,
                document_title="Large Doc",
                chunk_index=i,
            )
        )

    prompt: Prompt = prompt_builder.build_qa_prompt(
        question="Large context?",
        chunks=chunks,
    )

    assert isinstance(prompt, Prompt)
    assert prompt.metadata is not None
    assert prompt.metadata.num_chunks == len(chunks)
    # Should still include the question and at least some chunk content
    assert "Large context?" in prompt.user_prompt
    assert "Chunk 0" in prompt.user_prompt
    assert "Chunk 99" in prompt.user_prompt