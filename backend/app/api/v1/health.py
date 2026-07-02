from fastapi import APIRouter

from backend.app.services.storage import get_storage_backend

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/ping")
async def ping() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/storage")
async def storage_health() -> dict[str, str]:
    backend = get_storage_backend()
    backend_name = "s3" if backend.__class__.__name__ == "S3Storage" else "local"
    return {"status": "ok", "backend": backend_name}
