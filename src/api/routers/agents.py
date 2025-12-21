"""
Agents API Router - Agent management and direct invocation.
"""
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])


# Agent registry with metadata
AGENT_REGISTRY = {
    "zeus": {
        "name": "Zeus",
        "description": "Master orchestrator and query router",
        "domain": "orchestration",
        "capabilities": ["routing", "delegation", "coordination"],
        "pentarchy": False,
    },
    "athena": {
        "name": "Athena",
        "description": "Research and knowledge synthesis",
        "domain": "research",
        "capabilities": ["web_search", "analysis", "synthesis"],
        "pentarchy": True,
    },
    "hephaestus": {
        "name": "Hephaestus",
        "description": "Engineering and code generation",
        "domain": "engineering",
        "capabilities": ["code_generation", "builds", "deployments"],
        "pentarchy": True,
    },
    "hermes": {
        "name": "Hermes",
        "description": "Communication and integration",
        "domain": "communication",
        "capabilities": ["messaging", "notifications", "api_calls"],
        "pentarchy": True,
    },
    "prometheus": {
        "name": "Prometheus",
        "description": "Cost analysis and resource management",
        "domain": "finance",
        "capabilities": ["cost_estimation", "budgeting", "resource_tracking"],
        "pentarchy": True,
    },
    "aegis": {
        "name": "Aegis",
        "description": "Security and compliance",
        "domain": "security",
        "capabilities": ["access_control", "vulnerability_scanning", "compliance"],
        "pentarchy": True,
    },
    "chronos": {
        "name": "Chronos",
        "description": "Scheduling and time management",
        "domain": "scheduling",
        "capabilities": ["calendar", "reminders", "availability"],
        "pentarchy": False,
    },
    "memorix": {
        "name": "Memorix",
        "description": "Memory and knowledge graphs",
        "domain": "memory",
        "capabilities": ["storage", "retrieval", "relationships"],
        "pentarchy": False,
    },
    "iris": {
        "name": "Iris",
        "description": "Visualization and UI rendering",
        "domain": "visualization",
        "capabilities": ["charts", "templates", "rendering"],
        "pentarchy": False,
    },
    "hestia": {
        "name": "Hestia",
        "description": "Personalization and user preferences",
        "domain": "personalization",
        "capabilities": ["preferences", "ui_adaptation", "playlists"],
        "pentarchy": False,
    },
    "morpheus": {
        "name": "Morpheus",
        "description": "Learning and optimization",
        "domain": "optimization",
        "capabilities": ["pattern_analysis", "feedback", "model_routing"],
        "pentarchy": False,
    },
}


# Request/Response Models
class AgentInfo(BaseModel):
    """Agent metadata."""
    id: str
    name: str
    description: str
    domain: str
    capabilities: List[str]
    pentarchy: bool
    status: str = "available"


class AgentQueryRequest(BaseModel):
    """Request to query an agent directly."""
    query: str = Field(..., min_length=1, max_length=16000)
    context: Optional[Dict[str, Any]] = None
    conversation_id: Optional[str] = None


class AgentQueryResponse(BaseModel):
    """Response from agent query."""
    agent: str
    response: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    processing_time_ms: int
    timestamp: datetime


class AgentToolRequest(BaseModel):
    """Request to invoke a specific agent tool."""
    tool_name: str
    parameters: Dict[str, Any]


class AgentToolResponse(BaseModel):
    """Response from tool invocation."""
    agent: str
    tool: str
    result: Any
    success: bool
    error: Optional[str] = None


@router.get("", response_model=List[AgentInfo])
async def list_agents(
    domain: Optional[str] = Query(None, description="Filter by domain"),
    pentarchy_only: bool = Query(
        False, description="Only Pentarchy voting agents"),
):
    """List all available agents."""
    agents = []
    for agent_id, meta in AGENT_REGISTRY.items():
        if domain and meta["domain"] != domain:
            continue
        if pentarchy_only and not meta["pentarchy"]:
            continue

        agents.append(AgentInfo(
            id=agent_id,
            name=meta["name"],
            description=meta["description"],
            domain=meta["domain"],
            capabilities=meta["capabilities"],
            pentarchy=meta["pentarchy"],
        ))

    return agents


@router.get("/{agent_id}", response_model=AgentInfo)
async def get_agent(agent_id: str):
    """Get details about a specific agent."""
    if agent_id not in AGENT_REGISTRY:
        raise HTTPException(
            status_code=404, detail=f"Agent '{agent_id}' not found")

    meta = AGENT_REGISTRY[agent_id]
    return AgentInfo(
        id=agent_id,
        name=meta["name"],
        description=meta["description"],
        domain=meta["domain"],
        capabilities=meta["capabilities"],
        pentarchy=meta["pentarchy"],
    )


@router.post("/{agent_id}/query", response_model=AgentQueryResponse)
async def query_agent(agent_id: str, request: AgentQueryRequest):
    """Send a query directly to a specific agent."""
    import time

    if agent_id not in AGENT_REGISTRY:
        raise HTTPException(
            status_code=404, detail=f"Agent '{agent_id}' not found")

    start_time = time.time()

    try:
        # Try to import and use the actual agent
        agent_module = None
        try:
            if agent_id == "zeus":
                from src.agents.zeus.main import ZeusAgent
                agent_module = ZeusAgent()
            elif agent_id == "athena":
                from src.agents.athena.main import AthenaAgent
                agent_module = AthenaAgent()
            elif agent_id == "hephaestus":
                from src.agents.hephaestus.main import HephaestusAgent
                agent_module = HephaestusAgent()
            elif agent_id == "aegis":
                from src.agents.aegis.main import AegisAgent
                agent_module = AegisAgent()
            elif agent_id == "chronos":
                from src.agents.chronos.main import ChronosAgent
                agent_module = ChronosAgent()
            elif agent_id == "memorix":
                from src.agents.memorix.main import MemorixAgent
                agent_module = MemorixAgent()
            elif agent_id == "iris":
                from src.agents.iris.main import IrisAgent
                agent_module = IrisAgent()
            elif agent_id == "hestia":
                from src.agents.hestia.main import HestiaAgent
                agent_module = HestiaAgent()
            elif agent_id == "morpheus":
                from src.agents.morpheus.main import MorpheusAgent
                agent_module = MorpheusAgent()
        except ImportError as e:
            logger.warning(f"Could not import agent {agent_id}: {e}")

        # If agent has process_query, use it
        if agent_module and hasattr(agent_module, "process_query"):
            response = await agent_module.process_query(
                request.query,
                conversation_id=request.conversation_id or ""
            )
        else:
            # Fallback to LLM with agent persona
            from src.services.llm_service import get_llm_service, Message as LLMMessage
            llm = get_llm_service()

            meta = AGENT_REGISTRY[agent_id]
            system_prompt = f"""You are {meta['name']}, the {meta['description']} agent.
Your domain: {meta['domain']}
Your capabilities: {', '.join(meta['capabilities'])}

Respond helpfully to user queries within your domain of expertise."""

            llm_response = await llm.chat(
                messages=[LLMMessage(role="user", content=request.query)],
                system_prompt=system_prompt,
            )
            response = llm_response.content

        processing_time = int((time.time() - start_time) * 1000)

        return AgentQueryResponse(
            agent=agent_id,
            response=response,
            processing_time_ms=processing_time,
            timestamp=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Agent query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/tools/{tool_name}", response_model=AgentToolResponse)
async def invoke_tool(agent_id: str, tool_name: str, request: AgentToolRequest):
    """Invoke a specific tool on an agent."""
    if agent_id not in AGENT_REGISTRY:
        raise HTTPException(
            status_code=404, detail=f"Agent '{agent_id}' not found")

    # This would invoke the actual MCP tool
    # For now, return a placeholder
    return AgentToolResponse(
        agent=agent_id,
        tool=tool_name,
        result={"status": "mock",
                "message": f"Tool {tool_name} invoked with {request.parameters}"},
        success=True,
    )


@router.get("/{agent_id}/capabilities")
async def get_capabilities(agent_id: str):
    """Get detailed capabilities and tools for an agent."""
    if agent_id not in AGENT_REGISTRY:
        raise HTTPException(
            status_code=404, detail=f"Agent '{agent_id}' not found")

    meta = AGENT_REGISTRY[agent_id]
    return {
        "agent": agent_id,
        "capabilities": meta["capabilities"],
        "tools": [
            {"name": f"{agent_id}_{cap}", "description": f"{cap} capability"}
            for cap in meta["capabilities"]
        ],
    }
