"""
MCP (Model Context Protocol) Integrations for KOSMOS.
"""

from .server import BaseMCPServer
from .filesystem_server import FilesystemServer
from .memory_server import MemoryServer
from .web_search_server import WebSearchServer
from .client import (
    MCPClient,
    MCPServer,
    MCPTool,
    MCPServerStatus,
    get_mcp_client,
    initialize_default_servers,
)
from .stubs import (
    TrivyMCP,
    ZitadelMCP,
    PgVectorMCP,
    CalendarMCP,
    SlackMCP,
    EmailMCP,
    SMSMCP,
)

__all__ = [
    "BaseMCPServer",
    "FilesystemServer",
    "MemoryServer",
    "WebSearchServer",
    "MCPClient",
    "MCPServer",
    "MCPTool",
    "MCPServerStatus",
    "get_mcp_client",
    "initialize_default_servers",
    # Stub implementations
    "TrivyMCP",
    "ZitadelMCP",
    "PgVectorMCP",
    "CalendarMCP",
    "SlackMCP",
    "EmailMCP",
    "SMSMCP",
]
