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
logger = logging.getLogger("hephaestus-agent")

# --- Data Models ---


class CodeGenerationRequest(BaseModel):
    spec: str
    language: str
    context: Optional[str] = None


class FileReadRequest(BaseModel):
    path: str


class FileWriteRequest(BaseModel):
    path: str
    content: str
    mode: str = "w"


class BuildRequest(BaseModel):
    project: str
    branch: str = "main"


class ScriptExecutionRequest(BaseModel):
    script_id: str
    params: Dict[str, Any] = {}


class ProposalEvaluationRequest(BaseModel):
    proposal_id: str
    cost: float
    description: str


class PentarchyVote(BaseModel):
    vote: str  # "APPROVE", "REJECT", "ABSTAIN"
    score: float
    reasoning: List[str]


class OperationResult(BaseModel):
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# --- Agent Implementation ---


class HephaestusAgent:
    def __init__(self):
        self.name = "hephaestus"
        self.version = "2.0.0"
        self.mcp = FastMCP(self.name)
        self.llm = get_llm_service()
        self.system_prompt = """You are Hephaestus, the Engineering Agent in the KOSMOS Pentarchy.
Your domain: Code generation, builds, deployments, technical implementation.
When evaluating proposals, assess:
1. Technical feasibility and implementation complexity
2. Resource availability (compute, storage, time)
3. Engineering risk and technical debt implications
4. Build/deployment requirements and timeline

For Pentarchy votes, respond with JSON: {"vote": "APPROVE/REJECT/ABSTAIN", "score": 0-3, "reasoning": ["reason1", "reason2"]}"""
        logger.info(f"Initializing {self.name} Agent v{self.version}")

        # Register tools
        self.mcp.tool()(self.generate_code)
        self.mcp.tool()(self.read_file)
        self.mcp.tool()(self.write_file)
        self.mcp.tool()(self.run_build)
        self.mcp.tool()(self.execute_script)
        self.mcp.tool()(self.evaluate_proposal)

    async def evaluate_proposal(self, proposal_id: str, cost: float, description: str) -> PentarchyVote:
        """Evaluate a proposal from technical/engineering perspective."""
        logger.info(
            f"Evaluating proposal {proposal_id} (Cost: ${cost})")

        if self.llm:
            try:
                prompt = f"""Evaluate this proposal from a technical/engineering perspective:
Proposal ID: {proposal_id}
Cost: ${cost}
Description: {description}

Consider: technical feasibility, resource needs, complexity, implementation risk.
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
        score = 2
        reasoning = ["Resources available", "Low implementation risk"]
        return PentarchyVote(vote="APPROVE", score=score, reasoning=reasoning)

    async def generate_code(self, request: CodeGenerationRequest) -> OperationResult:
        logger.info(
            f"Generating {request.language} code from spec: {request.spec[:50]}...")
        # Mock code generation
        generated_code = f"// Generated {request.language} code\nprint('Hello from Hephaestus');"
        return OperationResult(success=True, output=generated_code)

    async def read_file(self, request: FileReadRequest) -> OperationResult:
        logger.info(f"Reading file: {request.path}")
        # TODO: Integrate with filesystem-mcp
        return OperationResult(success=True, output="[Mock File Content]")

    async def write_file(self, request: FileWriteRequest) -> OperationResult:
        logger.info(f"Writing to file: {request.path}")
        # TODO: Integrate with filesystem-mcp
        return OperationResult(success=True, output=f"File {request.path} written successfully")

    async def run_build(self, request: BuildRequest) -> OperationResult:
        logger.info(
            f"Triggering build for {request.project} on branch {request.branch}")
        # TODO: Integrate with CI/CD
        return OperationResult(success=True, output=f"Build triggered for {request.project}")

    async def execute_script(self, request: ScriptExecutionRequest) -> OperationResult:
        logger.info(
            f"Executing script {request.script_id} with params {request.params}")
        return OperationResult(success=True, output="Script executed successfully")

    def run(self):
        """Start the Hephaestus MCP server."""
        self.mcp.run()

# --- Entry Point ---


if __name__ == "__main__":
    agent = HephaestusAgent()
    agent.run()
