import asyncio
import sys
import os
import logging
from contextlib import AsyncExitStack
from typing import Optional, Any, Dict, List

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger("mcp-client")


class AgentClient:
    """
    A client to connect to a local MCP agent running as a subprocess.
    """

    def __init__(self, agent_name: str, script_path: str):
        self.agent_name = agent_name
        self.script_path = script_path
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect(self):
        """Connect to the agent via stdio."""
        logger.info(
            f"Connecting to agent {self.agent_name} at {self.script_path}...")

        # Ensure PYTHONPATH includes the workspace root
        env = os.environ.copy()
        workspace_root = os.getcwd()
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = f"{workspace_root}:{env['PYTHONPATH']}"
        else:
            env["PYTHONPATH"] = workspace_root

        server_params = StdioServerParameters(
            command=sys.executable,
            args=[self.script_path],
            env=env
        )

        try:
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            self.read, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(ClientSession(self.read, self.write))
            await self.session.initialize()
            logger.info(f"Connected to {self.agent_name}")
        except Exception as e:
            logger.error(f"Failed to connect to {self.agent_name}: {e}")
            raise

    async def list_tools(self):
        if not self.session:
            raise RuntimeError(f"Not connected to agent {self.agent_name}")
        return await self.session.list_tools()

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]):
        if not self.session:
            raise RuntimeError(f"Not connected to agent {self.agent_name}")
        return await self.session.call_tool(tool_name, arguments)

    async def close(self):
        logger.info(f"Closing connection to {self.agent_name}")
        await self.exit_stack.aclose()
