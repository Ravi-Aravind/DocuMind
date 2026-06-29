from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional, Sequence
from uuid import UUID

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from backend.app.config import settings


@dataclass
class VectorPayload:
    """Metadata payload stored for each document chunk."""

    owner_id: str
    collection_id: Optional[str]
    document_id: str
    document_title: Optional[str]
    chunk_index: int
    page: int
    section: Optional[str]
    score: Optional[float]
    text: str
    created_at: str  # ISO 8601 string


QDRANT_URL = settings.qdrant_url
QDRANT_API_KEY: Optional[str] = settings.qdrant_api_key
QDRANT_COLLECTION_NAME: str = settings.qdrant_collection_name


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


_client: Optional[QdrantClient] = None


def get_qdrant_client() -> QdrantClient:
    """Return a shared Qdrant client instance."""
    global _client
    if _client is None:
        _client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY or None,
        )
    return _client


def ensure_collection(
    collection_name: str,
    vector_size: int,
    distance: qmodels.Distance = qmodels.Distance.COSINE,
) -> None:
    """Ensure the Qdrant collection exists with the correct configuration."""
    client = get_qdrant_client()

    if client.collection_exists(collection_name):
        return

    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=qmodels.VectorParams(
            size=vector_size,
            distance=distance,
        ),
    )


def _build_payloads(
    owner_id: UUID,
    collection_id: Optional[UUID],
    document_id: UUID,
    document_title: Optional[str],
    texts: Sequence[str],
    pages: Sequence[int],
    sections: Sequence[Optional[str]],
    scores: Optional[Sequence[float]] = None,
) -> List[dict]:
    """Construct Qdrant payloads with rich metadata."""
    payloads: List[dict] = []
    for idx, (text, page, section) in enumerate(zip(texts, pages, sections)):
        score_val: Optional[float] = None
        if scores is not None and idx < len(scores):
            score_val = scores[idx]
        payload = {
            "owner_id": str(owner_id),
            "collection_id": str(collection_id) if collection_id is not None else None,
            "document_id": str(document_id),
            "document_title": document_title,
            "chunk_index": idx,
            "page": page,
            "section": section,
            "score": score_val,
            "text": text,
            "created_at": _now_iso(),
        }
        payloads.append(payload)
    return payloads


def upsert_document_chunks(
    collection_name: str,
    owner_id: UUID,
    collection_id: Optional[UUID],
    document_id: UUID,
    document_title: Optional[str],
    texts: Iterable[str],
    vectors: List[List[float]],
    pages: Iterable[int],
    sections: Iterable[Optional[str]],
    scores: Optional[Sequence[float]] = None,
) -> int:
    """Upsert chunks of a document into Qdrant, returns count of inserted points."""
    client = get_qdrant_client()

    texts_list = list(texts)
    pages_list = list(pages)
    sections_list = list(sections)

    payloads = _build_payloads(
        owner_id=owner_id,
        collection_id=collection_id,
        document_id=document_id,
        document_title=document_title,
        texts=texts_list,
        pages=pages_list,
        sections=sections_list,
        scores=scores,
    )

    ids: List[str] = []
    for idx in range(len(texts_list)):
        ids.append(f"{document_id}-{idx}")

    client.upsert(
        collection_name=collection_name,
        points=qmodels.Batch(
            ids=ids,
            vectors=vectors,
            payloads=payloads,
        ),
    )

    return len(ids)


def delete_document_vectors(
    collection_name: str,
    document_id: UUID,
) -> None:
    """Delete all vectors associated with a document. Idempotent."""
    client = get_qdrant_client()
    try:
        client.delete(
            collection_name=collection_name,
            points_selector=qmodels.FilterSelector(
                filter=qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="document_id",
                            match=qmodels.MatchValue(value=str(document_id)),
                        )
                    ]
                )
            ),
        )
    except Exception:
        # Swallow errors to keep deletion idempotent.
        pass


def update_document_collection(
    collection_name: str,
    document_id: UUID,
    new_collection_id: Optional[UUID],
) -> None:
    """Update collection_id payload for all vectors of a document."""
    client = get_qdrant_client()
    try:
        client.set_payload(
            collection_name=collection_name,
            payload={"collection_id": str(new_collection_id) if new_collection_id else None},
            points_selector=qmodels.FilterSelector(
                filter=qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="document_id",
                            match=qmodels.MatchValue(value=str(document_id)),
                        )
                    ]
                )
            ),
        )
    except Exception:
        # If payload update fails, fallback behaviour can be added later.
        pass