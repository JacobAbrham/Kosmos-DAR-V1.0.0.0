"""
Integration tests for KOSMOS API endpoints.

Tests the FastAPI gateway endpoints including health checks, 
chat interface, and voting functionality.
"""

import pytest
import httpx
from typing import AsyncGenerator

# Test configuration
API_BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0


@pytest.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create an async HTTP client for API testing."""
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=TIMEOUT) as client:
        yield client


@pytest.mark.asyncio
async def test_health_endpoint(client: httpx.AsyncClient):
    """Test the /health endpoint returns healthy status."""
    response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "agent_status" in data


@pytest.mark.asyncio
async def test_chat_endpoint_valid_request(client: httpx.AsyncClient):
    """Test chat endpoint with valid message."""
    payload = {
        "message": "Hello Zeus, what can you do?",
        "conversation_id": "test-conv-001",
        "user_id": "test-user"
    }
    
    response = await client.post("/chat", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "response" in data
    assert "agents_used" in data
    assert "confidence" in data
    assert "metadata" in data
    
    # Verify metadata structure
    assert "trace_id" in data["metadata"]
    assert "processing_time_ms" in data["metadata"]
    assert "token_usage" in data["metadata"]


@pytest.mark.asyncio
async def test_chat_endpoint_empty_message(client: httpx.AsyncClient):
    """Test chat endpoint rejects empty messages."""
    payload = {
        "message": "",
        "conversation_id": "test-conv-002",
        "user_id": "test-user"
    }
    
    response = await client.post("/chat", json=payload)
    
    # Should return validation error
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_chat_endpoint_missing_fields(client: httpx.AsyncClient):
    """Test chat endpoint handles missing required fields."""
    payload = {
        "message": "Test message"
        # Missing conversation_id and user_id
    }
    
    response = await client.post("/chat", json=payload)
    
    # Should still work with defaults or return validation error
    assert response.status_code in [200, 422]


@pytest.mark.asyncio
async def test_vote_endpoint_low_cost(client: httpx.AsyncClient):
    """Test voting endpoint with cost below $50 (auto-approved)."""
    payload = {
        "proposal_id": "test-prop-low-001",
        "cost": 25.00,
        "description": "Low cost test proposal"
    }
    
    response = await client.post("/vote", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert data["proposal_id"] == "test-prop-low-001"
    assert data["outcome"] in ["approved", "auto_approved"]
    assert "votes" in data
    assert isinstance(data["reasoning"], list)


@pytest.mark.asyncio
async def test_vote_endpoint_medium_cost(client: httpx.AsyncClient):
    """Test voting endpoint with cost $50-$100 (requires pentarchy)."""
    payload = {
        "proposal_id": "test-prop-med-001",
        "cost": 75.00,
        "description": "Medium cost test proposal requiring vote"
    }
    
    response = await client.post("/vote", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify pentarchy vote occurred
    assert data["proposal_id"] == "test-prop-med-001"
    assert data["outcome"] in ["approved", "rejected"]
    assert len(data["votes"]) == 5  # All 5 pentarchy members
    assert len(data["reasoning"]) == 5


@pytest.mark.asyncio
async def test_vote_endpoint_high_cost(client: httpx.AsyncClient):
    """Test voting endpoint with cost above $100 (rejected)."""
    payload = {
        "proposal_id": "test-prop-high-001",
        "cost": 150.00,
        "description": "High cost test proposal"
    }
    
    response = await client.post("/vote", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Should be auto-rejected
    assert data["outcome"] == "rejected"


@pytest.mark.asyncio
async def test_vote_endpoint_invalid_cost(client: httpx.AsyncClient):
    """Test voting endpoint with negative cost."""
    payload = {
        "proposal_id": "test-prop-invalid-001",
        "cost": -10.00,
        "description": "Invalid cost proposal"
    }
    
    response = await client.post("/vote", json=payload)
    
    # Should return validation error
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_concurrent_chat_requests(client: httpx.AsyncClient):
    """Test API handles concurrent chat requests."""
    import asyncio
    
    async def send_chat(msg_id: int):
        payload = {
            "message": f"Concurrent test message {msg_id}",
            "conversation_id": f"concurrent-{msg_id}",
            "user_id": "test-user"
        }
        return await client.post("/chat", json=payload)
    
    # Send 5 concurrent requests
    tasks = [send_chat(i) for i in range(5)]
    responses = await asyncio.gather(*tasks)
    
    # All should succeed
    for response in responses:
        assert response.status_code == 200
        data = response.json()
        assert "response" in data


@pytest.mark.asyncio
async def test_api_cors_headers(client: httpx.AsyncClient):
    """Test API returns proper CORS headers."""
    response = await client.options("/chat", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST"
    })
    
    # Should allow CORS from frontend
    assert response.status_code in [200, 204]


@pytest.mark.asyncio
async def test_api_error_handling(client: httpx.AsyncClient):
    """Test API gracefully handles internal errors."""
    # Send malformed JSON
    response = await client.post(
        "/chat",
        content=b"{{invalid json}}",
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code in [400, 422]
    data = response.json()
    assert "detail" in data or "error" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
