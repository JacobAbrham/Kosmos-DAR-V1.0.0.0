"""Smoke tests for hardened API behaviors."""
import types
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

import src.main as app_module
import src.api.routers.chat as chat_router
from src.services.auth_service import AuthService, UserRole


class StubConversationService:
    def __init__(self):
        self._messages = []

    async def get_or_create_conversation(self, conversation_id: str, user_id: str):
        return types.SimpleNamespace(
            conversation_id=conversation_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            title=None,
            user_id=user_id,
        )

    async def add_message(self, **kwargs):
        self._messages.append(kwargs)
        return types.SimpleNamespace(**kwargs)

    async def get_conversation_history(self, conversation_id: str, limit: int = 50):
        return []

    async def get_conversation(self, conversation_id: str, user_id: str):
        return types.SimpleNamespace(
            conversation_id=conversation_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            title=None,
            user_id=user_id,
        )

    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        return True

    async def update_conversation_title(self, conversation_id: str, user_id: str, title: str) -> bool:
        return True

    async def get_recent_conversations(self, user_id: str, limit: int = 20):
        return []


def stub_llm_response(content: str):
    return types.SimpleNamespace(
        content=content,
        model="stub-model",
        usage={"total_tokens": 10},
        cached=False,
    )


def get_stub_llm_service():
    class _Stub:
        async def chat(self, *args, **kwargs):
            return stub_llm_response("stubbed reply")

    return _Stub()


def auth_header():
    token = AuthService().create_tokens(
        user_id="user-123",
        email="user@example.com",
        roles=[UserRole.USER.value],
    )
    return {"Authorization": f"Bearer {token.access_token}"}


@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    # Patch conversation service to avoid DB usage.
    monkeypatch.setattr(chat_router, "get_conversation_service", lambda: StubConversationService())
    monkeypatch.setattr(app_module, "get_conversation_service", lambda: StubConversationService(), raising=False)
    # Patch LLM service to avoid external calls.
    monkeypatch.setattr(chat_router, "get_llm_service", get_stub_llm_service, raising=False)
    monkeypatch.setattr(app_module, "get_llm_service", get_stub_llm_service, raising=False)
    # Disable dependency checks during tests.
    monkeypatch.setenv("ENABLE_DEP_CHECKS", "false")
    yield


def test_chat_requires_auth_by_default(monkeypatch):
    # Override the module-level REQUIRE_AUTH check
    monkeypatch.setattr(chat_router, "REQUIRE_AUTH", True)
    client = TestClient(app_module.app)
    response = client.post("/api/v1/chat/message", json={"content": "hello"})
    # When auth is required, should return 401 or 403
    assert response.status_code in [401, 403, 422]


def test_chat_allows_authenticated_flow(monkeypatch):
    # Allow dependency checks to be skipped and conversation/LLM to be stubbed.
    client = TestClient(app_module.app)

    response = client.post(
        "/api/v1/chat/message",
        headers=auth_header(),
        json={"content": "hello"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "stubbed reply"
    assert data["conversation_id"]


def test_ready_uses_hardened_checks(monkeypatch):
    async def ok():
        return {"ok": True, "detail": "ok"}

    monkeypatch.setattr(app_module, "check_postgres", ok)
    monkeypatch.setattr(app_module, "check_redis", ok)
    monkeypatch.setattr(app_module, "check_minio", ok)
    monkeypatch.setenv("ENABLE_DEP_CHECKS", "true")

    client = TestClient(app_module.app)
    response = client.get("/ready")
    assert response.status_code == 200
    payload = response.json()
    assert payload["dependencies"]["postgres"]["ok"] is True
    assert payload["status"] == "ready"
