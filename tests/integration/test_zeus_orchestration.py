"""
Integration tests for Zeus orchestration and agent delegation.

Tests Zeus's ability to route tasks, delegate to specialist agents,
and manage conversation context.
"""

import pytest
import sys
import os

sys.path.append(os.getcwd())

from src.agents.zeus.main import ZeusAgent, ZeusInput, UserContext


@pytest.mark.asyncio
async def test_zeus_initialization():
    """Test Zeus agent initializes successfully."""
    zeus = ZeusAgent()
    
    try:
        assert zeus.name == "zeus"
        assert zeus.version == "2.0.0"
    finally:
        await zeus.shutdown()


@pytest.mark.asyncio
async def test_zeus_process_simple_message():
    """Test Zeus processes a simple chat message."""
    zeus = ZeusAgent()
    
    try:
        input_data = ZeusInput(
            user_message="Hello Zeus, what can you help me with?",
            conversation_id="test-001",
            user_context=UserContext(
                user_id="test-user",
                tenant_id="test-tenant",
                roles=["user"],
                preferences={}
            )
        )
        
        result = await zeus.process_message(input_data)
        
        assert result.response is not None
        assert len(result.response) > 0
        assert "Zeus" in result.agents_used
        
    finally:
        await zeus.shutdown()


@pytest.mark.asyncio
async def test_zeus_delegates_to_hermes():
    """Test Zeus can delegate email tasks to Hermes."""
    zeus = ZeusAgent()
    
    try:
        result = await zeus.delegate_task(
            agent_name="hermes",
            tool_name="send_email",
            args={
                "to": ["test@example.com"],
                "subject": "Integration Test",
                "body": "This is a test email from Zeus"
            }
        )
        
        # Should return mock success response
        assert result is not None
        assert isinstance(result, dict)
        
    finally:
        await zeus.shutdown()


@pytest.mark.asyncio
async def test_zeus_handles_invalid_agent():
    """Test Zeus handles delegation to non-existent agent."""
    zeus = ZeusAgent()
    
    try:
        result = await zeus.delegate_task(
            agent_name="nonexistent_agent",
            tool_name="some_tool",
            args={}
        )
        
        # Should handle gracefully (return error or None)
        assert result is None or "error" in result
        
    finally:
        await zeus.shutdown()


@pytest.mark.asyncio
async def test_zeus_conversation_context():
    """Test Zeus maintains conversation context."""
    zeus = ZeusAgent()
    
    try:
        user_context = UserContext(
            user_id="test-user",
            tenant_id="test-tenant",
            roles=["user"],
            preferences={}
        )
        
        # First message
        input1 = ZeusInput(
            user_message="My name is Alice",
            conversation_id="context-001",
            user_context=user_context
        )
        result1 = await zeus.process_message(input1)
        
        # Second message referencing context
        input2 = ZeusInput(
            user_message="What is my name?",
            conversation_id="context-001",
            user_context=user_context
        )
        result2 = await zeus.process_message(input2)
        
        # Should maintain context (in Phase 2)
        assert result1.response is not None
        assert result2.response is not None
        
    finally:
        await zeus.shutdown()


@pytest.mark.asyncio
async def test_zeus_multi_turn_conversation():
    """Test Zeus handles multi-turn conversations."""
    zeus = ZeusAgent()
    
    try:
        user_context = UserContext(
            user_id="test-user",
            tenant_id="test-tenant",
            roles=["user"],
            preferences={}
        )
        
        messages = [
            "Hello, I need help with a task",
            "Can you send an email?",
            "Send it to team@example.com",
            "The subject should be 'Team Update'",
            "Thank you!"
        ]
        
        for i, msg in enumerate(messages):
            input_data = ZeusInput(
                user_message=msg,
                conversation_id="multi-turn-001",
                user_context=user_context,
                conversation_history=[]  # Phase 2: populate with history
            )
            
            result = await zeus.process_message(input_data)
            assert result.response is not None
            
    finally:
        await zeus.shutdown()


@pytest.mark.asyncio
async def test_zeus_handles_empty_message():
    """Test Zeus handles empty messages gracefully."""
    zeus = ZeusAgent()
    
    try:
        input_data = ZeusInput(
            user_message="",
            conversation_id="empty-001",
            user_context=UserContext(
                user_id="test-user",
                tenant_id="test-tenant",
                roles=["user"],
                preferences={}
            )
        )
        
        result = await zeus.process_message(input_data)
        
        # Should handle gracefully
        assert result is not None
        
    finally:
        await zeus.shutdown()


@pytest.mark.asyncio
async def test_zeus_delegates_security_check():
    """Test Zeus can delegate to AEGIS for security checks."""
    zeus = ZeusAgent()
    
    try:
        result = await zeus.delegate_task(
            agent_name="aegis",
            tool_name="vulnerability_scan",
            args={
                "target": "test-container:latest"
            }
        )
        
        # Should return mock result
        assert result is not None
        
    finally:
        await zeus.shutdown()


@pytest.mark.asyncio
async def test_zeus_response_metadata():
    """Test Zeus includes proper metadata in responses."""
    zeus = ZeusAgent()
    
    try:
        input_data = ZeusInput(
            user_message="Test message",
            conversation_id="metadata-001",
            user_context=UserContext(
                user_id="test-user",
                tenant_id="test-tenant",
                roles=["user"],
                preferences={}
            )
        )
        
        result = await zeus.process_message(input_data)
        
        # Verify metadata fields
        assert result.agents_used is not None
        assert isinstance(result.agents_used, list)
        assert result.confidence >= 0.0 and result.confidence <= 1.0
        
    finally:
        await zeus.shutdown()


@pytest.mark.asyncio
async def test_zeus_error_recovery():
    """Test Zeus recovers from errors during processing."""
    zeus = ZeusAgent()
    
    try:
        # Simulate error condition
        input_data = ZeusInput(
            user_message="Test with intentional error: " + "x" * 100000,  # Very long message
            conversation_id="error-001",
            user_context=UserContext(
                user_id="test-user",
                tenant_id="test-tenant",
                roles=["user"],
                preferences={}
            )
        )
        
        result = await zeus.process_message(input_data)
        
        # Should handle gracefully, not crash
        assert result is not None
        
    finally:
        await zeus.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
