"""
User model for authentication and authorization.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from src.models.base import Base


class UserRole(str, enum.Enum):
    """User roles for RBAC."""
    ADMIN = "admin"
    OPERATOR = "operator"
    USER = "user"
    AGENT = "agent"
    READONLY = "readonly"


class User(Base):
    """User account for authentication."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False)

    # Profile information
    full_name: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at: Mapped[Optional[datetime]
                          ] = mapped_column(DateTime, nullable=True)

    # Relationships
    api_keys: Mapped[List["APIKey"]] = relationship(
        "APIKey", back_populates="user", cascade="all, delete-orphan")
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.email})>"


class APIKey(Base):
    """API key for programmatic access."""
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_hash: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True)
    key_prefix: Mapped[str] = mapped_column(
        String(12), nullable=False)  # First 8 chars for identification
    scopes: Mapped[str] = mapped_column(
        Text, nullable=False, default="read")  # Comma-separated scopes

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True)
    last_used_at: Mapped[Optional[datetime]
                         ] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="api_keys")

    def __repr__(self) -> str:
        return f"<APIKey {self.key_prefix}... ({self.name})>"
