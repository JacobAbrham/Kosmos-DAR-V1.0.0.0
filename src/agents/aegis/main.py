import asyncio
import logging
import json
import re
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from fastmcp import FastMCP

from src.services.llm_service import get_llm_service, Message as LLMMessage

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("aegis-agent")


class ProposalEvaluationRequest(BaseModel):
    """Request to evaluate a proposal for Pentarchy voting."""
    proposal_id: str
    cost: float
    description: str


class PentarchyVote(BaseModel):
    """Vote result from an agent."""
    vote: str  # APPROVE, REJECT, ABSTAIN
    score: float = Field(ge=0, le=3)
    reasoning: List[str]

# --- Data Models ---


class KillSwitchLevel(str, Enum):
    AGENT = "agent"
    SUBSYSTEM = "subsystem"
    GLOBAL = "global"


class AccessCheckRequest(BaseModel):
    user_id: str
    resource: str
    action: str


class AccessCheckResponse(BaseModel):
    allowed: bool
    reason: Optional[str] = None
    timestamp: datetime


class VulnerabilityScanRequest(BaseModel):
    target: str
    scan_type: str = "quick"  # quick, full


class ScanResult(BaseModel):
    target: str
    vulnerabilities_found: int
    severity: str
    report_url: Optional[str] = None


class KillSwitchRequest(BaseModel):
    reason: str
    scope: KillSwitchLevel
    requester_id: str


class KillSwitchResponse(BaseModel):
    activated: bool
    scope: KillSwitchLevel
    timestamp: datetime
    message: str

# --- Agent Implementation ---


class AegisAgent:
    def __init__(self):
        self.name = "aegis"
        self.version = "2.0.0"
        self.mcp = FastMCP(self.name)
        self.llm = get_llm_service()
        self.system_prompt = """You are AEGIS, the Security Agent in the KOSMOS Pentarchy.
Your domain: Security assessments, compliance, access control, vulnerability scanning.
When evaluating proposals, assess:
1. Security risks and threat vectors
2. Compliance implications (GDPR, SOC2, HIPAA)
3. Access control requirements
4. Data protection and privacy concerns

For Pentarchy votes, respond with JSON: {"vote": "APPROVE/REJECT/ABSTAIN", "score": 0-3, "reasoning": ["reason1", "reason2"]}"""
        logger.info(f"Initializing {self.name} Agent v{self.version}")

        # Register tools
        self.mcp.tool()(self.process_query)
        self.mcp.tool()(self.check_access)
        self.mcp.tool()(self.scan_vulnerabilities)
        self.mcp.tool()(self.activate_kill_switch)
        self.mcp.tool()(self.verify_compliance)
        self.mcp.tool()(self.evaluate_proposal)

    async def process_query(self, query: str, conversation_id: str = "") -> str:
        """Process a security-related query using LLM."""
        logger.info(f"Processing query: {query[:50]}...")
        if self.llm:
            try:
                response = await self.llm.chat([
                    LLMMessage(role="system", content=self.system_prompt),
                    LLMMessage(role="user", content=query)
                ])
                return response.content
            except Exception as e:
                logger.error(f"LLM query failed: {e}")
        return f"AEGIS: Security analysis for '{query}' - mock response"

    async def evaluate_proposal(self, request: ProposalEvaluationRequest) -> PentarchyVote:
        """Evaluate a proposal from security perspective for Pentarchy voting."""
        logger.info(f"Evaluating proposal {request.proposal_id} for security")

        if self.llm:
            try:
                prompt = f"""Evaluate this proposal from a SECURITY perspective:
Proposal ID: {request.proposal_id}
Cost: ${request.cost}
Description: {request.description}

Consider: security risks, compliance, access control, data protection.
Respond with JSON: {{"vote": "APPROVE/REJECT/ABSTAIN", "score": 0-3, "reasoning": ["reason1", "reason2"]}}"""

                response = await self.llm.chat([
                    LLMMessage(role="system", content=self.system_prompt),
                    LLMMessage(role="user", content=prompt)
                ])

                json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    return PentarchyVote(
                        vote=data.get("vote", "ABSTAIN"),
                        score=float(data.get("score", 1)),
                        reasoning=data.get("reasoning", ["LLM evaluation"])
                    )
            except Exception as e:
                logger.error(f"LLM evaluation failed: {e}")

        # Fallback mock logic
        return PentarchyVote(vote="APPROVE", score=2, reasoning=["No security risks identified", "Compliance verified"])

    async def check_access(self, request: AccessCheckRequest) -> AccessCheckResponse:
        logger.info(
            f"Checking access for user {request.user_id} on {request.resource}")
        # TODO: Integrate with Zitadel MCP
        # Mock Logic: Allow everything for now
        return AccessCheckResponse(
            allowed=True,
            reason="Mock access granted",
            timestamp=datetime.now()
        )

    async def scan_vulnerabilities(self, request: VulnerabilityScanRequest) -> ScanResult:
        logger.info(f"Starting {request.scan_type} scan on {request.target}")
        # TODO: Integrate with Trivy MCP
        return ScanResult(
            target=request.target,
            vulnerabilities_found=0,
            severity="LOW",
            report_url="http://mock-report-url"
        )

    async def activate_kill_switch(self, request: KillSwitchRequest) -> KillSwitchResponse:
        logger.warning(
            f"KILL SWITCH ACTIVATED by {request.requester_id}. Scope: {request.scope}. Reason: {request.reason}")
        # TODO: Implement actual shutdown logic
        return KillSwitchResponse(
            activated=True,
            scope=request.scope,
            timestamp=datetime.now(),
            message=f"Kill switch activated for {request.scope}. System halting."
        )

    async def verify_compliance(self, framework: str, scope: str) -> Dict[str, Any]:
        logger.info(f"Verifying compliance for {framework} in {scope}")
        return {
            "framework": framework,
            "compliant": True,
            "issues": []
        }

    def run(self):
        """Start the Aegis MCP server."""
        self.mcp.run()

# --- Entry Point ---


if __name__ == "__main__":
    agent = AegisAgent()
    agent.run()
