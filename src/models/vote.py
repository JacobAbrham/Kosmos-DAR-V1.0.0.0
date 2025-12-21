"""
Vote model for Pentarchy governance decisions.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, Text, JSON, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from src.models.base import Base


class VoteStatus(str, enum.Enum):
    """Status of a Pentarchy proposal."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"


class Proposal(Base):
    """Pentarchy governance proposal."""
    __tablename__ = "proposals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    proposal_id: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, index=True)

    # Proposal details
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Status and result
    status: Mapped[str] = mapped_column(
        String(20), default=VoteStatus.PENDING.value, nullable=False, index=True)
    final_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    threshold_used: Mapped[Optional[float]
                           ] = mapped_column(Float, nullable=True)

    # Initiator
    initiated_by_agent: Mapped[Optional[str]
                               ] = mapped_column(String(50), nullable=True)
    initiated_by_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True)

    # Context
    context: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False)
    resolved_at: Mapped[Optional[datetime]
                        ] = mapped_column(DateTime, nullable=True)

    # Relationships
    votes: Mapped[List["Vote"]] = relationship(
        "Vote", back_populates="proposal", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Proposal {self.proposal_id} ({self.status})>"


class Vote(Base):
    """Individual agent vote on a proposal."""
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    proposal_id: Mapped[int] = mapped_column(
        ForeignKey("proposals.id"), nullable=False, index=True)

    # Vote details
    agent_name: Mapped[str] = mapped_column(String(50), nullable=False)
    vote: Mapped[str] = mapped_column(
        String(10), nullable=False)  # APPROVE, REJECT, ABSTAIN
    score: Mapped[float] = mapped_column(Float, nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    # Reasoning
    reasoning: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True)  # List of reasons

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    proposal: Mapped["Proposal"] = relationship(
        "Proposal", back_populates="votes")

    def __repr__(self) -> str:
        return f"<Vote {self.agent_name}: {self.vote} ({self.score})>"
