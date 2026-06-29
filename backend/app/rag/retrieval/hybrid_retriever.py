from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from qdrant_client.http import models as qmodels

from backend.app.config import settings
from backend.app.rag.retrieval.base import BaseRetriever, RetrievedChunk
from backend.app.rag.embeddings import embed_texts


class HybridRetriever(BaseRetriever):
    """Hybrid retriever that queries Qdrant with metadata-aware filters."""

    def __init__(self) -> None:
        from backend.app.rag.qdrant_client import get_qdrant_client  # avoid circular import

        self.client = get_qdrant_client()
        self.collection_name = settings.qdrant_collection_name

    async def retrieve(
        self,
        *,
        query: str,
        user_id: UUID | None = None,
        collection_id: UUID | None = None,
        document_ids: List[UUID] | None = None,
        top_k: int = 5,
    ) -> List[RetrievedChunk]:
        if not query.strip():
            return []

        if user_id is None:
            # We require user_id to enforce ownership.
            return []

        # Build filter
        must_conditions: List[qmodels.Condition] = [
            qmodels.FieldCondition(
                key="owner_id",
                match=qmodels.MatchValue(value=str(user_id)),
            )
        ]

        if collection_id is not None:
            must_conditions.append(
                qmodels.FieldCondition(
                    key="collection_id",
                    match=qmodels.MatchValue(value=str(collection_id)),
                )
            )

        if document_ids:
            # Restrict to specific documents owned by user
            must_conditions.append(
                qmodels.FieldCondition(
                    key="document_id",
                    match=qmodels.MatchAny(
                        any=[str(did) for did in document_ids],
                    ),
                )
            )

        query_filter = qmodels.Filter(must=must_conditions)

        # Embed query
        vectors = embed_texts([query])
        query_vector = vectors[0]

        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
        )

        chunks: List[RetrievedChunk] = []
        for point in search_result:
            payload = point.payload or {}
            text = payload.get("text", "")
            if not text:
                continue

            chunks.append(
                RetrievedChunk(
                    text=text,
                    page=int(payload.get("page", 0) or 0),
                    section=payload.get("section"),
                    score=float(point.score or 0.0),
                    document_id=str(payload.get("document_id")),
                    document_title=payload.get("document_title"),
                    chunk_index=int(payload.get("chunk_index", 0) or 0),
                )
            )

        # Logging: retrieval latency is handled upstream (SearchService),
        # but we can log basic filter usage here if needed.
        return chunks