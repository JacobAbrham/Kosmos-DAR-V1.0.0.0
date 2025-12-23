import os

# Set test defaults before importing app
os.environ.setdefault("REQUIRE_AUTH", "false")
os.environ.setdefault("ENABLE_DEP_CHECKS", "false")

from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"
    assert data.get("service") == "kosmos-api"


def test_ready_endpoint_defaults_skip_dep_checks(monkeypatch):
    # Ensure dependency checks are skipped by default for unit tests
    monkeypatch.setenv("ENABLE_DEP_CHECKS", "false")
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ready"
    deps = data.get("dependencies")
    assert deps
    assert deps.get("checked") is False
