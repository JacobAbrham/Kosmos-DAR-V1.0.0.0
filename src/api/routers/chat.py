"""
Chat API Router - Conversation management and messaging.
"""
import os
import uuid
import logging
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from src.services.llm_service import get_llm_service, Message as LLMMessage
from src.api.auth_deps import get_optional_user, get_current_user, require_permission
from src.services.auth_service import Permission

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# Check if auth is required
REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "false").lower() == "true"


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


# In-memory storage (replace with DB in production)
_conversations: dict = {}
_messages: dict = {}


@router.post("/message", response_model=MessageResponse)
async def send_message(
    request: MessageRequest,
    background_tasks: BackgroundTasks,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Send a message and get an AI response."""
    # Optionally enforce auth
    if REQUIRE_AUTH and current_user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_id = current_user.get("sub") if current_user else "anonymous"

    # Get or create conversation
    conversation_id = request.conversation_id or str(uuid.uuid4())

    if conversation_id not in _conversations:
        _conversations[conversation_id] = {
            "id": conversation_id,
            "title": None,
            "messages": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

    conv = _conversations[conversation_id]

    # Add user message
    user_msg = {
        "id": str(uuid.uuid4()),
        "role": "user",
        "content": request.content,
        "created_at": datetime.utcnow(),
    }
    conv["messages"].append(user_msg)

    # Get LLM response
    llm = get_llm_service()

    try:
        # Build message history
        messages = [
            LLMMessage(role=m["role"], content=m["content"])
            for m in conv["messages"][-10:]  # Last 10 messages for context
        ]

        # Route to agent if specified
        system_prompt = None
        if request.agent:
            system_prompt = f"You are {request.agent.upper()}, a specialized AI agent in the KOSMOS system."

        response = await llm.chat(
            messages=messages,
            system_prompt=system_prompt,
            model=request.model,
        )

        # Add assistant message
        assistant_msg = {
            "id": str(uuid.uuid4()),
            "role": "assistant",
            "content": response.content,
            "agent": request.agent,
            "model": response.model,
            "tokens": response.usage.get("total_tokens") if response.usage else None,
            "created_at": datetime.utcnow(),
        }
        conv["messages"].append(assistant_msg)
        conv["updated_at"] = datetime.utcnow()

        # Generate title in background if first message
        if len(conv["messages"]) == 2 and not conv["title"]:
            background_tasks.add_task(
                _generate_title, conversation_id, request.content)

        return MessageResponse(
            conversation_id=conversation_id,
            message_id=assistant_msg["id"],
            content=response.content,
            role="assistant",
            agent=request.agent,
            model=response.model,
            tokens_used=assistant_msg.get("tokens"),
            created_at=assistant_msg["created_at"],
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to process message: {str(e)}")


@router.get("/conversations", response_model=List[ConversationSummary])
async def list_conversations(limit: int = 20, offset: int = 0):
    """List all conversations."""
    convs = sorted(
        _conversations.values(),
        key=lambda x: x["updated_at"],
        reverse=True
    )[offset:offset + limit]

    return [
        ConversationSummary(
            conversation_id=c["id"],
            title=c.get("title"),
            message_count=len(c["messages"]),
            created_at=c["created_at"],
            updated_at=c["updated_at"],
        )
        for c in convs
    ]


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(conversation_id: str):
    """Get a specific conversation with all messages."""
    if conversation_id not in _conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv = _conversations[conversation_id]
    return ConversationDetail(
        conversation_id=conv["id"],
        title=conv.get("title"),
        messages=conv["messages"],
        created_at=conv["created_at"],
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    if conversation_id not in _conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    del _conversations[conversation_id]
    return {"status": "deleted", "conversation_id": conversation_id}


@router.post("/conversations/{conversation_id}/title")
async def set_title(conversation_id: str, title: str):
    """Set conversation title."""
    if conversation_id not in _conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    _conversations[conversation_id]["title"] = title
    return {"status": "updated", "title": title}


async def _generate_title(conversation_id: str, first_message: str):
    """Background task to generate conversation title."""
    try:
        llm = get_llm_service()
        response = await llm.chat(
            messages=[LLMMessage(
                role="user",
                content=f"Generate a brief 3-5 word title for a conversation that starts with: {first_message[:200]}"
            )],
            temperature=0.3,
        )
        if conversation_id in _conversations:
            _conversations[conversation_id]["title"] = response.content.strip(
                '"\'')
    except Exception as e:
        logger.warning(f"Failed to generate title: {e}")
