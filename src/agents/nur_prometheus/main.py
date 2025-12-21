import asyncio
import logging
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from fastmcp import FastMCP

from src.services.llm_service import get_llm_service, Message as LLMMessage

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("nur-prometheus-agent")

# --- Data Models ---


class AnalysisRequest(BaseModel):
    query_type: str
    parameters: Dict[str, Any]


class ReportRequest(BaseModel):
    report_type: str
    scope: str
    period: str


class PredictionRequest(BaseModel):
    metric: str
    horizon: str
    model: str = "linear"


class OptimizationRequest(BaseModel):
    domain: str
    constraints: Optional[Dict[str, Any]] = None


class ProposalEvaluationRequest(BaseModel):
    proposal_id: str
    cost: float
    description: str


class AnalysisResult(BaseModel):
    data: Dict[str, Any]
    insights: List[str]
    timestamp: datetime = Field(default_factory=datetime.now)


class PentarchyVote(BaseModel):
    vote: str  # "APPROVE", "REJECT", "ABSTAIN"
    score: float
    reasoning: List[str]

# --- Agent Implementation ---


class NurPrometheusAgent:
    def __init__(self):
        self.name = "nur-prometheus"
        self.version = "2.0.0"
        self.mcp = FastMCP(self.name)
        self.llm = get_llm_service()
        self.system_prompt = """You are Nur-Prometheus, the Analytics & Finance Agent in the KOSMOS Pentarchy.
Your domain: Data analysis, financial forecasting, budget management, optimization.
When evaluating proposals, assess:
1. Budget impact and cost-effectiveness
2. ROI and financial sustainability
3. Resource utilization efficiency
4. Data-driven risk assessment

For Pentarchy votes, respond with JSON: {"vote": "APPROVE/REJECT/ABSTAIN", "score": 0-3, "reasoning": ["reason1", "reason2"]}"""
        logger.info(f"Initializing {self.name} Agent v{self.version}")

        # Register tools
        self.mcp.tool()(self.analyze_data)
        self.mcp.tool()(self.generate_report)
        self.mcp.tool()(self.predict_trend)
        self.mcp.tool()(self.recommend_optimization)
        self.mcp.tool()(self.evaluate_proposal)

    async def analyze_data(self, request: AnalysisRequest) -> AnalysisResult:
        logger.info(f"Analyzing data: {request.query_type}")
        # TODO: Integrate with mcp-postgresql
        return AnalysisResult(
            data={"mock_metric": 100, "trend": "up"},
            insights=["Metric is increasing", "Performance is stable"]
        )

    async def generate_report(self, request: ReportRequest) -> str:
        logger.info(
            f"Generating {request.report_type} report for {request.scope}")
        return f"Report: {request.report_type} - {request.scope} ({request.period})\n[Mock Report Content]"

    async def predict_trend(self, request: PredictionRequest) -> Dict[str, Any]:
        logger.info(f"Predicting trend for {request.metric}")
        return {
            "metric": request.metric,
            "forecast": [100, 110, 120],
            "confidence": 0.85
        }

    async def recommend_optimization(self, request: OptimizationRequest) -> List[str]:
        logger.info(f"Generating optimizations for {request.domain}")
        return [
            "Reduce cache TTL to save memory",
            "Scale down during off-peak hours"
        ]

    async def evaluate_proposal(self, proposal_id: str, cost: float, description: str) -> PentarchyVote:
        """Evaluate a proposal from financial/analytics perspective."""
        logger.info(
            f"Evaluating proposal {proposal_id} (Cost: ${cost})")

        if self.llm:
            try:
                prompt = f"""Evaluate this proposal from a financial/analytics perspective:
Proposal ID: {proposal_id}
Cost: ${cost}
Description: {description}

Consider: budget impact, ROI, cost-effectiveness, resource efficiency.
Respond with JSON: {{"vote": "APPROVE/REJECT/ABSTAIN", "score": 0-3, "reasoning": ["reason1", "reason2"]}}"""

                response = await self.llm.chat([
                    LLMMessage(role="system", content=self.system_prompt),
                    LLMMessage(role="user", content=prompt)
                ])

                import json
                import re
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
        budget_remaining = 1000.0
        score = 2 if cost < budget_remaining * 0.1 else 1
        reasoning = ["Cost within budget parameters", "ROI analysis positive"]
        return PentarchyVote(vote="APPROVE", score=score, reasoning=reasoning)

    def run(self):
        """Start the Nur Prometheus MCP server."""
        self.mcp.run()

# --- Entry Point ---


if __name__ == "__main__":
    agent = NurPrometheusAgent()
    agent.run()
