"""
Zeus Agent - Enhanced LangGraph Implementation
Supreme coordinator of the Pentarchy governance system.
Implements full reasoning chains with LangGraph state management.
"""
import asyncio
from datetime import datetime
from enum import Enum
from typing import Any, Literal, TypedDict
from uuid import uuid4

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

from src.core.logging import get_logger
from src.core.tracing import traced, add_span_attributes

logger = get_logger(__name__)


class ProposalType(str, Enum):
    """Types of proposals that can be submitted to the Pentarchy."""
    RESOURCE_ALLOCATION = "resource_allocation"
    POLICY_CHANGE = "policy_change"
    INFRASTRUCTURE = "infrastructure"
    CREW_ASSIGNMENT = "crew_assignment"
    EMERGENCY_RESPONSE = "emergency_response"
    RESEARCH_INITIATIVE = "research_initiative"
    MAINTENANCE_SCHEDULE = "maintenance_schedule"


class VoteDecision(str, Enum):
    """Possible voting decisions."""
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"
    DEFER = "defer"


class AgentVote(BaseModel):
    """Individual agent vote on a proposal."""
    agent_id: str
    agent_name: str
    decision: VoteDecision
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    concerns: list[str] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Proposal(BaseModel):
    """A proposal submitted to the Pentarchy for voting."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str
    proposal_type: ProposalType
    submitted_by: str
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    priority: int = Field(ge=1, le=5, default=3)
    metadata: dict[str, Any] = Field(default_factory=dict)


class VotingResult(BaseModel):
    """Result of a Pentarchy vote."""
    proposal_id: str
    outcome: VoteDecision
    total_votes: int
    approve_votes: int
    reject_votes: int
    abstain_votes: int
    votes: list[AgentVote]
    consensus_reached: bool
    consensus_threshold: float = 0.6
    final_reasoning: str
    completed_at: datetime = Field(default_factory=datetime.utcnow)


class ZeusState(TypedDict):
    """State for Zeus LangGraph workflow."""
    messages: list[BaseMessage]
    proposal: Proposal | None
    votes: list[AgentVote]
    current_phase: str
    analysis_complete: bool
    votes_collected: bool
    result: VotingResult | None
    iteration: int


class ZeusLangGraphAgent:
    """
    Zeus - Supreme Coordinator of the Pentarchy.

    Implements a full LangGraph-based workflow for:
    - Analyzing proposals
    - Coordinating with other Pentarchy agents
    - Collecting and aggregating votes
    - Making final decisions based on consensus
    """

    SYSTEM_PROMPT = """You are Zeus, the Supreme Coordinator of the Pentarchy governance system.
Your role is to:
1. Analyze proposals submitted by crew members
2. Coordinate deliberation among the Pentarchy council
3. Ensure fair and thorough evaluation
4. Aggregate votes and determine consensus
5. Communicate decisions with clear reasoning

The Pentarchy consists of:
- Zeus (you): Supreme Coordinator - overall system governance
- Athena: Strategic Advisor - long-term planning and resource optimization
- Hermes: Communications Director - crew relations and information flow
- Hephaestus: Engineering Chief - technical feasibility and implementation
- Apollo: Welfare Officer - crew wellbeing and morale

You must be fair, thorough, and transparent in all decisions.
Always provide clear reasoning for your conclusions."""

    def __init__(
        self,
        llm_provider: str = "openai",
        model_name: str | None = None,
        temperature: float = 0.3,
    ):
        """Initialize Zeus with LLM configuration."""
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.temperature = temperature
        self._llm = self._create_llm()
        self._graph = self._build_graph()
        logger.info(f"Zeus initialized with {llm_provider} provider")

    def _create_llm(self):
        """Create the LLM instance based on provider."""
        if self.llm_provider == "openai":
            return ChatOpenAI(
                model=self.model_name or "gpt-4o",
                temperature=self.temperature,
            )
        elif self.llm_provider == "anthropic":
            return ChatAnthropic(
                model=self.model_name or "claude-3-5-sonnet-20241022",
                temperature=self.temperature,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for Zeus."""
        workflow = StateGraph(ZeusState)

        # Add nodes
        workflow.add_node("analyze_proposal", self._analyze_proposal)
        workflow.add_node("collect_votes", self._collect_votes)
        workflow.add_node("aggregate_results", self._aggregate_results)
        workflow.add_node("generate_decision", self._generate_decision)

        # Define edges
        workflow.set_entry_point("analyze_proposal")
        workflow.add_edge("analyze_proposal", "collect_votes")
        workflow.add_edge("collect_votes", "aggregate_results")
        workflow.add_edge("aggregate_results", "generate_decision")
        workflow.add_edge("generate_decision", END)

        return workflow.compile()

    @traced(name="zeus_analyze_proposal")
    async def _analyze_proposal(self, state: ZeusState) -> ZeusState:
        """Analyze the submitted proposal."""
        proposal = state["proposal"]

        analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", self.SYSTEM_PROMPT),
            ("human", """Analyze the following proposal:

Title: {title}
Type: {proposal_type}
Priority: {priority}
Submitted by: {submitted_by}

Description:
{description}

Provide a thorough analysis considering:
1. Alignment with mission objectives
2. Resource requirements
3. Potential risks and benefits
4. Timeline feasibility
5. Impact on crew operations""")
        ])

        messages = analysis_prompt.format_messages(
            title=proposal.title,
            proposal_type=proposal.proposal_type.value,
            priority=proposal.priority,
            submitted_by=proposal.submitted_by,
            description=proposal.description,
        )

        response = await self._llm.ainvoke(messages)

        add_span_attributes({
            "proposal.id": proposal.id,
            "proposal.type": proposal.proposal_type.value,
        })

        return {
            **state,
            "messages": state["messages"] + [response],
            "analysis_complete": True,
            "current_phase": "analysis_complete",
        }

    @traced(name="zeus_collect_votes")
    async def _collect_votes(self, state: ZeusState) -> ZeusState:
        """Collect votes from Pentarchy agents (simulated for now)."""
        proposal = state["proposal"]

        # In production, this would communicate with actual agent instances
        # For now, we simulate the voting process
        agents = [
            ("athena", "Athena", "Strategic Advisor"),
            ("hermes", "Hermes", "Communications Director"),
            ("hephaestus", "Hephaestus", "Engineering Chief"),
            ("apollo", "Apollo", "Welfare Officer"),
        ]

        votes = []
        for agent_id, agent_name, role in agents:
            vote_prompt = ChatPromptTemplate.from_messages([
                ("system", f"""You are {agent_name}, the {role} of the Pentarchy council.
You are evaluating a proposal and must provide your vote and reasoning.
Consider your specific domain expertise when evaluating.
Be thorough but concise in your reasoning."""),
                ("human", """Evaluate this proposal:

Title: {title}
Type: {proposal_type}
Description: {description}

Previous analysis:
{analysis}

Provide your vote (approve/reject/abstain/defer), confidence (0.0-1.0), 
reasoning, any concerns, and conditions for approval.""")
            ])

            messages = vote_prompt.format_messages(
                title=proposal.title,
                proposal_type=proposal.proposal_type.value,
                description=proposal.description,
                analysis=state["messages"][-1].content if state["messages"] else "No prior analysis",
            )

            response = await self._llm.ainvoke(messages)

            # Parse the response (simplified - in production use structured output)
            vote = AgentVote(
                agent_id=agent_id,
                agent_name=agent_name,
                decision=self._parse_vote_decision(response.content),
                confidence=self._parse_confidence(response.content),
                reasoning=response.content,
                concerns=[],
                conditions=[],
            )
            votes.append(vote)

        return {
            **state,
            "votes": votes,
            "votes_collected": True,
            "current_phase": "votes_collected",
        }

    @traced(name="zeus_aggregate_results")
    async def _aggregate_results(self, state: ZeusState) -> ZeusState:
        """Aggregate voting results."""
        votes = state["votes"]

        approve_count = sum(
            1 for v in votes if v.decision == VoteDecision.APPROVE)
        reject_count = sum(1 for v in votes if v.decision ==
                           VoteDecision.REJECT)
        abstain_count = sum(
            1 for v in votes if v.decision == VoteDecision.ABSTAIN)

        total_decisive = approve_count + reject_count
        consensus_threshold = 0.6

        if total_decisive > 0:
            approval_ratio = approve_count / total_decisive
            if approval_ratio >= consensus_threshold:
                outcome = VoteDecision.APPROVE
                consensus = True
            elif approval_ratio <= (1 - consensus_threshold):
                outcome = VoteDecision.REJECT
                consensus = True
            else:
                outcome = VoteDecision.DEFER
                consensus = False
        else:
            outcome = VoteDecision.ABSTAIN
            consensus = False

        result = VotingResult(
            proposal_id=state["proposal"].id,
            outcome=outcome,
            total_votes=len(votes),
            approve_votes=approve_count,
            reject_votes=reject_count,
            abstain_votes=abstain_count,
            votes=votes,
            consensus_reached=consensus,
            final_reasoning="",  # Will be filled by generate_decision
        )

        return {
            **state,
            "result": result,
            "current_phase": "results_aggregated",
        }

    @traced(name="zeus_generate_decision")
    async def _generate_decision(self, state: ZeusState) -> ZeusState:
        """Generate final decision with reasoning."""
        result = state["result"]
        proposal = state["proposal"]

        decision_prompt = ChatPromptTemplate.from_messages([
            ("system", self.SYSTEM_PROMPT),
            ("human", """The Pentarchy has voted on the following proposal:

Title: {title}
Description: {description}

Voting Results:
- Approve: {approve}
- Reject: {reject}
- Abstain: {abstain}
- Consensus: {consensus}

Individual Votes:
{votes_summary}

As Zeus, provide a comprehensive final decision including:
1. The official outcome
2. Key factors that influenced the decision
3. Any conditions or modifications
4. Next steps for implementation (if approved) or feedback (if rejected)""")
        ])

        votes_summary = "\n".join([
            f"- {v.agent_name}: {v.decision.value} (confidence: {v.confidence:.2f})"
            for v in result.votes
        ])

        messages = decision_prompt.format_messages(
            title=proposal.title,
            description=proposal.description,
            approve=result.approve_votes,
            reject=result.reject_votes,
            abstain=result.abstain_votes,
            consensus="Yes" if result.consensus_reached else "No",
            votes_summary=votes_summary,
        )

        response = await self._llm.ainvoke(messages)

        # Update result with final reasoning
        result.final_reasoning = response.content

        return {
            **state,
            "result": result,
            "current_phase": "decision_complete",
            "messages": state["messages"] + [response],
        }

    def _parse_vote_decision(self, content: str) -> VoteDecision:
        """Parse vote decision from response content."""
        content_lower = content.lower()
        if "approve" in content_lower:
            return VoteDecision.APPROVE
        elif "reject" in content_lower:
            return VoteDecision.REJECT
        elif "defer" in content_lower:
            return VoteDecision.DEFER
        return VoteDecision.ABSTAIN

    def _parse_confidence(self, content: str) -> float:
        """Parse confidence score from response content."""
        import re

        # Look for patterns like "confidence: 0.8" or "0.85 confidence"
        patterns = [
            r"confidence[:\s]+([0-9]*\.?[0-9]+)",
            r"([0-9]*\.?[0-9]+)\s*confidence",
        ]

        for pattern in patterns:
            match = re.search(pattern, content.lower())
            if match:
                try:
                    value = float(match.group(1))
                    return min(max(value, 0.0), 1.0)
                except ValueError:
                    pass

        return 0.5  # Default confidence

    @traced(name="zeus_process_proposal")
    async def process_proposal(self, proposal: Proposal) -> VotingResult:
        """
        Process a proposal through the full Pentarchy voting workflow.

        Args:
            proposal: The proposal to evaluate

        Returns:
            VotingResult with the outcome and all details
        """
        initial_state: ZeusState = {
            "messages": [SystemMessage(content=self.SYSTEM_PROMPT)],
            "proposal": proposal,
            "votes": [],
            "current_phase": "initialized",
            "analysis_complete": False,
            "votes_collected": False,
            "result": None,
            "iteration": 0,
        }

        logger.info(f"Processing proposal {proposal.id}: {proposal.title}")

        # Run the graph
        final_state = await self._graph.ainvoke(initial_state)

        logger.info(
            f"Proposal {proposal.id} complete: {final_state['result'].outcome.value}"
        )

        return final_state["result"]

    async def quick_evaluate(self, question: str) -> str:
        """
        Quick evaluation without full voting process.
        Useful for simple queries or status checks.
        """
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=question),
        ]

        response = await self._llm.ainvoke(messages)
        return response.content


# Convenience function for creating Zeus instances
def create_zeus_agent(
    provider: str = "openai",
    model: str | None = None,
) -> ZeusLangGraphAgent:
    """Create a configured Zeus agent instance."""
    return ZeusLangGraphAgent(
        llm_provider=provider,
        model_name=model,
    )
