import asyncio
import logging
import json
import re
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from fastmcp import FastMCP

from src.services.llm_service import get_llm_service, Message as LLMMessage

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("iris-agent")


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


class ComponentRequest(BaseModel):
    component_type: str
    data: Dict[str, Any]


class ChartRequest(BaseModel):
    chart_type: str
    data: List[Dict[str, Any]]
    options: Optional[Dict[str, Any]] = None


class TemplateRequest(BaseModel):
    template_name: str
    context: Dict[str, Any]


class ConversionRequest(BaseModel):
    content: str
    source_format: str
    target_format: str


class RenderResult(BaseModel):
    content: str
    format: str
    metadata: Optional[Dict[str, Any]] = None

# --- Agent Implementation ---


class IrisAgent:
    def __init__(self):
        self.name = "iris"
        self.version = "2.0.0"
        self.mcp = FastMCP(self.name)
        self.llm = get_llm_service()
        self.system_prompt = """You are IRIS, the Visualization & UI Agent in the KOSMOS Pentarchy.
Your domain: Data visualization, UI rendering, charts, templates, format conversion.
When evaluating proposals, assess:
1. User interface and experience implications
2. Visualization requirements and complexity
3. Rendering performance and accessibility
4. Design consistency and standards

For Pentarchy votes, respond with JSON: {"vote": "APPROVE/REJECT/ABSTAIN", "score": 0-3, "reasoning": ["reason1", "reason2"]}"""
        logger.info(f"Initializing {self.name} Agent v{self.version}")

        # Register tools
        self.mcp.tool()(self.process_query)
        self.mcp.tool()(self.render_component)
        self.mcp.tool()(self.create_chart)
        self.mcp.tool()(self.render_template)
        self.mcp.tool()(self.convert_format)
        self.mcp.tool()(self.evaluate_proposal)

    async def process_query(self, query: str, conversation_id: str = "") -> str:
        """Process a visualization/UI-related query using LLM."""
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
        return f"IRIS: Visualization analysis for '{query}' - mock response"

    async def evaluate_proposal(self, request: ProposalEvaluationRequest) -> PentarchyVote:
        """Evaluate a proposal from UI/visualization perspective for Pentarchy voting."""
        logger.info(f"Evaluating proposal {request.proposal_id} for UI/UX")

        if self.llm:
            try:
                prompt = f"""Evaluate this proposal from a UI/VISUALIZATION perspective:
Proposal ID: {request.proposal_id}
Cost: ${request.cost}
Description: {request.description}

Consider: UI implications, visualization needs, accessibility, design consistency.
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
        return PentarchyVote(vote="APPROVE", score=2, reasoning=["UI requirements clear", "Design feasible"])

    async def render_component(self, request: ComponentRequest) -> RenderResult:
        logger.info(f"Rendering component: {request.component_type}")
        # Mock rendering
        return RenderResult(
            content=f"<div class='{request.component_type}'>{request.data}</div>",
            format="html"
        )

    async def create_chart(self, request: ChartRequest) -> RenderResult:
        logger.info(f"Creating {request.chart_type} chart")
        # Mock chart generation
        return RenderResult(
            content=f"[Chart: {request.chart_type} with {len(request.data)} points]",
            format="image/png"
        )

    async def render_template(self, request: TemplateRequest) -> RenderResult:
        logger.info(f"Rendering template: {request.template_name}")
        # Mock template rendering
        return RenderResult(
            content=f"Rendered {request.template_name} with context keys: {list(request.context.keys())}",
            format="text"
        )

    async def convert_format(self, request: ConversionRequest) -> RenderResult:
        logger.info(
            f"Converting from {request.source_format} to {request.target_format}")
        return RenderResult(
            content=f"Converted content ({request.target_format})",
            format=request.target_format
        )

    def run(self):
        """Start the Iris MCP server."""
        self.mcp.run()

# --- Entry Point ---


if __name__ == "__main__":
    agent = IrisAgent()
    agent.run()
