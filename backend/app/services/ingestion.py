from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.config import settings
from backend.app.db.models.document import Document
from backend.app.rag.parsers.base import ParsedDocument
from backend.app.rag.parsers.pdf import PDFParser
from backend.app.rag.parsers.docx_parser import DOCXParser
from backend.app.rag.parsers.txt_parser import TXTParser
from backend.app.rag.parsers.markdown_parser import MarkdownParser
from backend.app.rag.pipeline.chunker import chunk_document
from backend.app.rag.embeddings import embed_texts, get_embedding_model
from backend.app.rag.qdrant_client import (
    ensure_collection,
    upsert_document_chunks,
)
from backend.app.services.document_service import UPLOAD_ROOT


def _load_document_file(doc: Document) -> Path:
    """Locate the uploaded file path for a given document."""
    user_dir = UPLOAD_ROOT / str(doc.owner_id)
    doc_dir = user_dir / str(doc.id)

    if not doc_dir.exists():
        raise FileNotFoundError(f"Document directory not found: {doc_dir}")

    files = list(doc_dir.iterdir())
    if not files:
        raise FileNotFoundError(f"No files found for document: {doc.id}")
    return files[0]


async def _parse_file(path: Path, content_type: Optional[str]) -> ParsedDocument:
    """Dispatch to the correct parser based on content type / extension."""
    ext = path.suffix.lower()
    mime = content_type or ""

    if ext == ".pdf" or mime == "application/pdf":
        parser = PDFParser()
        return await parser.parse(path)
    if ext == ".docx" or mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        parser = DOCXParser()
        return await parser.parse(path)
    if ext in {".txt"} or mime == "text/plain":
        parser = TXTParser()
        return await parser.parse(path)
    if ext in {".md", ".markdown"} or mime == "text/markdown":
        parser = MarkdownParser()
        return await parser.parse(path)

    raise ValueError(f"Unsupported document type: {ext} ({mime})")


async def ingest_document(db: AsyncSession, document_id) -> None:
    """Full ingestion pipeline for a document.

    Steps:
    - Load document record
    - Set status=processing
    - Parse file
    - Chunk
    - Embed
    - Ensure Qdrant collection
    - Upsert chunks into Qdrant with rich metadata
    - Update document status / metadata
    """
    stmt = select(Document).where(Document.id == document_id)
    result = await db.execute(stmt)
    doc: Optional[Document] = result.scalar_one_or_none()
    if doc is None:
        return

    doc.status = "processing"
    doc.error_message = None
    await db.commit()
    await db.refresh(doc)

    try:
        file_path = _load_document_file(doc)
        parsed = await _parse_file(file_path, doc.content_type)

        chunks = chunk_document(parsed)
        if not chunks:
            raise ValueError("Parsed document produced no chunks")

        texts: List[str] = [c.text for c in chunks]
        pages: List[int] = [c.page for c in chunks]
        sections: List[Optional[str]] = [c.section for c in chunks]

        model = get_embedding_model()
        dim = model.get_sentence_embedding_dimension()

        collection_name = settings.qdrant_collection_name

        ensure_collection(collection_name=collection_name, vector_size=dim)

        vectors = embed_texts(texts)

        count = upsert_document_chunks(
            collection_name=collection_name,
            owner_id=doc.owner_id,
            collection_id=doc.collection_id,
            document_id=doc.id,
            document_title=doc.title,
            texts=texts,
            vectors=vectors,
            pages=pages,
            sections=sections,
            scores=None,
        )

        doc.status = "ready"
        doc.vector_collection = collection_name
        doc.vector_count = count
        doc.extra_metadata = (doc.extra_metadata or {}) | {
            "chunk_count": count,
        }
        await db.commit()
        await db.refresh(doc)

    except Exception as exc:
        doc.status = "failed"
        doc.error_message = str(exc)
        await db.commit()
        await db.refresh(doc)