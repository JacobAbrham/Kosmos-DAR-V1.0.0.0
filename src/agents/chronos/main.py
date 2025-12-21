import asyncio
import logging
import json
import re
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from fastmcp import FastMCP

from src.services.llm_service import get_llm_service, Message as LLMMessage

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("chronos-agent")


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


class MeetingRequest(BaseModel):
    title: str
    attendees: List[str]
    duration_minutes: int
    start_time: Optional[datetime] = None
    description: Optional[str] = None


class AvailabilityRequest(BaseModel):
    attendees: List[str]
    duration_minutes: int
    start_range: datetime
    end_range: datetime


class ReminderRequest(BaseModel):
    message: str
    trigger_time: datetime
    user_id: str


class CalendarQuery(BaseModel):
    user_id: str
    start_time: datetime
    end_time: datetime


class CalendarEvent(BaseModel):
    event_id: str
    title: str
    start: datetime
    end: datetime
    attendees: List[str]
    status: str

# --- Agent Implementation ---


class ChronosAgent:
    def __init__(self):
        self.name = "chronos"
        self.version = "2.0.0"
        self.mcp = FastMCP(self.name)
        self.llm = get_llm_service()
        self.system_prompt = """You are CHRONOS, the Scheduling & Time Agent in the KOSMOS Pentarchy.
Your domain: Calendar management, scheduling, reminders, time-based coordination.
When evaluating proposals, assess:
1. Timeline feasibility and deadline alignment
2. Resource scheduling conflicts
3. Calendar dependencies and constraints
4. Time-based risk factors

For Pentarchy votes, respond with JSON: {"vote": "APPROVE/REJECT/ABSTAIN", "score": 0-3, "reasoning": ["reason1", "reason2"]}"""
        logger.info(f"Initializing {self.name} Agent v{self.version}")

        # Register tools
        self.mcp.tool()(self.process_query)
        self.mcp.tool()(self.schedule_meeting)
        self.mcp.tool()(self.find_availability)
        self.mcp.tool()(self.set_reminder)
        self.mcp.tool()(self.get_calendar)
        self.mcp.tool()(self.evaluate_proposal)

    async def process_query(self, query: str, conversation_id: str = "") -> str:
        """Process a time/scheduling-related query using LLM."""
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
        return f"CHRONOS: Schedule analysis for '{query}' - mock response"

    async def evaluate_proposal(self, request: ProposalEvaluationRequest) -> PentarchyVote:
        """Evaluate a proposal from scheduling perspective for Pentarchy voting."""
        logger.info(
            f"Evaluating proposal {request.proposal_id} for scheduling")

        if self.llm:
            try:
                prompt = f"""Evaluate this proposal from a SCHEDULING/TIME perspective:
Proposal ID: {request.proposal_id}
Cost: ${request.cost}
Description: {request.description}

Consider: timeline feasibility, resource scheduling, calendar conflicts, deadlines.
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
        return PentarchyVote(vote="APPROVE", score=2, reasoning=["Timeline feasible", "No scheduling conflicts"])

    async def schedule_meeting(self, request: MeetingRequest) -> CalendarEvent:
        logger.info(
            f"Scheduling meeting '{request.title}' for {request.attendees}")
        # TODO: Integrate with calendar-mcp

        start = request.start_time or datetime.now() + timedelta(hours=1)
        end = start + timedelta(minutes=request.duration_minutes)

        return CalendarEvent(
            event_id=f"evt-{datetime.now().timestamp()}",
            title=request.title,
            start=start,
            end=end,
            attendees=request.attendees,
            status="confirmed"
        )

    async def find_availability(self, request: AvailabilityRequest) -> List[datetime]:
        logger.info(
            f"Finding availability for {request.attendees} between {request.start_range} and {request.end_range}")
        # Mock: Return 3 slots
        base_time = request.start_range
        return [
            base_time + timedelta(hours=10),
            base_time + timedelta(hours=14),
            base_time + timedelta(days=1, hours=10)
        ]

    async def set_reminder(self, request: ReminderRequest) -> Dict[str, Any]:
        logger.info(
            f"Setting reminder for {request.user_id} at {request.trigger_time}: {request.message}")
        return {
            "reminder_id": f"rem-{datetime.now().timestamp()}",
            "status": "scheduled",
            "trigger_time": request.trigger_time
        }

    async def get_calendar(self, query: CalendarQuery) -> List[CalendarEvent]:
        logger.info(f"Fetching calendar for {query.user_id}")
        # Mock events
        return [
            CalendarEvent(
                event_id="evt-1",
                title="Daily Standup",
                start=query.start_time + timedelta(hours=9),
                end=query.start_time + timedelta(hours=9, minutes=30),
                attendees=["team@kosmos.ai"],
                status="confirmed"
            )
        ]

    def run(self):
        """Start the Chronos MCP server."""
        self.mcp.run()

# --- Entry Point ---


if __name__ == "__main__":
    agent = ChronosAgent()
    agent.run()
