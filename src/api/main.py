from src.database import get_database
from src.services.conversation_service import get_conversation_service
from src.api.models import ChatRequest, ChatResponse, VoteRequest, VoteResponse
from src.agents.zeus.main import ZeusAgent, ZeusInput, UserContext
from fastapi import FastAPI, HTTPException, Depends
from typing import Optional
from src.api.auth_deps import get_optional_user
from contextlib import asynccontextmanager
import logging
import sys
import os

# Add project root to path to ensure imports work
sys.path.append(os.getcwd())


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kosmos-api")

# Global instances
zeus_agent = None
conversation_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global zeus_agent, conversation_service
    logger.info("Initializing Zeus Agent...")
    zeus_agent = ZeusAgent()

    # Initialize database connection
    try:
        db = await get_database()
        conversation_service = get_conversation_service()
        logger.info("Database connected")
    except Exception as e:
        logger.warning(f"Database connection failed (will use in-memory): {e}")
        conversation_service = None

    yield

    # Shutdown
    logger.info("Shutting down...")
    if zeus_agent:
        await zeus_agent.shutdown()
    try:
        db = get_database()
        await db.disconnect()
    except:
        pass

app = FastAPI(title="KOSMOS API", version="1.0.0", lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent_status": "active" if zeus_agent else "inactive"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not zeus_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        # Construct ZeusInput
        # Mock UserContext for now
        user_context = UserContext(
            user_id=request.user_id,
            tenant_id="default-tenant",
            roles=["user"],
            preferences={}
        )

        zeus_input = ZeusInput(
            user_message=request.message,
            conversation_id=request.conversation_id,
            user_context=user_context
        )

        # Persist user message if conversation_service available
        if conversation_service:
            try:
                conv = await conversation_service.get_or_create_conversation(
                    conversation_id=request.conversation_id,
                    user_id=request.user_id
                )
                await conversation_service.add_message(
                    conversation_id=conv.conversation_id,
                    role="user",
                    content=request.message
                )
            except Exception as db_err:
                logger.warning(f"Failed to persist user message: {db_err}")

        # Call process_message
        result = await zeus_agent.process_message(zeus_input)

        # Persist assistant response if conversation_service available
        if conversation_service and result:
            try:
                await conversation_service.add_message(
                    conversation_id=conv.conversation_id,
                    role="assistant",
                    content=result.response,
                    metadata={"agents_used": result.agents_used,
                              "confidence": result.confidence}
                )
            except Exception as db_err:
                logger.warning(
                    f"Failed to persist assistant message: {db_err}")

        # Map ZeusOutput to ChatResponse
        # Since they share structure, we can try returning result directly or converting
        return result
    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/chat/conversations")
async def list_conversations(
    limit: int = 20,
    offset: int = 0,
    user: Optional[dict] = Depends(get_optional_user)
):
    """List conversations for the current user."""
    if not conversation_service:
        raise HTTPException(status_code=503, detail="Database not initialized")

    user_id = user.get("sub") if user else "user"  # Default to "user" for dev

    try:
        conversations = await conversation_service.get_recent_conversations(
            user_id=user_id,
            limit=limit
        )
        
        # Convert to response format
        return [
            {
                "conversation_id": c.conversation_id,
                "title": c.title,
                "message_count": len(c.messages) if c.messages else 0,
                "created_at": c.created_at,
                "updated_at": c.updated_at
            }
            for c in conversations
        ]
    except Exception as e:
        logger.error(f"Failed to list conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversations/{conversation_id}/history")
async def get_conversation_history(conversation_id: str, limit: int = 50):
    """Retrieve conversation history."""
    if not conversation_service:
        raise HTTPException(status_code=503, detail="Database not initialized")

    try:
        messages = await conversation_service.get_conversation_history(
            conversation_id=conversation_id,
            limit=limit
        )
        return {"conversation_id": conversation_id, "messages": messages}
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vote", response_model=VoteResponse)
async def trigger_vote(request: VoteRequest):
    if not zeus_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        result = await zeus_agent.conduct_pentarchy_vote(
            request.proposal_id,
            request.cost,
            request.description
        )
        return result
    except Exception as e:
        logger.error(f"Vote failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
