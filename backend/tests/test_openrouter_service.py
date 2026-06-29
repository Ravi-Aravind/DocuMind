import pytest
import httpx
from httpx import Response, Request

from backend.app.services.openrouter_service import (
    OpenRouterService,
    OpenRouterAuthenticationError,
    OpenRouterTimeoutError,
    OpenRouterUnavailableError,
    OpenRouterRateLimitError,
    OpenRouterResponseError,
    OpenRouterError,
)
from backend.app.config import settings


class DummySettings:
    openrouter_api_key = "test-key"
    openrouter_endpoint = "https://example.com/chat/completions"
    openrouter_model = "test-model"
    llm_timeout = 1.0
    llm_temperature = 0.1


def make_service(monkeypatch) -> OpenRouterService:
    # Patch settings used by OpenRouterService
    import backend.app.services.openrouter_service as mod
    mod.settings = DummySettings()
    return OpenRouterService(max_retries=0)


@pytest.mark.asyncio
async def test_generate_success(monkeypatch):
    service = make_service(monkeypatch)

    async def fake_post(self, url, json=None, headers=None):
        assert url == DummySettings.openrouter_endpoint
        return Response(
            status_code=200,
            request=Request("POST", url),
            json={
                "choices": [{"message": {"content": "Hello"}}],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15,
                },
            },
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    content = await service.generate("Test prompt")
    assert content == "Hello"


@pytest.mark.asyncio
async def test_authentication_failure(monkeypatch):
    service = make_service(monkeypatch)

    async def fake_post(self, url, json=None, headers=None):
        return Response(status_code=401, request=Request("POST", url))

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    with pytest.raises(OpenRouterAuthenticationError):
        await service.generate("Test prompt")


@pytest.mark.asyncio
async def test_rate_limit(monkeypatch):
    service = make_service(monkeypatch)

    async def fake_post(self, url, json=None, headers=None):
        return Response(status_code=429, request=Request("POST", url))

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    with pytest.raises(OpenRouterRateLimitError):
        await service.generate("Test prompt")


@pytest.mark.asyncio
async def test_server_error(monkeypatch):
    service = make_service(monkeypatch)

    async def fake_post(self, url, json=None, headers=None):
        return Response(status_code=500, request=Request("POST", url))

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    with pytest.raises(OpenRouterUnavailableError):
        await service.generate("Test prompt")


@pytest.mark.asyncio
async def test_timeout(monkeypatch):
    service = make_service(monkeypatch)

    async def fake_post(self, url, json=None, headers=None):
        raise httpx.TimeoutException("timeout")

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    with pytest.raises(OpenRouterTimeoutError):
        await service.generate("Test prompt")


@pytest.mark.asyncio
async def test_malformed_response(monkeypatch):
    service = make_service(monkeypatch)

    async def fake_post(self, url, json=None, headers=None):
        return Response(status_code=200, request=Request("POST", url), json={})

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    with pytest.raises(OpenRouterResponseError):
        await service.generate("Test prompt")