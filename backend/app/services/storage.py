from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol

import boto3
from botocore.config import Config as BotoConfig

from backend.app.config import settings


class StorageBackend(Protocol):
    async def save(self, file_name: str, contents: bytes, metadata: dict | None = None) -> str:
        ...

    async def get_bytes(self, key: str) -> bytes:
        ...

    async def get_url(self, key: str) -> str:
        ...

    async def delete(self, key: str) -> None:
        ...


class LocalDiskStorage:
    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root or settings.storage_local_root)
        self.root.mkdir(parents=True, exist_ok=True)

    async def save(self, file_name: str, contents: bytes, metadata: dict | None = None) -> str:
        key = f"{metadata.get('user_id', 'unknown')}/{metadata.get('document_id', 'unknown')}/{file_name}" if metadata else file_name
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(contents)
        return key

    async def get_bytes(self, key: str) -> bytes:
        path = self.root / key
        return path.read_bytes()

    async def get_url(self, key: str) -> str:
        return str(self.root / key)

    async def delete(self, key: str) -> None:
        path = self.root / key
        if path.exists():
            path.unlink()


class S3Storage:
    def __init__(self) -> None:
        self.bucket = settings.storage_s3_bucket
        self.endpoint = settings.storage_s3_endpoint
        self.region = settings.storage_s3_region
        self.public_url = settings.storage_s3_public_url or self.endpoint
        self.client = boto3.client(
            "s3",
            endpoint_url=self.endpoint or None,
            aws_access_key_id=settings.storage_s3_access_key_id or None,
            aws_secret_access_key=settings.storage_s3_secret_access_key or None,
            region_name=self.region or None,
            config=BotoConfig(s3={"addressing_style": "path"}),
        )

    async def save(self, file_name: str, contents: bytes, metadata: dict | None = None) -> str:
        key = f"{metadata.get('user_id', 'unknown')}/{metadata.get('document_id', 'unknown')}/{file_name}" if metadata else file_name
        self.client.put_object(Bucket=self.bucket, Key=key, Body=contents)
        return key

    async def get_bytes(self, key: str) -> bytes:
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()

    async def get_url(self, key: str) -> str:
        if self.public_url:
            return f"{self.public_url.rstrip('/')}/{self.bucket}/{key}"
        return key

    async def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)


def get_storage_backend() -> StorageBackend:
    if settings.storage_backend.lower() == "s3" and settings.storage_s3_bucket:
        return S3Storage()
    return LocalDiskStorage()
