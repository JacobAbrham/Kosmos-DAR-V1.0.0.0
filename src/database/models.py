"""
SQLAlchemy ORM models for KOSMOS database.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import Column, String, Boolean, Integer, Float, Text, ForeignKey, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    conversations: Mapped[List["Conversation"]
                          ] = relationship(back_populates="user")

    @classmethod
    async def get_or_create(cls, user_id: uuid.UUID, email: str, username: str) -> "User":
        """Get existing user or create new one."""
        from .connection import get_database
        db = await get_database()

        # Try to get
        result = await db.fetch_one("SELECT * FROM users WHERE id = $1", user_id)
        if result:
            return cls(**result)

        # Create
        result = await db.fetch_one(
            """
            INSERT INTO users (id, email, username)
            VALUES ($1, $2, $3)
            ON CONFLICT (id) DO UPDATE SET updated_at = CURRENT_TIMESTAMP
            RETURNING *
            """,
            user_id, email, username
        )
        return cls(**result)


class Conversation(Base):
    """Conversation model for chat sessions."""

    __tablename__ = "conversations"
    __table_args__ = {"schema": "agents"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"))
    tenant_id: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata_: Mapped[Dict[str, Any]] = mapped_column(
        "metadata", JSON, default=dict)

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan")

    @classmethod
    async def create(cls, conversation_id: str, user_id: str, tenant_id: str, **kwargs) -> "Conversation":
        """Create a new conversation."""
        from .connection import get_database
        import json
        db = await get_database()

        result = await db.fetch_one(
            """
            INSERT INTO agents.conversations (conversation_id, user_id, tenant_id, metadata)
            VALUES ($1, $2, $3, $4)
            RETURNING id, conversation_id, user_id, tenant_id, created_at
            """,
            conversation_id,
            uuid.UUID(user_id) if user_id else None,
            tenant_id,
            json.dumps(kwargs.get("metadata", {}))
        )

        conv = cls()
        conv.id = result["id"]
        conv.conversation_id = result["conversation_id"]
        conv.user_id = result["user_id"]
        conv.tenant_id = tenant_id
        conv.created_at = result["created_at"]
        return conv

    @classmethod
    async def get(cls, conversation_id: str) -> Optional["Conversation"]:
        """Get conversation by ID."""
        from .connection import get_database
        db = await get_database()

        result = await db.fetch_one(
            "SELECT * FROM agents.conversations WHERE conversation_id = $1",
            conversation_id
        )

        if not result:
            return None

        conv = cls()
        for key, value in result.items():
            if hasattr(conv, key):
                setattr(conv, key, value)
        return conv

    async def delete(self):
        """Delete this conversation."""
        from .connection import get_database
        db = await get_database()
        await db.execute(
            "DELETE FROM agents.conversations WHERE id = $1",
            self.id
        )


class Message(Base):
    """Message model for conversation history."""

    __tablename__ = "messages"
    __table_args__ = {"schema": "agents"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[str] = mapped_column(
        String(100), ForeignKey("agents.conversations.conversation_id"))
    role: Mapped[str] = mapped_column(
        String(50), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    agent_name: Mapped[Optional[str]] = mapped_column(String(100))
    token_count: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)
    metadata_: Mapped[Dict[str, Any]] = mapped_column(
        "metadata", JSON, default=dict)

    # Relationships
    conversation: Mapped["Conversation"] = relationship(
        back_populates="messages")

    @classmethod
    async def create(cls, conversation_id: str, role: str, content: str, agent_name: str = None, **kwargs) -> "Message":
        """Create a new message."""
        from .connection import get_database
        import json
        db = await get_database()

        result = await db.fetch_one(
            """
            INSERT INTO agents.messages (conversation_id, role, content, agent_name, metadata)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, conversation_id, role, content, agent_name, created_at
            """,
            conversation_id, role, content, agent_name, json.dumps(kwargs.get(
                "metadata", {}))
        )

        msg = cls()
        msg.id = result["id"]
        msg.conversation_id = result["conversation_id"]
        msg.role = result["role"]
        msg.content = result["content"]
        msg.agent_name = result["agent_name"]
        msg.created_at = result["created_at"]
        return msg

    async def delete(self):
        """Delete this message."""
        from .connection import get_database
        db = await get_database()
        await db.execute("DELETE FROM agents.messages WHERE id = $1", self.id)


class AgentState(Base):
    """Agent state persistence model."""

    __tablename__ = "agent_states"
    __table_args__ = {"schema": "agents"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    conversation_id: Mapped[str] = mapped_column(String(100), nullable=False)
    state_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    async def create(cls, agent_name: str, conversation_id: str, state_data: Dict = None) -> "AgentState":
        """Create agent state."""
        from .connection import get_database
        db = await get_database()

        result = await db.fetch_one(
            """
            INSERT INTO agents.agent_states (agent_name, conversation_id, state_data)
            VALUES ($1, $2, $3)
            RETURNING id, agent_name, conversation_id, state_data, created_at
            """,
            agent_name, conversation_id, state_data or {}
        )

        state = cls()
        state.id = result["id"]
        state.agent_name = result["agent_name"]
        state.conversation_id = result["conversation_id"]
        state.state_data = result["state_data"]
        state.created_at = result["created_at"]
        return state


class PentarchyVote(Base):
    """Pentarchy voting record model."""

    __tablename__ = "pentarchy_votes"
    __table_args__ = {"schema": "agents"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proposal_id: Mapped[str] = mapped_column(String(100), nullable=False)
    cost: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(Text)
    # APPROVED, REJECTED, HUMAN_REVIEW
    outcome: Mapped[str] = mapped_column(String(50), nullable=False)
    votes: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    reasoning: Mapped[List[str]] = mapped_column(JSON, default=list)
    initiated_by: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    @classmethod
    async def create(cls, proposal_id: str, cost: float, description: str,
                     outcome: str, votes: Dict, reasoning: List[str]) -> "PentarchyVote":
        """Create a voting record."""
        from .connection import get_database
        db = await get_database()

        result = await db.fetch_one(
            """
            INSERT INTO agents.pentarchy_votes (proposal_id, cost, description, outcome, votes, reasoning)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id, proposal_id, cost, outcome, created_at
            """,
            proposal_id, cost, description, outcome, votes, reasoning
        )

        vote = cls()
        vote.id = result["id"]
        vote.proposal_id = result["proposal_id"]
        vote.cost = result["cost"]
        vote.outcome = result["outcome"]
        vote.created_at = result["created_at"]
        return vote
