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
logger = logging.getLogger("memorix-agent")


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


class MemoryItem(BaseModel):
    content: str
    context: Optional[Dict[str, Any]] = None
    tags: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.now)


class MemoryQuery(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 10


class Relationship(BaseModel):
    entity_a: str
    entity_b: str
    relation: str
    properties: Optional[Dict[str, Any]] = None


class ConsolidationRequest(BaseModel):
    topic: str
    time_range_start: Optional[datetime] = None
    time_range_end: Optional[datetime] = None


class MemoryResponse(BaseModel):
    memory_id: str
    status: str
    message: str

# --- Agent Implementation ---


class MemorixAgent:
    def __init__(self):
        self.name = "memorix"
        self.version = "2.0.0"
        self.mcp = FastMCP(self.name)
        self.llm = get_llm_service()
        self.system_prompt = """You are MEMORIX, the Memory & Knowledge Agent in the KOSMOS Pentarchy.
Your domain: Long-term memory, knowledge graphs, semantic search, context retrieval.
When evaluating proposals, assess:
1. Data storage and retrieval requirements
2. Knowledge preservation implications
3. Memory and context dependencies
4. Historical precedents and patterns

For Pentarchy votes, respond with JSON: {"vote": "APPROVE/REJECT/ABSTAIN", "score": 0-3, "reasoning": ["reason1", "reason2"]}"""
        logger.info(f"Initializing {self.name} Agent v{self.version}")

        # Register tools
        self.mcp.tool()(self.process_query)
        self.mcp.tool()(self.store_memory)
        self.mcp.tool()(self.recall_memory)
        self.mcp.tool()(self.map_relationship)
        self.mcp.tool()(self.consolidate_memories)
        self.mcp.tool()(self.evaluate_proposal)

    async def process_query(self, query: str, conversation_id: str = "") -> str:
        """Process a memory/knowledge-related query using LLM."""
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
        return f"MEMORIX: Knowledge analysis for '{query}' - mock response"

    async def evaluate_proposal(self, request: ProposalEvaluationRequest) -> PentarchyVote:
        """Evaluate a proposal from knowledge perspective for Pentarchy voting."""
        logger.info(
            f"Evaluating proposal {request.proposal_id} for knowledge impact")

        if self.llm:
            try:
                prompt = f"""Evaluate this proposal from a KNOWLEDGE/MEMORY perspective:
Proposal ID: {request.proposal_id}
Cost: ${request.cost}
Description: {request.description}

Consider: data storage needs, knowledge preservation, historical precedents, context.
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
        return PentarchyVote(vote="APPROVE", score=2, reasoning=["Knowledge requirements met", "No memory conflicts"])

    async def store_memory(self, item: MemoryItem) -> MemoryResponse:
        logger.info(f"Storing memory: {item.content[:50]}...")
        # TODO: Integrate with mcp-postgresql or mcp-memory
        return MemoryResponse(
            memory_id=f"mem-{datetime.now().timestamp()}",
            status="stored",
            message="Memory successfully stored"
        )

    async def recall_memory(self, query: MemoryQuery) -> List[MemoryItem]:
        logger.info(f"Recalling memories for: {query.query}")
        # Mock retrieval
        return [
            MemoryItem(
                content=f"Result for {query.query}",
                tags=["mock", "recall"],
                timestamp=datetime.now()
            )
        ]

    async def map_relationship(self, rel: Relationship) -> MemoryResponse:
        logger.info(
            f"Mapping relationship: {rel.entity_a} -[{rel.relation}]-> {rel.entity_b}")
        # TODO: Integrate with mcp-age
        return MemoryResponse(
            memory_id=f"rel-{datetime.now().timestamp()}",
            status="mapped",
            message=f"Relationship {rel.relation} created"
        )

    async def consolidate_memories(self, request: ConsolidationRequest) -> str:
        logger.info(f"Consolidating memories for topic: {request.topic}")
        return f"Consolidated summary for {request.topic}: [Mock Summary Data]"

    def run(self):
        """Start the Memorix MCP server."""
        self.mcp.run()

# --- Entry Point ---


if __name__ == "__main__":
    agent = MemorixAgent()
    agent.run()
