"""Chat API Router - Conversation management and messaging."""
import logging
import os
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field

from src.api.auth_deps import get_current_user, get_optional_user, require_permission
from src.services.auth_service import Permission
from src.services.conversation_service import get_conversation_service
from src.services.llm_service import Message as LLMMessage
from src.services.llm_service import get_llm_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# Check if auth is required (default: enabled)
REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "true").lower() == "true"
UserDependency = get_current_user if REQUIRE_AUTH else get_optional_user


# Request/Response Models
class MessageRequest(BaseModel):
    """Request to send a message."""
    content: str = Field(..., min_length=1, max_length=32000)
    conversation_id: Optional[str] = None
    agent: Optional[str] = Field(
        None, description="Target agent (zeus, athena, etc.)")
    model: Optional[str] = Field(None, description="LLM model override")


class MessageResponse(BaseModel):
    """Response from chat endpoint."""
    conversation_id: str
    message_id: str
    content: str
    role: str = "assistant"
    agent: Optional[str] = None
    model: Optional[str] = None
    tokens_used: Optional[int] = None
    created_at: datetime


class ConversationSummary(BaseModel):
    """Summary of a conversation."""
    conversation_id: str
    title: Optional[str]
    message_count: int
    created_at: datetime
    updated_at: datetime


class ConversationDetail(BaseModel):
    """Full conversation with messages."""
    conversation_id: str
    title: Optional[str]
    messages: List[dict]
    created_at: datetime


chat_write_deps = [Depends(require_permission(Permission.CHAT_WRITE))] if REQUIRE_AUTH else []
chat_read_deps = [Depends(require_permission(Permission.CHAT_READ))] if REQUIRE_AUTH else []


@router.post("/message", response_model=MessageResponse, dependencies=chat_write_deps)
async def send_message(
    request: MessageRequest,
    background_tasks: BackgroundTasks,
    current_user: Optional[dict] = Depends(UserDependency),
):
    """Send a message and get an AI response."""
    if REQUIRE_AUTH and current_user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_id = current_user.get("sub") if current_user else "anonymous"
    conversation_id = request.conversation_id or str(uuid.uuid4())

    conv_service = get_conversation_service()
    try:
        conversation = await conv_service.get_or_create_conversation(
            conversation_id, user_id)
    except PermissionError:
        raise HTTPException(status_code=403, detail="Conversation not owned by user")
    except Exception as exc:  # noqa: BLE001
        logger.error("Conversation storage unavailable: %s", exc)
        raise HTTPException(status_code=503, detail="Conversation storage unavailable")

    # Build context from history (last 10)
    history = await conv_service.get_conversation_history(
        conversation.conversation_id, limit=10)
    messages = [
        LLMMessage(role=m.role, content=m.content)
        for m in history
    ]
    messages.append(LLMMessage(role="user", content=request.content))

    llm = get_llm_service()

    try:
        system_prompt = None
        if request.agent:
            system_prompt = (
                f"You are {request.agent.upper()}, a specialized AI agent in the KOSMOS system."
            )

        response = await llm.chat(
            messages=messages,
            system_prompt=system_prompt,
            model=request.model,
        )

        assistant_msg_id = str(uuid.uuid4())
        created_at = datetime.utcnow()

        # Persist user and assistant messages
        await conv_service.add_message(
            conversation_id=conversation.conversation_id,
            role="user",
            content=request.content,
        )
        await conv_service.add_message(
            conversation_id=conversation.conversation_id,
            role="assistant",
            content=response.content,
            agent_name=request.agent,
            metadata={
                "model": response.model,
                "tokens": response.usage.get("total_tokens") if response.usage else None,
            },
        )

        if len(history) == 0:
            background_tasks.add_task(
                _generate_title, conversation.conversation_id, request.content, user_id)

        return MessageResponse(
            conversation_id=conversation.conversation_id,
            message_id=assistant_msg_id,
            content=response.content,
            role="assistant",
            agent=request.agent,
            model=response.model,
            tokens_used=response.usage.get("total_tokens") if response.usage else None,
            created_at=created_at,
        )

    except Exception as e:  # noqa: BLE001
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to process message: {str(e)}")


@router.get(
    "/conversations",
    response_model=List[ConversationSummary],
    dependencies=chat_read_deps,
)
async def list_conversations(
    limit: int = 20,
    current_user: Optional[dict] = Depends(UserDependency),
):
    """List conversations for the current user."""
    if REQUIRE_AUTH and current_user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_id = current_user.get("sub") if current_user else "anonymous"
    conv_service = get_conversation_service()
    conversations = await conv_service.get_recent_conversations(
        user_id=user_id, limit=limit)

    summaries: List[ConversationSummary] = []
    for conv in conversations:
        messages = await conv_service.get_conversation_history(conv.conversation_id, limit=1_000)
        summaries.append(
            ConversationSummary(
                conversation_id=conv.conversation_id,
                title=getattr(conv, "title", None),
                message_count=len(messages),
                created_at=conv.created_at,
                updated_at=getattr(conv, "updated_at", conv.created_at),
            )
        )

    return summaries


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationDetail,
    dependencies=chat_read_deps,
)
async def get_conversation(conversation_id: str, current_user: Optional[dict] = Depends(UserDependency)):
    """Get a specific conversation with all messages for the user."""
    if REQUIRE_AUTH and current_user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_id = current_user.get("sub") if current_user else "anonymous"
    conv_service = get_conversation_service()

    try:
        conversation = await conv_service.get_conversation(conversation_id, user_id)
    except PermissionError:
        raise HTTPException(status_code=403, detail="Conversation not owned by user")

    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = await conv_service.get_conversation_history(conversation_id, limit=200)
    return ConversationDetail(
        conversation_id=conversation.conversation_id,
        title=getattr(conversation, "title", None),
        messages=[
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "agent": getattr(m, "agent_name", None),
                "created_at": m.created_at,
            }
            for m in messages
        ],
        created_at=conversation.created_at,
    )


@router.delete(
    "/conversations/{conversation_id}",
    dependencies=chat_write_deps,
)
async def delete_conversation(conversation_id: str, current_user: Optional[dict] = Depends(UserDependency)):
    """Delete a conversation owned by the user."""
    if REQUIRE_AUTH and current_user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_id = current_user.get("sub") if current_user else "anonymous"
    conv_service = get_conversation_service()
    try:
        deleted = await conv_service.delete_conversation(conversation_id, user_id)
    except PermissionError:
        raise HTTPException(status_code=403, detail="Conversation not owned by user")

    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"status": "deleted", "conversation_id": conversation_id}


@router.post(
    "/conversations/{conversation_id}/title",
    dependencies=chat_write_deps,
)
async def set_title(conversation_id: str, title: str, current_user: Optional[dict] = Depends(UserDependency)):
    """Set conversation title for a user's conversation."""
    if REQUIRE_AUTH and current_user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_id = current_user.get("sub") if current_user else "anonymous"
    conv_service = get_conversation_service()
    try:
        updated = await conv_service.update_conversation_title(conversation_id, user_id, title)
    except PermissionError:
        raise HTTPException(status_code=403, detail="Conversation not owned by user")

    if not updated:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "updated", "title": title}


async def _generate_title(conversation_id: str, first_message: str, user_id: str):
    """Background task to generate conversation title."""
    try:
        llm = get_llm_service()
        response = await llm.chat(
            messages=[LLMMessage(
                role="user",
                content=(
                    "Generate a brief 3-5 word title for a conversation that starts with: "
                    f"{first_message[:200]}"
                ),
            )],
            temperature=0.3,
        )
        title = response.content.strip('"\'')
        conv_service = get_conversation_service()
        await conv_service.update_conversation_title(conversation_id, user_id, title)
    except Exception as e:  # noqa: BLE001
        logger.warning(f"Failed to generate title: {e}")
