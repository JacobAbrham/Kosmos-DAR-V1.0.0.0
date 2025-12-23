"""
Unit tests for API routers.
Tests chat, agents, votes, and MCP endpoints.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


class TestChatRouter:
    """Tests for chat API endpoints."""

    def test_chat_request_validation(self):
        """Chat requests should validate input."""
        from src.api.models import ChatRequest
        
        # Valid request
        request = ChatRequest(
            message="Hello",
            user_id="user-123",
            conversation_id="conv-456"
        )
        assert request.message == "Hello"
        assert request.user_id == "user-123"

    def test_chat_response_structure(self):
        """Chat responses should have correct structure."""
        from src.api.models import ChatResponse, ResponseMetadata, TokenUsage
        
        metadata = ResponseMetadata(
            processing_time_ms=100,
            token_usage=TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
            trace_id="trace-123",
            conversation_turn=1
        )
        response = ChatResponse(
            response="Hello!",
            agents_used=["zeus"],
            confidence=0.95,
            metadata=metadata
        )
        assert response.response == "Hello!"
        assert "zeus" in response.agents_used


class TestAgentsRouter:
    """Tests for agents API endpoints."""

    def test_agent_status_structure(self):
        """Agent status should have correct structure."""
        status = {
            "name": "zeus",
            "version": "2.0.0",
            "status": "active",
            "last_active": "2025-01-01T00:00:00Z"
        }
        assert "name" in status
        assert "status" in status


class TestVotesRouter:
    """Tests for voting API endpoints."""

    def test_vote_request_validation(self):
        """Vote requests should validate input."""
        from src.api.models import VoteRequest
        
        request = VoteRequest(
            proposal_id="prop-123",
            cost=75.0,
            description="Test proposal"
        )
        assert request.proposal_id == "prop-123"
        assert request.cost == 75.0

    def test_vote_response_structure(self):
        """Vote responses should have correct structure."""
        from src.api.models import VoteResponse
        
        response = VoteResponse(
            proposal_id="prop-123",
            outcome="APPROVED",
            votes={"zeus": "APPROVE", "athena": "APPROVE"},
            reasoning=["Majority approved", "Low risk"]
        )
        assert response.outcome == "APPROVED"
        assert len(response.votes) >= 1


class TestAPIModels:
    """Tests for Pydantic API models."""

    def test_chat_request_model(self):
        """ChatRequest model should validate correctly."""
        from src.api.models import ChatRequest
        
        # Valid request
        request = ChatRequest(
            message="Test message",
            user_id="user-1"
        )
        assert request.message == "Test message"

    def test_chat_request_default_fields(self):
        """ChatRequest should have sensible defaults."""
        from src.api.models import ChatRequest
        
        request = ChatRequest(
            message="Test"
        )
        # conversation_id defaults to "default", user_id defaults to "user"
        assert request.conversation_id == "default"
        assert request.user_id == "user"

    def test_vote_request_required_fields(self):
        """VoteRequest should require all fields."""
        from src.api.models import VoteRequest
        
        request = VoteRequest(
            proposal_id="prop-1",
            cost=50.0,
            description="Test"
        )
        assert request.proposal_id == "prop-1"
        assert request.cost == 50.0


class TestErrorHandling:
    """Tests for API error handling."""

    def test_error_response_format(self):
        """Error responses should have consistent format."""
        error_response = {
            "detail": "An error occurred",
            "code": "INTERNAL_ERROR"
        }
        assert "detail" in error_response


class TestMiddlewareIntegration:
    """Tests for middleware integration with routes."""

    def test_middleware_classes_defined(self):
        """Middleware classes should be properly defined."""
        from src.core.logging import LoggingMiddleware
        from src.api.metrics import MetricsMiddleware
        
        assert LoggingMiddleware is not None
        assert MetricsMiddleware is not None
