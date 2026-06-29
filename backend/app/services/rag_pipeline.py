from __future__ import annotations

import logging
import time
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.db.models.document import Document
from backend.app.rag.retrieval.base import RetrievedChunk
from backend.app.rag.retrieval.hybrid_retriever import HybridRetriever
from backend.app.rag.retrieval.bge_reranker import BGEReranker
from backend.app.schemas.qa import (
    MCQOption,
    MCQOptionScore,
    MCQRequest,
    MCQResponse,
    QARequest,
    QAResponse,
    SourceCitation,
    ConfidenceLevel,
)
from backend.app.services.search_service import SearchService
from backend.app.services.openrouter_service import (
    OpenRouterService,
    OpenRouterError,
    OpenRouterTimeoutError,
    OpenRouterAuthenticationError,
    OpenRouterUnavailableError,
    OpenRouterRateLimitError,
    OpenRouterResponseError,
)
from backend.app.prompts import PromptBuilder

logger = logging.getLogger(__name__)

MIN_SUPPORTING_CHUNKS_FOR_HIGH_CONF = 3
MIN_SUPPORTING_CHUNKS_FOR_MEDIUM_CONF = 2

_search_service: Optional[SearchService] = None
_openrouter_service: Optional[OpenRouterService] = None
_prompt_builder: Optional[PromptBuilder] = None


def _get_search_service() -> SearchService:
    global _search_service
    if _search_service is None:
        _search_service = SearchService(
            retriever=HybridRetriever(),
            reranker=BGEReranker(),
        )
    return _search_service


def _get_openrouter_service() -> OpenRouterService:
    global _openrouter_service
    if _openrouter_service is None:
        _openrouter_service = OpenRouterService()
    return _openrouter_service


def _get_prompt_builder() -> PromptBuilder:
    global _prompt_builder
    if _prompt_builder is None:
        _prompt_builder = PromptBuilder()
    return _prompt_builder


async def _load_document_titles(
    db: AsyncSession,
    document_ids: List[UUID],
) -> Dict[str, str]:
    """Load titles for documents referenced in results."""
    unique_ids = list({doc_id for doc_id in document_ids})
    if not unique_ids:
        return {}

    stmt = select(Document).where(Document.id.in_(unique_ids))
    result = await db.execute(stmt)
    docs = result.scalars().all()

    id_to_title: Dict[str, str] = {}
    for d in docs:
        id_to_title[str(d.id)] = d.title
    return id_to_title


def _compute_confidence(chunks: List[RetrievedChunk]) -> ConfidenceLevel:
    if not chunks:
        return "not_found"

    scores = [c.score for c in chunks]
    best = max(scores)
    avg = sum(scores) / len(scores)
    supporting = len(chunks)

    if best >= 0.8 and avg >= 0.7 and supporting >= MIN_SUPPORTING_CHUNKS_FOR_HIGH_CONF:
        return "high"

    if best >= 0.6 and avg >= 0.5 and supporting >= MIN_SUPPORTING_CHUNKS_FOR_MEDIUM_CONF:
        return "medium"

    if best >= 0.4:
        return "low"

    return "not_found"


def _build_citations(chunks: List[RetrievedChunk]) -> List[SourceCitation]:
    sources: List[SourceCitation] = []
    for c in chunks:
        snippet = c.text[:500]
        sources.append(
            SourceCitation(
                document_id=c.document_id,
                document_title=c.document_title,
                page=c.page,
                section=c.section,
                snippet=snippet,
                score=c.score,
            )
        )
    return sources


async def _search_with_metrics(
    search: SearchService,
    query: str,
    user_id: UUID,
    top_k: int,
) -> List[RetrievedChunk]:
    start = time.monotonic()
    reranked = await search.search(query=query, user_id=user_id, top_k=top_k)
    latency = time.monotonic() - start
    logger.info(
        "Search pipeline completed",
        extra={
            "latency_ms": int(latency * 1000),
            "top_k": top_k,
        },
    )
    return reranked


async def run_qa_pipeline(
    db: AsyncSession,
    user_id: str,
    req: QARequest,
) -> QAResponse:
    """Run question-answering pipeline over ingested documents."""
    start_total = time.monotonic()

    search = _get_search_service()
    reranked = await _search_with_metrics(
        search=search,
        query=req.question,
        user_id=UUID(user_id),
        top_k=req.top_k,
    )

    if not reranked:
        logger.info("QA pipeline: no results")
        return QAResponse(
            answer="I could not find relevant information in the documents.",
            confidence="not_found",
            score=0.0,
            sources=[],
        )

    # Load titles for citations
    id_to_title = await _load_document_titles(
        db=db,
        document_ids=[UUID(c.document_id) for c in reranked],
    )
    for c in reranked:
        c.document_title = id_to_title.get(c.document_id)

    confidence = _compute_confidence(reranked)
    best_score = reranked[0].score

    if confidence == "not_found":
        logger.info("QA pipeline: low confidence, treating as not_found")
        total_latency = time.monotonic() - start_total
        logger.info(
            "QA pipeline completed",
            extra={"total_latency_ms": int(total_latency * 1000)},
        )
        return QAResponse(
            answer="I could not find relevant information in the documents.",
            confidence=confidence,
            score=best_score,
            sources=[],
        )

    prompt_builder = _get_prompt_builder()
    prompt = prompt_builder.build_qa_prompt(question=req.question, chunks=reranked)

    # Combine system + user prompt into single message content for OpenRouterService
    openrouter = _get_openrouter_service()
    combined_prompt = f"{prompt.system_prompt}\n\n{prompt.user_prompt}"

    try:
        answer_text = await openrouter.generate(combined_prompt)
    except (
        OpenRouterTimeoutError,
        OpenRouterAuthenticationError,
        OpenRouterUnavailableError,
        OpenRouterRateLimitError,
        OpenRouterResponseError,
        OpenRouterError,
    ):
        logger.error("QA pipeline: OpenRouter failure")
        total_latency = time.monotonic() - start_total
        logger.info(
            "QA pipeline completed with LLM error",
            extra={"total_latency_ms": int(total_latency * 1000)},
        )
        return QAResponse(
            answer="An internal error occurred while generating the answer.",
            confidence="not_found",
            score=best_score,
            sources=[],
        )

    sources = _build_citations(reranked)

    total_latency = time.monotonic() - start_total
    logger.info(
        "QA pipeline completed",
        extra={"total_latency_ms": int(total_latency * 1000)},
    )

    return QAResponse(
        answer=answer_text,
        confidence=confidence,
        score=best_score,
        sources=sources,
    )


async def run_mcq_pipeline(
    db: AsyncSession,
    user_id: str,
    req: MCQRequest,
) -> MCQResponse:
    """Run MCQ scoring pipeline over ingested documents."""
    start_total = time.monotonic()

    search = _get_search_service()
    reranked = await _search_with_metrics(
        search=search,
        query=req.question,
        user_id=UUID(user_id),
        top_k=req.top_k,
    )

    if not reranked:
        logger.info("MCQ pipeline: no results")
        return MCQResponse(
            selected_option_id=None,
            confidence="not_found",
            options=[],
            sources=[],
        )

    id_to_title = await _load_document_titles(
        db=db,
        document_ids=[UUID(c.document_id) for c in reranked],
    )
    for c in reranked:
        c.document_title = id_to_title.get(c.document_id)

    confidence = _compute_confidence(reranked)
    best_score = reranked[0].score

    prompt_builder = _get_prompt_builder()
    prompt = prompt_builder.build_mcq_prompt(
        question=req.question,
        chunks=reranked,
        options=req.options,
    )

    combined_prompt = f"{prompt.system_prompt}\n\n{prompt.user_prompt}"
    openrouter = _get_openrouter_service()

    try:
        llm_output = await openrouter.generate(combined_prompt)
    except (
        OpenRouterTimeoutError,
        OpenRouterAuthenticationError,
        OpenRouterUnavailableError,
        OpenRouterRateLimitError,
        OpenRouterResponseError,
        OpenRouterError,
    ):
        logger.error("MCQ pipeline: OpenRouter failure")
        total_latency = time.monotonic() - start_total
        logger.info(
            "MCQ pipeline completed with LLM error",
            extra={"total_latency_ms": int(total_latency * 1000)},
        )
        return MCQResponse(
            selected_option_id=None,
            confidence="not_found",
            options=[],
            sources=[],
        )

    selected_id: Optional[str] = None
    normalized_output = llm_output.upper()
    for opt in req.options:
        marker_variants = [
            f"ANSWER: {opt.id.upper()}",
            f"{opt.id.upper()}.",
            f"({opt.id.upper()})",
            f"OPTION {opt.id.upper()}",
        ]
        if any(m in normalized_output for m in marker_variants):
            selected_id = opt.id
            break

    option_scores: List[MCQOptionScore] = []
    for opt in req.options:
        option_scores.append(
            MCQOptionScore(
                id=opt.id,
                score=1.0 if opt.id == selected_id else 0.0,
                justification=llm_output[:500],
            )
        )

    sources = _build_citations(reranked)

    total_latency = time.monotonic() - start_total
    logger.info(
        "MCQ pipeline completed",
        extra={"total_latency_ms": int(total_latency * 1000)},
    )

    return MCQResponse(
        selected_option_id=selected_id,
        confidence=confidence,
        options=option_scores,
        sources=sources,
    )