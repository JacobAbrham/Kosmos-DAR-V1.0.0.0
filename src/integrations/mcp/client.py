"""
MCP (Model Context Protocol) Client Library.
Manages connections to MCP servers and provides unified tool access.
"""
import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import aiohttp
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class MCPServerStatus(str, Enum):
    """Status of an MCP server."""
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    CONNECTING = "connecting"
    DISCONNECTED = "disconnected"


@dataclass
class MCPTool:
    """Represents a tool exposed by an MCP server."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    server_id: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "server_id": self.server_id,
        }


@dataclass
class MCPServer:
    """Configuration for an MCP server."""
    id: str
    name: str
    url: str
    transport: str = "stdio"  # stdio, http, websocket
    command: Optional[str] = None  # For stdio transport
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    tools: List[MCPTool] = field(default_factory=list)
    status: MCPServerStatus = MCPServerStatus.UNKNOWN
    last_health_check: Optional[datetime] = None
    error_message: Optional[str] = None


class MCPTransport(ABC):
    """Abstract base class for MCP transports."""

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the server."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the connection."""
        pass

    @abstractmethod
    async def send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request and wait for response."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the server is healthy."""
        pass


class HTTPTransport(MCPTransport):
    """HTTP-based MCP transport."""

    def __init__(self, url: str, timeout: int = 30):
        self.url = url
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None

    async def connect(self) -> bool:
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return await self.health_check()

    async def disconnect(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    async def send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if not self.session:
            raise RuntimeError("Not connected")

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params,
        }

        async with self.session.post(self.url, json=payload) as response:
            response.raise_for_status()
            result = await response.json()

            if "error" in result:
                raise Exception(f"MCP error: {result['error']}")

            return result.get("result", {})

    async def health_check(self) -> bool:
        try:
            if not self.session:
                return False
            async with self.session.get(f"{self.url}/health") as response:
                return response.status == 200
        except Exception:
            return False


class MCPClient:
    """
    Client for managing multiple MCP server connections.
    Provides unified access to tools across all connected servers.
    """

    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.transports: Dict[str, MCPTransport] = {}
        self._tool_cache: Dict[str, MCPTool] = {}
        self._health_check_interval = 30  # seconds
        self._health_check_task: Optional[asyncio.Task] = None

    async def register_server(self, server: MCPServer) -> bool:
        """Register and connect to an MCP server."""
        logger.info(f"Registering MCP server: {server.id} ({server.name})")

        self.servers[server.id] = server
        server.status = MCPServerStatus.CONNECTING

        try:
            # Create appropriate transport
            if server.transport == "http":
                transport = HTTPTransport(server.url)
            else:
                # Default to mock transport for now
                transport = MockTransport(server.id)

            self.transports[server.id] = transport

            # Connect
            if await transport.connect():
                server.status = MCPServerStatus.HEALTHY
                server.last_health_check = datetime.utcnow()

                # Discover tools
                await self._discover_tools(server.id)

                logger.info(
                    f"MCP server {server.id} connected with {len(server.tools)} tools")
                return True
            else:
                server.status = MCPServerStatus.UNHEALTHY
                server.error_message = "Connection failed"
                return False

        except Exception as e:
            logger.error(f"Failed to connect to MCP server {server.id}: {e}")
            server.status = MCPServerStatus.UNHEALTHY
            server.error_message = str(e)
            return False

    async def unregister_server(self, server_id: str) -> None:
        """Disconnect and remove an MCP server."""
        if server_id in self.transports:
            await self.transports[server_id].disconnect()
            del self.transports[server_id]

        if server_id in self.servers:
            # Remove tools from cache
            for tool in self.servers[server_id].tools:
                self._tool_cache.pop(f"{server_id}:{tool.name}", None)
            del self.servers[server_id]

    async def _discover_tools(self, server_id: str) -> List[MCPTool]:
        """Discover available tools from a server."""
        transport = self.transports.get(server_id)
        if not transport:
            return []

        try:
            result = await transport.send_request("tools/list", {})
            tools = []

            for tool_data in result.get("tools", []):
                tool = MCPTool(
                    name=tool_data["name"],
                    description=tool_data.get("description", ""),
                    input_schema=tool_data.get("inputSchema", {}),
                    server_id=server_id,
                )
                tools.append(tool)
                self._tool_cache[f"{server_id}:{tool.name}"] = tool

            self.servers[server_id].tools = tools
            return tools

        except Exception as e:
            logger.error(f"Failed to discover tools from {server_id}: {e}")
            return []

    def get_all_tools(self) -> List[MCPTool]:
        """Get all available tools across all servers."""
        return list(self._tool_cache.values())

    def get_tool(self, server_id: str, tool_name: str) -> Optional[MCPTool]:
        """Get a specific tool."""
        return self._tool_cache.get(f"{server_id}:{tool_name}")

    def find_tools(self, query: str) -> List[MCPTool]:
        """Find tools matching a query string."""
        query = query.lower()
        return [
            tool for tool in self._tool_cache.values()
            if query in tool.name.lower() or query in tool.description.lower()
        ]

    async def invoke_tool(
        self,
        server_id: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Invoke a tool on a specific server."""
        transport = self.transports.get(server_id)
        if not transport:
            raise ValueError(f"Server {server_id} not connected")

        tool = self.get_tool(server_id, tool_name)
        if not tool:
            raise ValueError(
                f"Tool {tool_name} not found on server {server_id}")

        logger.info(f"Invoking tool {tool_name} on {server_id}")

        try:
            result = await transport.send_request("tools/call", {
                "name": tool_name,
                "arguments": arguments,
            })
            return result

        except Exception as e:
            logger.error(f"Tool invocation failed: {e}")
            raise

    async def health_check_all(self) -> Dict[str, MCPServerStatus]:
        """Check health of all registered servers."""
        results = {}

        for server_id, transport in self.transports.items():
            try:
                is_healthy = await transport.health_check()
                status = MCPServerStatus.HEALTHY if is_healthy else MCPServerStatus.UNHEALTHY
                self.servers[server_id].status = status
                self.servers[server_id].last_health_check = datetime.utcnow()
                results[server_id] = status
            except Exception as e:
                self.servers[server_id].status = MCPServerStatus.UNHEALTHY
                self.servers[server_id].error_message = str(e)
                results[server_id] = MCPServerStatus.UNHEALTHY

        return results

    def get_server_status(self) -> List[Dict[str, Any]]:
        """Get status of all registered servers."""
        return [
            {
                "id": server.id,
                "name": server.name,
                "status": server.status.value,
                "tools_count": len(server.tools),
                "last_health_check": server.last_health_check.isoformat() if server.last_health_check else None,
                "error": server.error_message,
            }
            for server in self.servers.values()
        ]

    async def start_health_monitoring(self) -> None:
        """Start background health check task."""
        async def monitor():
            while True:
                await asyncio.sleep(self._health_check_interval)
                await self.health_check_all()

        self._health_check_task = asyncio.create_task(monitor())

    async def stop_health_monitoring(self) -> None:
        """Stop background health check task."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass


class MockTransport(MCPTransport):
    """Mock transport for testing and development."""

    MOCK_TOOLS = {
        "filesystem": [
            {"name": "read_file", "description": "Read contents of a file", "inputSchema": {
                "type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
            {"name": "write_file", "description": "Write contents to a file", "inputSchema": {"type": "object", "properties": {
                "path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}},
            {"name": "list_directory", "description": "List directory contents", "inputSchema": {
                "type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
        ],
        "memory": [
            {"name": "store", "description": "Store a value in memory", "inputSchema": {"type": "object", "properties": {
                "key": {"type": "string"}, "value": {"type": "string"}}, "required": ["key", "value"]}},
            {"name": "retrieve", "description": "Retrieve a value from memory", "inputSchema": {
                "type": "object", "properties": {"key": {"type": "string"}}, "required": ["key"]}},
            {"name": "list_keys", "description": "List all stored keys",
                "inputSchema": {"type": "object", "properties": {}}},
        ],
        "sequential-thinking": [
            {"name": "think", "description": "Process a thought step", "inputSchema": {"type": "object", "properties": {
                "thought": {"type": "string"}, "step": {"type": "integer"}}, "required": ["thought"]}},
            {"name": "conclude", "description": "Conclude the thinking process", "inputSchema": {
                "type": "object", "properties": {"summary": {"type": "string"}}, "required": ["summary"]}},
        ],
        "web-search": [
            {"name": "search", "description": "Search the web", "inputSchema": {"type": "object", "properties": {
                "query": {"type": "string"}, "max_results": {"type": "integer"}}, "required": ["query"]}},
            {"name": "fetch_page", "description": "Fetch a web page", "inputSchema": {
                "type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
        ],
        "time": [
            {"name": "get_current_time", "description": "Get current time", "inputSchema": {
                "type": "object", "properties": {"timezone": {"type": "string"}}}},
            {"name": "schedule_reminder", "description": "Schedule a reminder", "inputSchema": {"type": "object",
                                                                                                "properties": {"message": {"type": "string"}, "at": {"type": "string"}}, "required": ["message", "at"]}},
        ],
    }

    def __init__(self, server_id: str):
        self.server_id = server_id
        self.connected = False
        self._memory: Dict[str, str] = {}

    async def connect(self) -> bool:
        self.connected = True
        return True

    async def disconnect(self) -> None:
        self.connected = False

    async def send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if not self.connected:
            raise RuntimeError("Not connected")

        if method == "tools/list":
            tools = self.MOCK_TOOLS.get(self.server_id, [])
            return {"tools": tools}

        elif method == "tools/call":
            return await self._handle_tool_call(params)

        return {}

    async def _handle_tool_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle mock tool invocations."""
        tool_name = params.get("name", "")
        args = params.get("arguments", {})

        # Mock responses
        if tool_name == "read_file":
            return {"content": f"Mock content of {args.get('path', 'unknown')}"}
        elif tool_name == "store":
            self._memory[args["key"]] = args["value"]
            return {"status": "stored"}
        elif tool_name == "retrieve":
            return {"value": self._memory.get(args["key"], None)}
        elif tool_name == "search":
            return {"results": [{"title": f"Result for {args['query']}", "url": "https://example.com"}]}
        elif tool_name == "get_current_time":
            return {"time": datetime.utcnow().isoformat()}
        elif tool_name == "think":
            return {"thought_id": f"thought-{args.get('step', 1)}", "processed": True}

        return {"status": "ok"}

    async def health_check(self) -> bool:
        return self.connected


# Global client instance
_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """Get or create the global MCP client."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client


async def initialize_default_servers() -> MCPClient:
    """Initialize MCP client with default servers."""
    client = get_mcp_client()

    # Register default MCP servers
    default_servers = [
        MCPServer(id="filesystem", name="Filesystem",
                  url="", transport="mock"),
        MCPServer(id="memory", name="Memory", url="", transport="mock"),
        MCPServer(id="sequential-thinking",
                  name="Sequential Thinking", url="", transport="mock"),
        MCPServer(id="web-search", name="Web Search",
                  url="", transport="mock"),
        MCPServer(id="time", name="Time & Scheduling",
                  url="", transport="mock"),
    ]

    for server in default_servers:
        await client.register_server(server)

    return client
