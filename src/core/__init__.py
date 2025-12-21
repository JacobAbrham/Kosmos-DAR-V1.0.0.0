"""
KOSMOS Core Module - Agent Registry and MCP Client.
"""

from .agent_registry import AGENT_REGISTRY, get_agent_path
from .mcp_client import AgentClient

__all__ = [
    "AGENT_REGISTRY",
    "get_agent_path",
    "AgentClient",
]
