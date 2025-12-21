from typing import Dict, Any, List, Optional
from fastmcp import FastMCP
from pydantic import BaseModel, Field
import asyncio
import json
import re
import logging

from src.services.llm_service import get_llm_service, Message as LLMMessage

logger = logging.getLogger("hestia-agent")


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


class Preference(BaseModel):
    key: str = Field(..., description="The preference key")
    value: Any = Field(..., description="The preference value")
    category: str = Field("general", description="Category of the preference")


class HabitLog(BaseModel):
    habit_type: str = Field(...,
                            description="Type of habit (e.g., 'coding', 'reading')")
    duration_minutes: int = Field(..., description="Duration in minutes")
    notes: Optional[str] = Field(None, description="Optional notes")


class PlaylistRequest(BaseModel):
    mood: str = Field(..., description="Target mood for the playlist")
    duration_minutes: int = Field(30, description="Target duration in minutes")
    genres: List[str] = Field(default_factory=list,
                              description="Preferred genres")


class HestiaAgent:
    """
    HESTIA: Personal & Media Agent
    Responsible for user preferences, personalization, UI adaptation, and media management.
    """

    def __init__(self):
        self.name = "hestia"
        self.version = "2.0.0"
        self.mcp = FastMCP(self.name)
        self.llm = get_llm_service()
        self.system_prompt = """You are HESTIA, the Personal & Media Agent in the KOSMOS Pentarchy.
Your domain: User preferences, personalization, UI adaptation, media curation, wellness.
When evaluating proposals, assess:
1. User experience and personalization impact
2. Privacy and preference considerations
3. Media and content implications
4. User wellness and engagement factors

For Pentarchy votes, respond with JSON: {"vote": "APPROVE/REJECT/ABSTAIN", "score": 0-3, "reasoning": ["reason1", "reason2"]}"""
        self.preferences_store: Dict[str, Any] = {}
        self.habit_logs: List[Dict[str, Any]] = []
        logger.info(f"Initializing {self.name} Agent v{self.version}")

        # Register tools
        self.mcp.tool()(self.process_query)
        self.mcp.tool()(self.get_preferences)
        self.mcp.tool()(self.set_preference)
        self.mcp.tool()(self.adapt_ui)
        self.mcp.tool()(self.track_habit)
        self.mcp.tool()(self.curate_playlist)
        self.mcp.tool()(self.enable_focus_mode)
        self.mcp.tool()(self.evaluate_proposal)

    async def process_query(self, query: str, conversation_id: str = "") -> str:
        """Process a personalization/media-related query using LLM."""
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
        return f"HESTIA: Personalization analysis for '{query}' - mock response"

    async def evaluate_proposal(self, request: ProposalEvaluationRequest) -> PentarchyVote:
        """Evaluate a proposal from user/personalization perspective for Pentarchy voting."""
        logger.info(
            f"Evaluating proposal {request.proposal_id} for user impact")

        if self.llm:
            try:
                prompt = f"""Evaluate this proposal from a USER/PERSONALIZATION perspective:
Proposal ID: {request.proposal_id}
Cost: ${request.cost}
Description: {request.description}

Consider: user experience, privacy, preferences, wellness, engagement.
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
        return PentarchyVote(vote="APPROVE", score=2, reasoning=["User experience positive", "Privacy preserved"])

    async def get_preferences(self, category: str = "general") -> Dict[str, Any]:
        """Retrieve user preferences for a specific category."""
        # In a real implementation, this would query a database (PostgreSQL)
        return {k: v for k, v in self.preferences_store.items() if k.startswith(f"{category}.")}

    async def set_preference(self, key: str, value: Any, category: str = "general") -> str:
        """Update a user preference."""
        full_key = f"{category}.{key}"
        self.preferences_store[full_key] = value
        return f"Preference '{full_key}' set to '{value}'"

    async def adapt_ui(self, context: str) -> Dict[str, Any]:
        """Generate UI adaptation settings based on context."""
        # Mock logic for UI adaptation
        if context == "night":
            return {"theme": "dark", "contrast": "high", "font_size": "medium"}
        elif context == "focus":
            return {"theme": "minimal", "notifications": "muted", "sidebar": "collapsed"}
        return {"theme": "system", "layout": "standard"}

    async def track_habit(self, habit: HabitLog) -> str:
        """Record a habit activity."""
        self.habit_logs.append(habit.model_dump())
        return f"Logged {habit.duration_minutes} minutes of {habit.habit_type}"

    async def curate_playlist(self, request: PlaylistRequest) -> List[str]:
        """Generate a music playlist based on mood and preferences."""
        # Mock logic for playlist generation
        return [
            f"Song for {request.mood} - Track 1 ({request.genres[0] if request.genres else 'Pop'})",
            f"Song for {request.mood} - Track 2 ({request.genres[0] if request.genres else 'Pop'})",
            f"Song for {request.mood} - Track 3 (Ambient)"
        ]

    async def enable_focus_mode(self, duration_minutes: int = 25, mode_type: str = "pomodoro") -> str:
        """Enable distraction-free focus mode."""
        # In a real implementation, this would trigger system-level DND and UI changes
        return f"Focus mode '{mode_type}' enabled for {duration_minutes} minutes. Distractions minimized."

    def run(self):
        """Start the Hestia MCP server."""
        self.mcp.run()


if __name__ == "__main__":
    agent = HestiaAgent()
    agent.run()
