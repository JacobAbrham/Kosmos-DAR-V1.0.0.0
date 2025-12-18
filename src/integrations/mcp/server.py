import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

class BaseMCPServer:
    """
    Base class for KOSMOS MCP Servers using FastMCP.
    """
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.mcp = FastMCP(name)
        self._register_tools()

    def _register_tools(self):
        """
        Override this method to register tools with self.mcp.tool()
        """
        pass

    def run(self):
        """
        Run the MCP server.
        """
        logger.info(f"Starting {self.name} MCP Server v{self.version}")
        self.mcp.run()

if __name__ == "__main__":
    # Example usage
    server = BaseMCPServer("base-server")
    server.run()
