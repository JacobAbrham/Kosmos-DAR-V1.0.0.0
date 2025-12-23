"""
Votes API Router - Pentarchy governance and voting.
"""
import os
import uuid
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, Depends
from pydantic import BaseModel, Field

from src.api.auth_deps import get_optional_user, require_permission
from src.services.auth_service import Permission
from src.core.governance import (
    THRESHOLDS, 
    PENTARCHY_AGENTS, 
    RiskLevel, 
    get_risk_level, 
    calculate_vote_outcome
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/votes", tags=["governance"])

# Check if auth is required
REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "false").lower() == "true"


# Request/Response Models
class ProposalRequest(BaseModel):
    """Request to create a proposal for Pentarchy voting."""
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=10, max_length=10000)
    cost: float = Field(0.0, ge=0)
    risk_level: str = Field("medium", pattern="^(low|medium|high|critical)$")
    context: Optional[Dict[str, Any]] = None
    auto_execute: bool = Field(False, description="Auto-execute if approved")


class VoteResult(BaseModel):
    """Individual agent vote."""
    agent: str
    vote: str  # APPROVE, REJECT, ABSTAIN
    score: float
    reasoning: List[str]
    timestamp: datetime


class ProposalResponse(BaseModel):
    """Response with proposal details and voting results."""
    proposal_id: str
    title: str
    description: str
    cost: float
    risk_level: str
    status: str  # pending, approved, rejected, escalated
    votes: List[VoteResult]
    final_score: Optional[float]
    threshold: float
    created_at: datetime
    resolved_at: Optional[datetime]


class ProposalSummary(BaseModel):
    """Summary of a proposal."""
    proposal_id: str
    title: str
    status: str
    final_score: Optional[float]
    vote_count: int
    created_at: datetime


# In-memory storage (replace with DB)
_proposals: Dict[str, dict] = {}


@router.post("/proposals", response_model=ProposalResponse)
async def create_proposal(
    request: ProposalRequest,
    background_tasks: BackgroundTasks,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Create a new proposal and initiate Pentarchy voting."""
    # Optionally enforce auth for proposal creation
    if REQUIRE_AUTH and current_user is None:
        raise HTTPException(
            status_code=401, detail="Authentication required to create proposals")

    initiator = current_user.get("sub") if current_user else "anonymous"

    proposal_id = str(uuid.uuid4())
    # Convert string risk level to Enum
    try:
        risk_enum = RiskLevel(request.risk_level)
    except ValueError:
        risk_enum = RiskLevel.MEDIUM
        
    threshold = THRESHOLDS.get(risk_enum, THRESHOLDS[RiskLevel.MEDIUM])

    proposal = {
        "id": proposal_id,
        "title": request.title,
        "description": request.description,
        "cost": request.cost,
        "risk_level": request.risk_level,
        "status": "pending",
        "votes": [],
        "final_score": None,
        "threshold": threshold,
        "context": request.context or {},
        "auto_execute": request.auto_execute,
        "created_at": datetime.utcnow(),
        "resolved_at": None,
    }

    _proposals[proposal_id] = proposal

    # Trigger async voting
    background_tasks.add_task(_collect_votes, proposal_id)

    return _format_proposal_response(proposal)


@router.get("/proposals", response_model=List[ProposalSummary])
async def list_proposals(
    status: Optional[str] = Query(
        None, pattern="^(pending|approved|rejected|escalated)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List all proposals with optional filtering."""
    proposals = list(_proposals.values())

    if status:
        proposals = [p for p in proposals if p["status"] == status]

    # Sort by created_at descending
    proposals.sort(key=lambda x: x["created_at"], reverse=True)
    proposals = proposals[offset:offset + limit]

    return [
        ProposalSummary(
            proposal_id=p["id"],
            title=p["title"],
            status=p["status"],
            final_score=p["final_score"],
            vote_count=len(p["votes"]),
            created_at=p["created_at"],
        )
        for p in proposals
    ]


@router.get("/proposals/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(proposal_id: str):
    """Get details of a specific proposal."""
    if proposal_id not in _proposals:
        raise HTTPException(status_code=404, detail="Proposal not found")

    return _format_proposal_response(_proposals[proposal_id])


@router.post("/proposals/{proposal_id}/vote")
async def manual_vote(proposal_id: str, agent: str, vote: str, score: float, reasoning: List[str]):
    """Manually add a vote (for testing or override)."""
    if proposal_id not in _proposals:
        raise HTTPException(status_code=404, detail="Proposal not found")

    if agent not in PENTARCHY_AGENTS:
        raise HTTPException(
            status_code=400, detail=f"Agent must be one of: {PENTARCHY_AGENTS}")

    if vote not in ["APPROVE", "REJECT", "ABSTAIN"]:
        raise HTTPException(
            status_code=400, detail="Vote must be APPROVE, REJECT, or ABSTAIN")

    proposal = _proposals[proposal_id]

    # Remove existing vote from this agent
    proposal["votes"] = [v for v in proposal["votes"] if v["agent"] != agent]

    # Add new vote
    proposal["votes"].append({
        "agent": agent,
        "vote": vote,
        "score": score,
        "reasoning": reasoning,
        "timestamp": datetime.utcnow(),
    })

    # Check if voting is complete
    if len(proposal["votes"]) >= len(PENTARCHY_AGENTS):
        _resolve_proposal(proposal_id)

    return {"status": "voted", "proposal_id": proposal_id, "agent": agent, "vote": vote}


@router.post("/proposals/{proposal_id}/resolve")
async def resolve_proposal(proposal_id: str):
    """Force resolution of a pending proposal."""
    if proposal_id not in _proposals:
        raise HTTPException(status_code=404, detail="Proposal not found")

    proposal = _proposals[proposal_id]
    if proposal["status"] != "pending":
        raise HTTPException(
            status_code=400, detail="Proposal already resolved")

    _resolve_proposal(proposal_id)
    return _format_proposal_response(_proposals[proposal_id])


@router.get("/thresholds")
async def get_thresholds():
    """Get voting thresholds for different risk levels."""
    return {
        "thresholds": THRESHOLDS,
        "max_score": 3.0,
        "pentarchy_agents": PENTARCHY_AGENTS,
        "description": "Score must meet or exceed threshold for approval",
    }


@router.get("/stats")
async def get_voting_stats():
    """Get voting statistics."""
    proposals = list(_proposals.values())

    return {
        "total_proposals": len(proposals),
        "by_status": {
            "pending": len([p for p in proposals if p["status"] == "pending"]),
            "approved": len([p for p in proposals if p["status"] == "approved"]),
            "rejected": len([p for p in proposals if p["status"] == "rejected"]),
            "escalated": len([p for p in proposals if p["status"] == "escalated"]),
        },
        "average_score": sum(p["final_score"] or 0 for p in proposals) / len(proposals) if proposals else 0,
        "total_votes": sum(len(p["votes"]) for p in proposals),
    }


class ActionAnalysis(BaseModel):
    """Analysis result for determining if action requires voting."""
    requires_voting: bool
    estimated_cost: float
    risk_level: str
    action_type: str
    description: str


class AnalyzeActionRequest(BaseModel):
    """Request body for analyze-action endpoint."""
    message: str = Field(..., description="User message to analyze")
    context: Optional[Dict[str, Any]] = None


@router.post("/analyze-action", response_model=ActionAnalysis)
async def analyze_action(request: AnalyzeActionRequest):
    """
    Analyze a user message to determine if it requires Pentarchy voting.
    
    This endpoint checks if the action described in the message:
    - Has an estimated cost >= $50 (triggers voting)
    - Has an estimated cost >= $100 (requires human review)
    - Involves sensitive operations (security, legal, financial)
    """
    import re
    
    message = request.message
    
    # Keywords that suggest costly or sensitive operations
    cost_keywords = {
        "purchase": 75.0,
        "buy": 75.0,
        "subscribe": 60.0,
        "deploy": 80.0,
        "provision": 100.0,
        "scale": 70.0,
        "upgrade": 85.0,
        "migrate": 150.0,
        "delete": 50.0,
        "remove": 40.0,
        "transfer": 90.0,
        "payment": 100.0,
        "invoice": 50.0,
        "hire": 200.0,
        "contract": 150.0,
    }
    
    security_keywords = ["security", "access", "permission", "credential", "secret", "key", "password"]
    legal_keywords = ["legal", "compliance", "gdpr", "contract", "agreement", "terms"]
    
    message_lower = message.lower()
    
    # Detect explicit cost mentions (e.g., "$75", "100 dollars")
    cost_patterns = [
        r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars?|usd)',
        r'cost(?:s|ing)?\s*(?:about|around|approximately)?\s*\$?(\d+)',
    ]
    
    detected_cost = 0.0
    for pattern in cost_patterns:
        matches = re.findall(pattern, message_lower)
        for match in matches:
            try:
                cost = float(match.replace(",", ""))
                detected_cost = max(detected_cost, cost)
            except ValueError:
                pass
    
    # Check for action keywords
    action_type = "general"
    estimated_cost = detected_cost
    
    for keyword, default_cost in cost_keywords.items():
        if keyword in message_lower:
            action_type = keyword
            if estimated_cost == 0:
                estimated_cost = default_cost
            break
    
    # Check for security/legal sensitivity
    is_security = any(kw in message_lower for kw in security_keywords)
    is_legal = any(kw in message_lower for kw in legal_keywords)
    
    if is_security:
        action_type = "security"
        estimated_cost = max(estimated_cost, 100.0)  # Always requires human review
    elif is_legal:
        action_type = "legal"
        estimated_cost = max(estimated_cost, 100.0)
    
    # Determine risk level based on cost
    from src.core.governance import AUTO_APPROVE_LIMIT, HUMAN_REVIEW_LIMIT
    
    if estimated_cost >= HUMAN_REVIEW_LIMIT:
        risk_level = "high"
    elif estimated_cost >= AUTO_APPROVE_LIMIT:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    requires_voting = estimated_cost >= AUTO_APPROVE_LIMIT
    
    return ActionAnalysis(
        requires_voting=requires_voting,
        estimated_cost=estimated_cost,
        risk_level=risk_level,
        action_type=action_type,
        description=f"Action '{action_type}' with estimated cost ${estimated_cost:.2f}"
    )


class AutoProposalRequest(BaseModel):
    """Request body for auto-proposal endpoint."""
    message: str
    conversation_id: Optional[str] = None


@router.post("/auto-proposal")
async def create_auto_proposal(
    request: AutoProposalRequest,
    background_tasks: BackgroundTasks,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    Automatically create a proposal if the message warrants Pentarchy voting.
    
    This is called by the chat system when an action is detected that requires governance.
    """
    message = request.message
    conversation_id = request.conversation_id
    
    # First analyze the action
    analysis_request = AnalyzeActionRequest(message=message)
    analysis = await analyze_action(analysis_request)
    
    if not analysis.requires_voting:
        return {
            "proposal_created": False,
            "reason": "Action does not require voting (cost below threshold)",
            "analysis": analysis.model_dump()
        }
    
    # Create proposal
    proposal_request = ProposalRequest(
        title=f"Auto-generated: {analysis.action_type.title()} Action",
        description=message,
        cost=analysis.estimated_cost,
        risk_level=analysis.risk_level,
        context={"conversation_id": conversation_id, "auto_generated": True},
        auto_execute=False
    )
    
    response = await create_proposal(proposal_request, background_tasks, current_user)
    
    return {
        "proposal_created": True,
        "proposal_id": response.proposal_id,
        "analysis": analysis.model_dump(),
        "status": response.status
    }


@router.get("/pending")
async def get_pending_proposals():
    """Get all pending proposals that are awaiting votes."""
    pending = [p for p in _proposals.values() if p["status"] == "pending"]
    pending.sort(key=lambda x: x["created_at"], reverse=True)
    
    return [
        {
            "proposal_id": p["id"],
            "title": p["title"],
            "description": p["description"][:200] + "..." if len(p["description"]) > 200 else p["description"],
            "cost": p["cost"],
            "risk_level": p["risk_level"],
            "votes_collected": len(p["votes"]),
            "votes_needed": len(PENTARCHY_AGENTS),
            "created_at": p["created_at"].isoformat(),
        }
        for p in pending
    ]


def _format_proposal_response(proposal: dict) -> ProposalResponse:
    """Format proposal dict to response model."""
    return ProposalResponse(
        proposal_id=proposal["id"],
        title=proposal["title"],
        description=proposal["description"],
        cost=proposal["cost"],
        risk_level=proposal["risk_level"],
        status=proposal["status"],
        votes=[
            VoteResult(
                agent=v["agent"],
                vote=v["vote"],
                score=v["score"],
                reasoning=v["reasoning"],
                timestamp=v["timestamp"],
            )
            for v in proposal["votes"]
        ],
        final_score=proposal["final_score"],
        threshold=proposal["threshold"],
        created_at=proposal["created_at"],
        resolved_at=proposal["resolved_at"],
    )


async def _collect_votes(proposal_id: str):
    """Collect votes from all Pentarchy agents."""
    if proposal_id not in _proposals:
        return

    proposal = _proposals[proposal_id]

    for agent_name in PENTARCHY_AGENTS:
        try:
            vote_result = await _get_agent_vote(agent_name, proposal)
            proposal["votes"].append({
                "agent": agent_name,
                "vote": vote_result["vote"],
                "score": vote_result["score"],
                "reasoning": vote_result["reasoning"],
                "timestamp": datetime.utcnow(),
            })
        except Exception as e:
            logger.error(f"Failed to get vote from {agent_name}: {e}")
            # Add abstain on error
            proposal["votes"].append({
                "agent": agent_name,
                "vote": "ABSTAIN",
                "score": 1.5,
                "reasoning": [f"Error collecting vote: {str(e)}"],
                "timestamp": datetime.utcnow(),
            })

    # Resolve after all votes
    _resolve_proposal(proposal_id)


async def _get_agent_vote(agent_name: str, proposal: dict) -> dict:
    """Get vote from a specific agent."""
    try:
        # Try to use actual agent
        agent = None
        if agent_name == "athena":
            from src.agents.athena.main import AthenaAgent
            agent = AthenaAgent()
        elif agent_name == "hephaestus":
            from src.agents.hephaestus.main import HephaestusAgent
            agent = HephaestusAgent()
        elif agent_name == "hermes":
            from src.agents.hermes.main import HermesAgent
            agent = HermesAgent()
        elif agent_name == "prometheus":
            from src.agents.nur_prometheus.main import PrometheusAgent
            agent = PrometheusAgent()
        elif agent_name == "aegis":
            from src.agents.aegis.main import AegisAgent
            agent = AegisAgent()

        if agent and hasattr(agent, "evaluate_proposal"):
            from pydantic import BaseModel

            class ProposalRequest(BaseModel):
                proposal_id: str
                cost: float
                description: str

            request = ProposalRequest(
                proposal_id=proposal["id"],
                cost=proposal["cost"],
                description=proposal["description"],
            )
            result = await agent.evaluate_proposal(request)
            return {
                "vote": result.vote,
                "score": result.score,
                "reasoning": result.reasoning,
            }
    except Exception as e:
        logger.warning(f"Could not use agent {agent_name}: {e}")

    # Fallback mock vote
    import random
    vote = random.choice(["APPROVE", "APPROVE", "APPROVE", "REJECT"])
    score = random.uniform(
        1.5, 2.8) if vote == "APPROVE" else random.uniform(0.5, 1.5)

    return {
        "vote": vote,
        "score": round(score, 2),
        "reasoning": [f"Mock vote from {agent_name}", "Assessment pending full implementation"],
    }


def _resolve_proposal(proposal_id: str):
    """Resolve a proposal based on collected votes."""
    if proposal_id not in _proposals:
        return

    proposal = _proposals[proposal_id]

    if not proposal["votes"]:
        proposal["status"] = "escalated"
        proposal["resolved_at"] = datetime.utcnow()
        return

    # Calculate weighted average score
    total_score = sum(v["score"] for v in proposal["votes"])
    avg_score = total_score / len(proposal["votes"])

    proposal["final_score"] = round(avg_score, 2)

    # Determine outcome
    if avg_score >= proposal["threshold"]:
        proposal["status"] = "approved"
    elif avg_score < 1.0:
        proposal["status"] = "rejected"
    else:
        # Check for consensus issues
        approves = len([v for v in proposal["votes"]
                       if v["vote"] == "APPROVE"])
        rejects = len([v for v in proposal["votes"] if v["vote"] == "REJECT"])

        if rejects > approves:
            proposal["status"] = "rejected"
        elif approves >= 3:
            proposal["status"] = "approved"
        else:
            proposal["status"] = "escalated"

    proposal["resolved_at"] = datetime.utcnow()
    logger.info(
        f"Proposal {proposal_id} resolved: {proposal['status']} (score: {avg_score:.2f})")
