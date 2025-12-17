import os
import logging
import asyncio
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from fastmcp import FastMCP

# Import Core Client Logic
from src.core.agent_registry import AGENT_REGISTRY, get_agent_path
from src.core.mcp_client import AgentClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("zeus-agent")

# --- Data Models (from Specification) ---

class UserContext(BaseModel):
    """User context for personalization."""
    user_id: str
    tenant_id: str
    roles: List[str]
    preferences: Dict[str, Any] = {}

class ZeusInput(BaseModel):
    """Input schema for Zeus orchestrator."""
    user_message: str
    conversation_id: str
    user_context: Optional[UserContext] = None
    routing_hints: Optional[List[str]] = None
    priority: str = "normal" # Literal["low", "normal", "high", "critical"] = "normal"

class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ResponseMetadata(BaseModel):
    """Metadata about response generation."""
    processing_time_ms: int
    token_usage: TokenUsage
    trace_id: str
    conversation_turn: int

class ZeusOutput(BaseModel):
    """Output schema for Zeus orchestrator."""
    response: str
    agents_used: List[str]
    confidence: float
    follow_up_suggestions: List[str] = []
    metadata: ResponseMetadata

# --- Agent Implementation ---

class ZeusAgent:
    def __init__(self):
        self.name = "zeus"
        self.version = "2.0.0"
        self.mcp = FastMCP(self.name)
        self.clients: Dict[str, AgentClient] = {}
        logger.info(f"Initializing {self.name} Agent v{self.version}")
        
        # Register tools
        self.mcp.tool()(self.process_message)
        self.mcp.tool()(self.delegate_task)
        self.mcp.tool()(self.list_available_agents)
        self.mcp.tool()(self.conduct_pentarchy_vote)

    async def shutdown(self):
        """Close all agent connections."""
        logger.info("Shutting down Zeus Agent connections...")
        for name, client in self.clients.items():
            try:
                await client.close()
                logger.info(f"Closed connection to {name}")
            except Exception as e:
                logger.error(f"Error closing connection to {name}: {e}")
        self.clients.clear()

    async def get_client(self, agent_name: str) -> AgentClient:
        """Get or create a client connection to an agent."""
        if agent_name not in self.clients:
            if agent_name not in AGENT_REGISTRY:
                raise ValueError(f"Unknown agent: {agent_name}")
            
            path = get_agent_path(agent_name)
            client = AgentClient(agent_name, path)
            await client.connect()
            self.clients[agent_name] = client
        
        return self.clients[agent_name]

    async def list_available_agents(self) -> List[str]:
        """List all registered agents available for delegation."""
        return list(AGENT_REGISTRY.keys())

    async def delegate_task(self, agent_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Delegate a task to another agent via MCP."""
        logger.info(f"Delegating to {agent_name}: {tool_name}")
        try:
            client = await self.get_client(agent_name)
            result = await client.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            logger.error(f"Delegation failed: {e}")
            return {"error": str(e)}

    async def conduct_pentarchy_vote(self, proposal_id: str, cost: float, description: str) -> Dict[str, Any]:
        """Conduct a Pentarchy vote for a proposal."""
        logger.info(f"Conducting Pentarchy vote for {proposal_id} (Cost: ${cost})")
        
        # 1. Check Auto-Approval Thresholds
        if cost < 50.0:
            return {
                "proposal_id": proposal_id,
                "outcome": "APPROVED",
                "votes": {"system": "AUTO_APPROVE"},
                "reasoning": ["Cost below $50 auto-approval threshold"]
            }
        
        if cost > 100.0:
            return {
                "proposal_id": proposal_id,
                "outcome": "HUMAN_REVIEW_REQUIRED",
                "votes": {"system": "ABSTAIN"},
                "reasoning": ["Cost exceeds $100 limit for autonomous approval"]
            }

        # 2. Gather Votes from Pentarchy Members
        voters = ["nur_prometheus", "hephaestus", "athena"]
        votes = {}
        reasons = []
        
        for voter in voters:
            try:
                # In a real system, we would parse the MCP result object.
                # Here we assume the tool returns a dict-like structure or we'd need to parse the JSON string from the content.
                result = await self.delegate_task(
                    voter, 
                    "evaluate_proposal", 
                    {"proposal_id": proposal_id, "cost": cost, "description": description}
                )
                
                # Mock parsing logic for MVP
                # If result is a list (MCP content), we'd extract text.
                # For now, assuming direct return or simple dict for the mock flow.
                votes[voter] = "APPROVE" # Default for mock
                reasons.append(f"{voter} approved (mock)")
                
            except Exception as e:
                logger.error(f"Failed to get vote from {voter}: {e}")
                votes[voter] = "ERROR"

        # 3. Tally Votes
        approve_count = sum(1 for v in votes.values() if v == "APPROVE")
        
        outcome = "REJECTED"
        if approve_count == 3:
            outcome = "APPROVED"
        elif approve_count == 2:
            outcome = "APPROVED_WITH_REVIEW"

        return {
            "proposal_id": proposal_id,
            "outcome": outcome,
            "votes": votes,
            "reasoning": reasons
        }

    async def process_message(self, input_data: ZeusInput) -> ZeusOutput:
        """
        Main entry point for processing a user message.
        """
        start_time = datetime.now()
        logger.info(f"Processing message for conversation: {input_data.conversation_id}")

        # TODO: Implement Intent Classification
        # TODO: Implement Task Decomposition
        # TODO: Implement Agent Routing
        
        # Mock Logic for MVP
        response_text = f"Zeus received: {input_data.user_message}. (Orchestration logic pending)"
        
        processing_time = (datetime.now() - start_time).microseconds // 1000

        return ZeusOutput(
            response=response_text,
            agents_used=["Zeus"],
            confidence=1.0,
            follow_up_suggestions=[],
            metadata=ResponseMetadata(
                processing_time_ms=processing_time,
                token_usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                trace_id="mock-trace-id",
                conversation_turn=1
            )
        )
    
    def run(self):
        """Start the Zeus MCP server."""
        self.mcp.run()

# --- Entry Point ---

if __name__ == "__main__":
    agent = ZeusAgent()
    agent.run()
