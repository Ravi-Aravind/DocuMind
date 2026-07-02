import os

from arq import Worker

from backend.app.services.ingestion import run_sync_ingestion_pipeline
from backend.app.config import settings


async def startup(ctx):
    print("Ingestion worker started")


async def shutdown(ctx):
    print("Ingestion worker stopped")


async def ingest_job(ctx, document_id: str):
    await run_sync_ingestion_pipeline(document_id)


class WorkerSettings:
    functions = [ingest_job]
    on_startup = startup
    on_shutdown = shutdown
    cron_jobs = []
    max_tries = 3


async def main():
    worker = Worker(
        functions=[ingest_job],
        redis_settings=settings.redis_url,
        on_startup=startup,
        on_shutdown=shutdown,
        max_tries=3,
    )
    await worker.async_run()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
