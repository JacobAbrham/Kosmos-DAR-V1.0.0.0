from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import logging
import sys
import os

# Add project root to path to ensure imports work
sys.path.append(os.getcwd())

from src.agents.zeus.main import ZeusAgent, ZeusInput, UserContext
from src.api.models import ChatRequest, ChatResponse, VoteRequest, VoteResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kosmos-api")

# Global Zeus instance
zeus_agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global zeus_agent
    logger.info("Initializing Zeus Agent...")
    zeus_agent = ZeusAgent()
    yield
    # Shutdown
    logger.info("Shutting down Zeus Agent...")
    if zeus_agent:
        await zeus_agent.shutdown()

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
        
        # Call process_message
        result = await zeus_agent.process_message(zeus_input)
        
        # Map ZeusOutput to ChatResponse
        # Since they share structure, we can try returning result directly or converting
        return result
    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
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
