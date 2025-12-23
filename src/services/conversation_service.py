"""Conversation persistence service backed by PostgreSQL."""

import hashlib
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.database import get_database
from src.database.models import Conversation, Message, User

logger = logging.getLogger("conversation-service")


class ConversationService:
    """Service for persisting conversations to the database."""

    def __init__(self) -> None:
        self._db = None

    async def _get_db(self):
        if self._db is None:
            self._db = await get_database()
        return self._db

    @staticmethod
    def _normalize_user_id(user_id: str) -> str:
        """Ensure we have a UUID string; deterministically hash if needed."""
        try:
            uuid_obj = uuid.UUID(user_id)
            return str(uuid_obj)
        except Exception:
            digest = hashlib.md5(user_id.encode("utf-8")).hexdigest()
            return str(uuid.UUID(digest))

    async def get_or_create_conversation(
        self,
        conversation_id: str,
        user_id: str,
    ) -> Conversation:
        """Get existing conversation or create new one for the user."""
        db = await self._get_db()
        normalized_user_id = self._normalize_user_id(user_id)

        existing = await Conversation.get(conversation_id)
        if existing:
            if existing.user_id and str(existing.user_id) != normalized_user_id:
                raise PermissionError("Conversation owned by a different user")
            return existing

        # Ensure user record exists
        await User.get_or_create(
            user_id=uuid.UUID(normalized_user_id),
            email=f"{user_id}@example.com",
            username=user_id,
        )

        conversation = await Conversation.create(
            conversation_id=conversation_id,
            user_id=normalized_user_id,
            tenant_id="default",
            metadata={},
        )
        logger.info("Created new conversation %s for user %s",
                    conversation_id, normalized_user_id)
        return conversation

    async def get_conversation(
        self,
        conversation_id: str,
        user_id: str,
    ) -> Optional[Conversation]:
        """Fetch a conversation if the user owns it."""
        normalized_user_id = self._normalize_user_id(user_id)
        conversation = await Conversation.get(conversation_id)
        if conversation is None:
            return None
        if conversation.user_id and str(conversation.user_id) != normalized_user_id:
            raise PermissionError("Conversation owned by a different user")
        return conversation

    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Delete a conversation the user owns."""
        conversation = await self.get_conversation(conversation_id, user_id)
        if conversation is None:
            return False
        await conversation.delete()
        return True

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """Add a message to a conversation."""
        message = await Message.create(
            conversation_id=conversation_id,
            role=role,
            content=content,
            agent_name=agent_name,
            metadata=metadata or {},
        )

        try:
            db = await self._get_db()
            await db.execute(
                "UPDATE agents.conversations SET updated_at = NOW() WHERE conversation_id = $1",
                conversation_id,
            )
        except Exception as exc:
            logger.debug("Failed to bump conversation updated_at: %s", exc)

        logger.debug("Added %s message to %s", role, conversation_id)
        return message

    async def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 50,
    ) -> List[Message]:
        """Get conversation history ordered by creation."""
        try:
            db = await self._get_db()
            rows = await db.fetch_all(
                """
                SELECT *
                FROM agents.messages
                WHERE conversation_id = $1
                ORDER BY created_at ASC
                LIMIT $2
                """,
                conversation_id,
                limit,
            )
            messages: List[Message] = []
            for row in rows:
                msg = Message()
                for key, value in row.items():
                    if hasattr(msg, key):
                        setattr(msg, key, value)
                messages.append(msg)
            return messages
        except Exception as exc:
            logger.error("Failed to get history: %s", exc)
            return []

    async def get_recent_conversations(
        self,
        user_id: str,
        limit: int = 20,
    ) -> List[Conversation]:
        """Get recent conversations for a user."""
        try:
            normalized_user_id = self._normalize_user_id(user_id)
            db = await self._get_db()
            rows = await db.fetch_all(
                """
                SELECT *
                FROM agents.conversations
                WHERE user_id = $1
                ORDER BY updated_at DESC NULLS LAST, created_at DESC
                LIMIT $2
                """,
                uuid.UUID(normalized_user_id),
                limit,
            )
            conversations: List[Conversation] = []
            for row in rows:
                conv = Conversation()
                for key, value in row.items():
                    if hasattr(conv, key):
                        setattr(conv, key, value)
                conversations.append(conv)
            return conversations
        except Exception as exc:
            logger.error("Failed to get conversations: %s", exc)
            return []

    async def update_conversation_title(
        self,
        conversation_id: str,
        user_id: str,
        title: str,
    ) -> bool:
        """Update conversation title if owned by user."""
        conversation = await self.get_conversation(conversation_id, user_id)
        if conversation is None:
            return False
        try:
            db = await self._get_db()
            await db.execute(
                "UPDATE agents.conversations SET title = $1 WHERE conversation_id = $2",
                title,
                conversation_id,
            )
            conversation.title = title
            return True
        except Exception as exc:
            logger.error("Failed to update title: %s", exc)
            return False


# Global instance
_conversation_service: Optional[ConversationService] = None


def get_conversation_service() -> ConversationService:
    """Get or create conversation service singleton."""
    global _conversation_service
    if _conversation_service is None:
        _conversation_service = ConversationService()
    return _conversation_service
