from __future__ import annotations

import mimetypes
import os
import uuid
from pathlib import Path
from typing import Iterable

from backend.app.services.storage import get_storage_backend

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.models import Document, User
from backend.app.rag.qdrant_client import (
    delete_document_vectors,
    update_document_collection,
)
from backend.app.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

UPLOAD_ROOT = Path("uploads")
storage_backend = get_storage_backend()


def _validate_file_extension(filename: str) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file extension")


def _infer_mime_type(filename: str) -> str | None:
    mime, _ = mimetypes.guess_type(filename)
    return mime


async def _validate_file(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise ValueError("Unsupported MIME type")

    file_size = 0
    chunk = await file.read(1024 * 1024)
    while chunk:
        file_size += len(chunk)
        if file_size > MAX_FILE_SIZE_BYTES:
            raise ValueError("File too large")
        chunk = await file.read(1024 * 1024)

    await file.seek(0)


async def create_document(
    db: AsyncSession,
    user: User,
    file: UploadFile,
) -> Document:
    """Create a Document row and store the uploaded file."""
    _validate_file_extension(file.filename)
    await _validate_file(file)

    document_id = uuid.uuid4()

    contents = await file.read()
    key = await storage_backend.save(file_name=file.filename, contents=contents, metadata={"user_id": str(user.id), "document_id": str(document_id)})

    await file.seek(0)

    document = Document(
        id=document_id,
        title=file.filename,
        original_filename=file.filename,
        content_type=file.content_type or _infer_mime_type(file.filename),
        status="uploaded",
        owner_id=user.id,
        extra_metadata={"storage_key": key},
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    return document


async def list_documents(db: AsyncSession, user: User) -> list[Document]:
    result = await db.execute(select(Document).where(Document.owner_id == user.id))
    return list(result.scalars().all())


async def get_document(db: AsyncSession, user: User, document_id: uuid.UUID) -> Document | None:
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.owner_id == user.id)
    )
    return result.scalars().first()


async def delete_document(db: AsyncSession, user: User, document: Document) -> None:
    """Delete a document and its stored files and vectors for the authenticated user."""
    storage_key = None
    if document.extra_metadata:
        storage_key = document.extra_metadata.get("storage_key")
    if storage_key:
        await storage_backend.delete(storage_key)

    # Delete vectors from Qdrant (idempotent)
    if document.vector_collection:
        delete_document_vectors(
            collection_name=document.vector_collection,
            document_id=document.id,
        )

    await db.delete(document)
    await db.commit()


async def move_document_to_collection(
    db: AsyncSession,
    user: User,
    document: Document,
    new_collection_id: uuid.UUID | None,
) -> Document:
    """Move a document to another collection and update Qdrant payload."""
    if document.owner_id != user.id:
        raise ValueError("Document does not belong to current user")

    old_collection = document.collection_id
    document.collection_id = new_collection_id
    await db.commit()
    await db.refresh(document)

    # Update Qdrant payloads for this document
    if document.vector_collection and old_collection != new_collection_id:
        update_document_collection(
            collection_name=document.vector_collection,
            document_id=document.id,
            new_collection_id=new_collection_id,
        )

    return document