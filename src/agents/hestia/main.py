from typing import Dict, Any, List, Optional
from fastmcp import FastMCP
from pydantic import BaseModel, Field
import asyncio
import json

# Define data models
class Preference(BaseModel):
    key: str = Field(..., description="The preference key")
    value: Any = Field(..., description="The preference value")
    category: str = Field("general", description="Category of the preference")

class HabitLog(BaseModel):
    habit_type: str = Field(..., description="Type of habit (e.g., 'coding', 'reading')")
    duration_minutes: int = Field(..., description="Duration in minutes")
    notes: Optional[str] = Field(None, description="Optional notes")

class PlaylistRequest(BaseModel):
    mood: str = Field(..., description="Target mood for the playlist")
    duration_minutes: int = Field(30, description="Target duration in minutes")
    genres: List[str] = Field(default_factory=list, description="Preferred genres")

class HestiaAgent:
    """
    HESTIA: Personal & Media Agent
    Responsible for user preferences, personalization, UI adaptation, and media management.
    """
    
    def __init__(self):
        self.name = "hestia"
        self.mcp = FastMCP(self.name)
        self.preferences_store: Dict[str, Any] = {}
        self.habit_logs: List[Dict[str, Any]] = []
        
        # Register tools
        self.mcp.tool()(self.get_preferences)
        self.mcp.tool()(self.set_preference)
        self.mcp.tool()(self.adapt_ui)
        self.mcp.tool()(self.track_habit)
        self.mcp.tool()(self.curate_playlist)
        self.mcp.tool()(self.enable_focus_mode)

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
