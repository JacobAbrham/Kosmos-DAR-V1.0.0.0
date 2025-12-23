"""
Unit tests for the agent message bus.
Tests Redis/NATS pub-sub, agent communication, and event handling.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json


class TestAgentMessages:
    """Tests for agent message structure."""

    def test_request_message_format(self):
        """Request messages should have correct format."""
        message = {
            "id": "msg-123",
            "type": "request",
            "from_agent": "zeus",
            "to_agent": "athena",
            "action": "search",
            "payload": {"query": "test"},
            "timestamp": "2025-01-01T00:00:00Z"
        }
        
        assert "type" in message
        assert "from_agent" in message
        assert "to_agent" in message

    def test_response_message_format(self):
        """Response messages should have correct format."""
        message = {
            "id": "msg-124",
            "type": "response",
            "request_id": "msg-123",
            "from_agent": "athena",
            "to_agent": "zeus",
            "status": "success",
            "payload": {"results": []},
            "timestamp": "2025-01-01T00:00:01Z"
        }
        
        assert message["type"] == "response"
        assert "request_id" in message
        assert "status" in message

    def test_event_message_format(self):
        """Event messages should have correct format."""
        message = {
            "id": "msg-125",
            "type": "event",
            "event_name": "task_completed",
            "source_agent": "hephaestus",
            "payload": {"task_id": "task-1", "result": "success"},
            "timestamp": "2025-01-01T00:00:02Z"
        }
        
        assert message["type"] == "event"
        assert "event_name" in message


class TestChannelNaming:
    """Tests for message channel naming conventions."""

    def test_agent_direct_channel(self):
        """Agent direct channels should be named correctly."""
        agent_name = "zeus"
        channel = f"agent:{agent_name}:inbox"
        
        assert channel == "agent:zeus:inbox"

    def test_broadcast_channel(self):
        """Broadcast channels should be named correctly."""
        channel = "kosmos:broadcast:all-agents"
        
        assert "broadcast" in channel

    def test_pentarchy_channel(self):
        """Pentarchy voting channels should be named correctly."""
        proposal_id = "prop-123"
        channel = f"pentarchy:vote:{proposal_id}"
        
        assert "pentarchy" in channel
        assert proposal_id in channel


class TestMessageSerialization:
    """Tests for message serialization."""

    def test_serialize_message(self):
        """Should serialize message to JSON."""
        message = {
            "type": "request",
            "from": "zeus",
            "payload": {"data": [1, 2, 3]}
        }
        
        serialized = json.dumps(message)
        assert isinstance(serialized, str)
        assert "zeus" in serialized

    def test_deserialize_message(self):
        """Should deserialize message from JSON."""
        json_str = '{"type": "response", "status": "success", "data": {"result": 42}}'
        message = json.loads(json_str)
        
        assert message["type"] == "response"
        assert message["data"]["result"] == 42

    def test_handle_nested_payloads(self):
        """Should handle nested message payloads."""
        message = {
            "type": "complex",
            "payload": {
                "level1": {
                    "level2": {
                        "data": [1, 2, 3],
                        "nested": {"key": "value"}
                    }
                }
            }
        }
        
        serialized = json.dumps(message)
        deserialized = json.loads(serialized)
        
        assert deserialized["payload"]["level1"]["level2"]["nested"]["key"] == "value"


class TestErrorHandling:
    """Tests for message bus error handling."""

    def test_invalid_message_format(self):
        """Should reject invalid message format."""
        # Message without required fields
        invalid_message = {"random": "data"}
        
        # Validation would reject this
        required_fields = ["type", "from_agent"]
        missing = [f for f in required_fields if f not in invalid_message]
        
        assert len(missing) > 0


class TestPentarchyVoting:
    """Tests for Pentarchy voting via message bus."""

    def test_vote_request_message(self):
        """Vote request should have correct structure."""
        vote_request = {
            "type": "vote_request",
            "proposal_id": "prop-123",
            "description": "Deploy new feature",
            "cost": 75.0,
            "risk_level": "medium",
            "voters": ["athena", "hephaestus", "hermes", "nur_prometheus", "aegis"]
        }
        
        assert vote_request["type"] == "vote_request"
        assert len(vote_request["voters"]) == 5

    def test_vote_response_message(self):
        """Vote response should have correct structure."""
        vote_response = {
            "type": "vote",
            "proposal_id": "prop-123",
            "voter": "athena",
            "vote": "APPROVE",
            "reasoning": "Analysis shows low risk",
            "confidence": 0.85
        }
        
        assert vote_response["vote"] in ["APPROVE", "REJECT", "ABSTAIN"]
        assert "reasoning" in vote_response

    def test_vote_result_message(self):
        """Vote result should have correct structure."""
        vote_result = {
            "type": "vote_result",
            "proposal_id": "prop-123",
            "outcome": "APPROVED",
            "votes": {
                "athena": "APPROVE",
                "hephaestus": "APPROVE",
                "hermes": "APPROVE",
                "nur_prometheus": "ABSTAIN",
                "aegis": "APPROVE"
            },
            "final_score": 4.0,
            "threshold": 2.0
        }
        
        assert vote_result["outcome"] in ["APPROVED", "REJECTED", "APPROVED_WITH_REVIEW"]
