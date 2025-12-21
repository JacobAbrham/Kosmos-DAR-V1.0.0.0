"""
Conversation and message models for chat history persistence.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, Text, JSON, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Conversation(Base):
    """Chat conversation session."""
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Extra data
    agent_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True)
    model_used: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Conversation {self.conversation_id}>"


class Message(Base):
    """Individual message in a conversation."""
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(
        String(20), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Token tracking
    input_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True)

    # Extra data
    model_used: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True)
    agent_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message {self.id} ({self.role})>"
