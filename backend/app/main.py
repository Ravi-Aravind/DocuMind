import json
import logging
import uuid
from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pyrate_limiter import Duration, Limiter, Rate, RedisBucket
from redis import asyncio as aioredis

from backend.app.api.v1.router import api_router
from backend.app.config import settings
from backend.app.core.exceptions import (
    AppException,
    http_exception_handler,
    request_validation_exception_handler,
    unhandled_exception_handler,
)

REQUEST_ID_CONTEXT: ContextVar[str | None] = ContextVar("request_id", default=None)


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        request_id = REQUEST_ID_CONTEXT.get()
        if request_id:
            payload["request_id"] = request_id

        for key, value in record.__dict__.items():
            if key in {"name", "msg", "args", "levelname", "levelno", "pathname", "filename", "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName", "created", "msecs", "relativeCreated", "thread", "threadName", "processName", "process", "message", "asctime"}:
                continue
            payload[key] = value

        return json.dumps(payload)


def configure_logging() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)


async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    token = REQUEST_ID_CONTEXT.set(request_id)
    request.state.request_id = request_id
    try:
        response = await call_next(request)
    except Exception as exc:
        handler = request.app.exception_handlers.get(type(exc)) or request.app.exception_handlers.get(Exception)
        if handler is None:
            raise
        response = await handler(request, exc)
    finally:
        REQUEST_ID_CONTEXT.reset(token)

    response.headers["X-Request-ID"] = request_id
    return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize redis and pyrate-limiter buckets.

    Older code passed bucket_class/bucket_kwargs to Limiter
    which is not supported in the installed pyrate_limiter package.
    Instead we create RedisBucket instances (awaiting their async
    initializer when necessary) and pass the concrete bucket to
    Limiter (which accepts an AbstractBucket).
    """
    redis = aioredis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    app.state.redis = redis

    # Prepare rate definitions
    qa_rates = [Rate(settings.qa_rate_limit_requests, Duration.SECOND * settings.qa_rate_limit_window_seconds)]
    upload_rates = [Rate(settings.upload_rate_limit_requests, Duration.SECOND * settings.upload_rate_limit_window_seconds)]

    # Initialize RedisBucket instances (init may return a coroutine)
    qa_bucket = RedisBucket.init(qa_rates, redis, "qa-rate-limit")
    if hasattr(qa_bucket, "__await__"):
        qa_bucket = await qa_bucket

    upload_bucket = RedisBucket.init(upload_rates, redis, "upload-rate-limit")
    if hasattr(upload_bucket, "__await__"):
        upload_bucket = await upload_bucket

    # Create Limiter objects from concrete buckets
    app.state.rate_limiters = {
        "qa": Limiter(qa_bucket),
        "upload": Limiter(upload_bucket),
    }

    try:
        yield
    finally:
        await redis.close()


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    app.middleware("http")(request_id_middleware)

    app.add_exception_handler(AppException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API routes
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
