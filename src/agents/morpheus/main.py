from typing import Dict, Any, List, Optional
from fastmcp import FastMCP
from pydantic import BaseModel, Field
import asyncio
import json
import re
import logging

from src.services.llm_service import get_llm_service, Message as LLMMessage

logger = logging.getLogger("morpheus-agent")


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

# Define data models


class Feedback(BaseModel):
    feedback_id: str = Field(...,
                             description="Unique identifier for the feedback")
    content: str = Field(..., description="The feedback content")
    rating: int = Field(..., description="Rating (1-5)")
    source: str = Field(...,
                        description="Source of feedback (e.g., 'user', 'system')")


class PromptOptimizationRequest(BaseModel):
    prompt_id: str = Field(..., description="ID of the prompt to optimize")
    current_template: str = Field(..., description="Current prompt template")
    performance_metrics: Dict[str, float] = Field(
        ..., description="Performance metrics (e.g., latency, accuracy)")


class ModelRecommendationRequest(BaseModel):
    task_type: str = Field(...,
                           description="Type of task (e.g., 'coding', 'creative_writing')")
    constraints: Dict[str, Any] = Field(
        default_factory=dict, description="Constraints (e.g., 'max_cost', 'min_speed')")


class MorpheusAgent:
    """
    MORPHEUS: Learning & Optimization Agent
    Responsible for continuous learning, pattern recognition, and system optimization.
    """

    def __init__(self):
        self.name = "morpheus"
        self.version = "2.0.0"
        self.mcp = FastMCP(self.name)
        self.llm = get_llm_service()
        self.system_prompt = """You are MORPHEUS, the Learning & Optimization Agent in the KOSMOS Pentarchy.
Your domain: Machine learning, pattern recognition, system optimization, feedback loops.
When evaluating proposals, assess:
1. Learning and adaptation opportunities
2. Performance optimization potential
3. Pattern implications and predictions
4. System efficiency and scalability

For Pentarchy votes, respond with JSON: {"vote": "APPROVE/REJECT/ABSTAIN", "score": 0-3, "reasoning": ["reason1", "reason2"]}"""
        self.patterns: List[Dict[str, Any]] = []
        self.feedback_store: List[Dict[str, Any]] = []
        logger.info(f"Initializing {self.name} Agent v{self.version}")

        # Register tools
        self.mcp.tool()(self.process_query)
        self.mcp.tool()(self.analyze_patterns)
        self.mcp.tool()(self.process_feedback)
        self.mcp.tool()(self.optimize_prompt)
        self.mcp.tool()(self.recommend_model)
        self.mcp.tool()(self.detect_anomaly)
        self.mcp.tool()(self.evaluate_proposal)

    async def process_query(self, query: str, conversation_id: str = "") -> str:
        """Process an optimization/learning-related query using LLM."""
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
        return f"MORPHEUS: Optimization analysis for '{query}' - mock response"

    async def evaluate_proposal(self, request: ProposalEvaluationRequest) -> PentarchyVote:
        """Evaluate a proposal from optimization perspective for Pentarchy voting."""
        logger.info(
            f"Evaluating proposal {request.proposal_id} for optimization")

        if self.llm:
            try:
                prompt = f"""Evaluate this proposal from an OPTIMIZATION/LEARNING perspective:
Proposal ID: {request.proposal_id}
Cost: ${request.cost}
Description: {request.description}

Consider: learning opportunities, performance gains, scalability, efficiency.
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
        return PentarchyVote(vote="APPROVE", score=2, reasoning=["Learning potential high", "Performance gains expected"])

    async def analyze_patterns(self, scope: str = "global", time_range: str = "24h") -> List[Dict[str, Any]]:
        """Identify recurring patterns in agent behavior."""
        # Mock logic for pattern recognition
        return [
            {"pattern": "High latency in RAG queries",
                "frequency": "high", "impact": "medium"},
            {"pattern": "Frequent code generation errors in Python",
                "frequency": "low", "impact": "high"}
        ]

    async def process_feedback(self, feedback: Feedback) -> str:
        """Integrate human or system feedback."""
        self.feedback_store.append(feedback.model_dump())
        return f"Feedback {feedback.feedback_id} processed. Learning updated."

    async def optimize_prompt(self, request: PromptOptimizationRequest) -> str:
        """Suggest improvements for a prompt template."""
        # Mock logic for prompt optimization
        improved_template = request.current_template + \
            "\n# Optimized for clarity and conciseness."
        return f"Optimized prompt for {request.prompt_id}. Suggestion: {improved_template}"

    async def recommend_model(self, request: ModelRecommendationRequest) -> str:
        """Suggest the optimal LLM for a specific task."""
        # Mock logic for model routing
        if request.task_type == "coding":
            return "claude-3-5-sonnet"
        elif request.task_type == "creative_writing":
            return "gpt-4o"
        return "gpt-4o-mini"

    async def detect_anomaly(self, metric: str, baseline: float) -> Dict[str, Any]:
        """Identify performance anomalies."""
        # Mock logic for anomaly detection
        current_value = baseline * 1.2  # Simulate a 20% increase
        is_anomaly = current_value > (baseline * 1.1)
        return {
            "metric": metric,
            "current_value": current_value,
            "is_anomaly": is_anomaly,
            "severity": "medium" if is_anomaly else "low"
        }

    def run(self):
        """Start the Morpheus MCP server."""
        self.mcp.run()


if __name__ == "__main__":
    agent = MorpheusAgent()
    agent.run()
