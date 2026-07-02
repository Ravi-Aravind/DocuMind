from fastapi.testclient import TestClient

from backend.app.main import app


def test_storage_health_endpoint() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/health/storage")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["backend"] in {"local", "s3"}
