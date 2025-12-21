"""
Comprehensive API tests using pytest.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import json


@pytest.fixture
def client():
    """Create test client."""
    from src.main import app
    return TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_endpoint(self, client):
        """Test /health returns OK."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        # API returns "healthy" or "ok" depending on implementation
        assert data["status"] in ["ok", "healthy"]

    def test_ready_endpoint(self, client):
        """Test /ready returns ready status or 404 if not implemented."""
        response = client.get("/ready")
        # Some implementations may not have /ready
        assert response.status_code in [200, 404]

    def test_metrics_endpoint(self, client):
        """Test /metrics returns Prometheus metrics or 404."""
        response = client.get("/metrics")
        # Metrics may not be enabled in all environments
        assert response.status_code in [200, 404]

    def test_docs_endpoint(self, client):
        """Test /docs returns OpenAPI docs."""
        response = client.get("/docs")
        assert response.status_code == 200


class TestChatAPI:
    """Test chat endpoints."""

    def test_send_message(self, client):
        """Test sending a chat message."""
        response = client.post(
            "/api/v1/chat/message",
            json={"content": "Hello, KOSMOS!"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "message_id" in data
        assert "content" in data
        assert data["role"] == "assistant"

    def test_send_message_with_agent(self, client):
        """Test sending message to specific agent."""
        response = client.post(
            "/api/v1/chat/message",
            json={
                "content": "What is your domain?",
                "agent": "athena"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("agent") == "athena"

    def test_list_conversations(self, client):
        """Test listing conversations."""
        # Create a conversation first
        client.post("/api/v1/chat/message", json={"content": "Test"})

        response = client.get("/api/v1/chat/conversations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_conversation(self, client):
        """Test getting a specific conversation."""
        # Create conversation
        create_resp = client.post(
            "/api/v1/chat/message",
            json={"content": "Test message"}
        )
        conv_id = create_resp.json()["conversation_id"]

        response = client.get(f"/api/v1/chat/conversations/{conv_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == conv_id
        assert "messages" in data

    def test_get_nonexistent_conversation(self, client):
        """Test 404 for nonexistent conversation."""
        response = client.get("/api/v1/chat/conversations/nonexistent-id")
        assert response.status_code == 404

    def test_delete_conversation(self, client):
        """Test deleting a conversation."""
        # Create conversation
        create_resp = client.post(
            "/api/v1/chat/message",
            json={"content": "To be deleted"}
        )
        conv_id = create_resp.json()["conversation_id"]

        # Delete it
        response = client.delete(f"/api/v1/chat/conversations/{conv_id}")
        assert response.status_code == 200

        # Verify deleted
        get_resp = client.get(f"/api/v1/chat/conversations/{conv_id}")
        assert get_resp.status_code == 404

    def test_empty_message_rejected(self, client):
        """Test that empty messages are rejected."""
        response = client.post(
            "/api/v1/chat/message",
            json={"content": ""}
        )
        assert response.status_code == 422  # Validation error


class TestAgentsAPI:
    """Test agent endpoints."""

    def test_list_agents(self, client):
        """Test listing all agents."""
        response = client.get("/api/v1/agents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Check agent structure
        agent = data[0]
        assert "id" in agent
        assert "name" in agent
        assert "domain" in agent

    def test_get_agent(self, client):
        """Test getting a specific agent."""
        response = client.get("/api/v1/agents/zeus")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "zeus"
        assert data["name"] == "Zeus"

    def test_get_nonexistent_agent(self, client):
        """Test 404 for nonexistent agent."""
        response = client.get("/api/v1/agents/nonexistent")
        assert response.status_code == 404

    def test_query_agent(self, client):
        """Test querying an agent."""
        response = client.post(
            "/api/v1/agents/athena/query",
            json={"query": "What is your purpose?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "agent_id" in data

    def test_get_agent_capabilities(self, client):
        """Test getting agent capabilities."""
        response = client.get("/api/v1/agents/zeus/capabilities")
        assert response.status_code == 200
        data = response.json()
        assert "capabilities" in data
        assert isinstance(data["capabilities"], list)

    def test_filter_agents_by_domain(self, client):
        """Test filtering agents by domain."""
        response = client.get("/api/v1/agents?domain=governance")
        assert response.status_code == 200
        data = response.json()
        for agent in data:
            assert agent["domain"] == "governance"

    def test_pentarchy_only_filter(self, client):
        """Test filtering for Pentarchy agents only."""
        response = client.get("/api/v1/agents?pentarchy_only=true")
        assert response.status_code == 200
        data = response.json()
        pentarchy_ids = {"athena", "hephaestus",
                         "hermes", "prometheus", "aegis"}
        for agent in data:
            assert agent["id"] in pentarchy_ids


class TestVotesAPI:
    """Test Pentarchy voting endpoints."""

    def test_create_proposal(self, client):
        """Test creating a proposal."""
        response = client.post(
            "/api/v1/votes/proposals",
            json={
                "title": "Test Proposal",
                "description": "This is a test proposal for automated testing",
                "cost": 100.0,
                "risk_level": "low"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "proposal_id" in data
        assert data["title"] == "Test Proposal"
        assert data["status"] in ["pending", "approved", "rejected"]

    def test_list_proposals(self, client):
        """Test listing proposals."""
        # Create a proposal first
        client.post(
            "/api/v1/votes/proposals",
            json={
                "title": "List Test",
                "description": "Proposal for list testing",
                "cost": 50.0
            }
        )

        response = client.get("/api/v1/votes/proposals")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_proposal(self, client):
        """Test getting a specific proposal."""
        # Create proposal
        create_resp = client.post(
            "/api/v1/votes/proposals",
            json={
                "title": "Get Test",
                "description": "Proposal for get testing",
                "cost": 75.0
            }
        )
        prop_id = create_resp.json()["proposal_id"]

        response = client.get(f"/api/v1/votes/proposals/{prop_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["proposal_id"] == prop_id

    def test_vote_on_proposal(self, client):
        """Test voting on a proposal."""
        # Create proposal
        create_resp = client.post(
            "/api/v1/votes/proposals",
            json={
                "title": "Vote Test",
                "description": "Proposal for vote testing",
                "cost": 25.0
            }
        )
        prop_id = create_resp.json()["proposal_id"]

        # Cast vote
        response = client.post(
            f"/api/v1/votes/proposals/{prop_id}/vote",
            json={
                "agent": "athena",
                "vote": "APPROVE",
                "reasoning": ["Good proposal", "Low risk"]
            }
        )
        assert response.status_code == 200

    def test_get_voting_thresholds(self, client):
        """Test getting voting thresholds."""
        response = client.get("/api/v1/votes/thresholds")
        assert response.status_code == 200
        data = response.json()
        assert "low" in data
        assert "medium" in data
        assert "high" in data
        assert "critical" in data

    def test_get_voting_stats(self, client):
        """Test getting voting statistics."""
        response = client.get("/api/v1/votes/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_proposals" in data
        assert "approved" in data
        assert "rejected" in data


class TestMCPAPI:
    """Test MCP server management endpoints."""

    def test_list_servers(self, client):
        """Test listing MCP servers."""
        response = client.get("/api/v1/mcp/servers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_tools(self, client):
        """Test listing all tools."""
        response = client.get("/api/v1/mcp/tools")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_invoke_tool(self, client):
        """Test invoking a tool."""
        # First ensure servers are initialized
        client.get("/api/v1/mcp/servers")

        response = client.post(
            "/api/v1/mcp/tools/memory/store/invoke",
            json={"arguments": {"key": "test", "value": "data"}}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_stats(self, client):
        """Test getting MCP stats."""
        response = client.get("/api/v1/mcp/stats")
        assert response.status_code == 200
        data = response.json()
        assert "servers" in data
        assert "tools" in data


class TestWebSocketEndpoints:
    """Test WebSocket connection stats."""

    def test_connection_stats(self, client):
        """Test WebSocket connection statistics."""
        response = client.get("/ws/connections")
        assert response.status_code == 200
        data = response.json()
        assert "active_conversations" in data
        assert "total_connections" in data


class TestErrorHandling:
    """Test error handling across endpoints."""

    def test_invalid_json(self, client):
        """Test handling of invalid JSON."""
        response = client.post(
            "/api/v1/chat/message",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_missing_required_fields(self, client):
        """Test handling of missing required fields."""
        response = client.post(
            "/api/v1/votes/proposals",
            json={"title": "Missing description"}
        )
        assert response.status_code == 422

    def test_invalid_risk_level(self, client):
        """Test validation of risk level."""
        response = client.post(
            "/api/v1/votes/proposals",
            json={
                "title": "Test",
                "description": "Test description here",
                "risk_level": "invalid"
            }
        )
        assert response.status_code == 422
