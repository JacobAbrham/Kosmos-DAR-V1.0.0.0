"""
Integration tests for database layer.

Tests PostgreSQL connections, query patterns, connection pooling,
and data persistence across agents.
"""

import pytest
import sys
import os

sys.path.append(os.getcwd())


@pytest.mark.asyncio
async def test_database_connection():
    """Test database connection can be established."""
    from src.database.connection import get_database
    
    db = await get_database()
    assert db is not None
    
    # Test simple query
    result = await db.fetch_one("SELECT 1 as test")
    assert result["test"] == 1


@pytest.mark.asyncio
async def test_conversation_persistence():
    """Test conversation history can be saved and retrieved."""
    from src.database.models import Conversation
    
    # Create test conversation
    conversation = await Conversation.create(
        conversation_id="db-test-001",
        user_id="test-user",
        tenant_id="test-tenant"
    )
    
    assert conversation.conversation_id == "db-test-001"
    
    # Retrieve it
    retrieved = await Conversation.get(conversation_id="db-test-001")
    assert retrieved.user_id == "test-user"
    
    # Cleanup
    await conversation.delete()


@pytest.mark.asyncio
async def test_message_storage():
    """Test messages can be stored in database."""
    from src.database.models import Message, Conversation
    
    # Create conversation first
    conversation = await Conversation.create(
        conversation_id="msg-test-001",
        user_id="test-user",
        tenant_id="test-tenant"
    )
    
    # Store message
    message = await Message.create(
        conversation_id="msg-test-001",
        role="user",
        content="Test message",
        agent_name="zeus"
    )
    
    assert message.content == "Test message"
    
    # Cleanup
    await message.delete()
    await conversation.delete()


@pytest.mark.asyncio
async def test_connection_pool():
    """Test database connection pooling works correctly."""
    from src.database.connection import get_database
    
    # Get multiple connections
    db1 = await get_database()
    db2 = await get_database()
    db3 = await get_database()
    
    # All should work
    result1 = await db1.fetch_one("SELECT 1 as test")
    result2 = await db2.fetch_one("SELECT 2 as test")
    result3 = await db3.fetch_one("SELECT 3 as test")
    
    assert result1["test"] == 1
    assert result2["test"] == 2
    assert result3["test"] == 3


@pytest.mark.asyncio
async def test_transaction_rollback():
    """Test database transactions can be rolled back."""
    from src.database.connection import get_database
    from src.database.models import Conversation
    
    db = await get_database()
    
    async with db.transaction() as tx:
        # Create conversation in transaction
        conversation = await Conversation.create(
            conversation_id="rollback-test-001",
            user_id="test-user",
            tenant_id="test-tenant"
        )
        
        # Rollback
        await tx.rollback()
    
    # Should not exist after rollback
    retrieved = await Conversation.get(conversation_id="rollback-test-001")
    assert retrieved is None


@pytest.mark.asyncio
async def test_concurrent_writes():
    """Test concurrent database writes are handled correctly."""
    import asyncio
    from src.database.models import Message, Conversation
    
    # Create conversation
    conversation = await Conversation.create(
        conversation_id="concurrent-test-001",
        user_id="test-user",
        tenant_id="test-tenant"
    )
    
    # Create multiple concurrent writes
    tasks = [
        Message.create(
            conversation_id="concurrent-test-001",
            role="user",
            content=f"Message {i}",
            agent_name="zeus"
        )
        for i in range(10)
    ]
    
    messages = await asyncio.gather(*tasks)
    
    # All should succeed
    assert len(messages) == 10
    
    # Cleanup
    for msg in messages:
        await msg.delete()
    await conversation.delete()


@pytest.mark.asyncio
async def test_query_performance():
    """Test database queries complete in reasonable time."""
    import time
    from src.database.connection import get_database
    
    db = await get_database()
    
    start = time.time()
    result = await db.fetch_all("SELECT * FROM conversations LIMIT 100")
    elapsed = time.time() - start
    
    # Should complete in under 1 second
    assert elapsed < 1.0


@pytest.mark.asyncio
async def test_agent_state_persistence():
    """Test agent state can be persisted to database."""
    from src.database.models import AgentState
    
    # Save agent state
    state = await AgentState.create(
        agent_name="zeus",
        state_data={
            "active_conversations": 5,
            "tasks_delegated": 12,
            "uptime_seconds": 3600
        }
    )
    
    assert state.agent_name == "zeus"
    assert state.state_data["active_conversations"] == 5
    
    # Cleanup
    await state.delete()


@pytest.mark.asyncio
async def test_pentarchy_vote_storage():
    """Test Pentarchy votes are stored in database."""
    from src.database.models import PentarchyVote
    
    vote = await PentarchyVote.create(
        proposal_id="vote-db-test-001",
        agent_name="zeus",
        vote_value=1,  # Approve
        reasoning="Test vote storage"
    )
    
    assert vote.vote_value == 1
    
    # Retrieve all votes for proposal
    votes = await PentarchyVote.get_by_proposal("vote-db-test-001")
    assert len(votes) >= 1
    
    # Cleanup
    await vote.delete()


@pytest.mark.asyncio
async def test_database_schema_migrations():
    """Test database schema is up to date."""
    from src.database.connection import get_database
    
    db = await get_database()
    
    # Check required tables exist
    tables = await db.fetch_all("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    
    table_names = [t["table_name"] for t in tables]
    
    # Verify core tables
    assert "conversations" in table_names
    assert "messages" in table_names
    assert "pentarchy_votes" in table_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
