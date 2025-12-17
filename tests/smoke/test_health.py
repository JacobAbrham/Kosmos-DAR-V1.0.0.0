import requests


def test_health(base_url: str, session: requests.Session) -> None:
    resp = session.get(f"{base_url}/health", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "ok"


def test_ready(base_url: str, session: requests.Session) -> None:
    resp = session.get(f"{base_url}/ready", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") in ("ready", "degraded")
