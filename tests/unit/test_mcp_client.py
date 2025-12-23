"""
Unit tests for the MCP client.
Tests server management, tool discovery, and transport handling.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from src.integrations.mcp.client import (
    MCPServerStatus,
    MCPTool,
    MCPServer,
    MCPTransport,
    HTTPTransport,
)


class TestMCPServerStatus:
    """Tests for MCPServerStatus enum."""

    def test_all_statuses_defined(self):
        """All expected statuses should be defined."""
        assert MCPServerStatus.UNKNOWN.value == "unknown"
        assert MCPServerStatus.HEALTHY.value == "healthy"
        assert MCPServerStatus.UNHEALTHY.value == "unhealthy"
        assert MCPServerStatus.CONNECTING.value == "connecting"
        assert MCPServerStatus.DISCONNECTED.value == "disconnected"


class TestMCPTool:
    """Tests for MCPTool dataclass."""

    def test_tool_creation(self):
        """Should create tool with all fields."""
        tool = MCPTool(
            name="search",
            description="Search for documents",
            input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
            server_id="athena-server"
        )
        assert tool.name == "search"
        assert tool.description == "Search for documents"
        assert tool.server_id == "athena-server"
        assert "query" in tool.input_schema["properties"]

    def test_tool_to_dict(self):
        """Should convert tool to dictionary."""
        tool = MCPTool(
            name="search",
            description="Search docs",
            input_schema={"type": "object"},
            server_id="server-1"
        )
        result = tool.to_dict()
        assert result["name"] == "search"
        assert result["description"] == "Search docs"
        assert result["server_id"] == "server-1"


class TestMCPServer:
    """Tests for MCPServer dataclass."""

    def test_server_creation_minimal(self):
        """Should create server with minimal fields."""
        server = MCPServer(
            id="test-server",
            name="Test Server",
            url="http://localhost:8080"
        )
        assert server.id == "test-server"
        assert server.name == "Test Server"
        assert server.url == "http://localhost:8080"
        assert server.transport == "stdio"  # default
        assert server.status == MCPServerStatus.UNKNOWN

    def test_server_creation_full(self):
        """Should create server with all fields."""
        server = MCPServer(
            id="full-server",
            name="Full Server",
            url="http://localhost:9000",
            transport="http",
            command="/usr/bin/server",
            args=["--port", "9000"],
            env={"DEBUG": "true"},
            status=MCPServerStatus.HEALTHY,
            last_health_check=datetime.now(),
        )
        assert server.transport == "http"
        assert server.command == "/usr/bin/server"
        assert server.args == ["--port", "9000"]
        assert server.env["DEBUG"] == "true"
        assert server.status == MCPServerStatus.HEALTHY

    def test_server_tools_default_empty(self):
        """Server tools should default to empty list."""
        server = MCPServer(
            id="test",
            name="Test",
            url="http://localhost"
        )
        assert server.tools == []

    def test_server_with_tools(self):
        """Should support server with tools."""
        tool = MCPTool(
            name="test-tool",
            description="A test tool",
            input_schema={},
            server_id="test"
        )
        server = MCPServer(
            id="test",
            name="Test",
            url="http://localhost",
            tools=[tool]
        )
        assert len(server.tools) == 1
        assert server.tools[0].name == "test-tool"


class TestHTTPTransport:
    """Tests for HTTPTransport class."""

    def test_transport_initialization(self):
        """Should initialize with URL and timeout."""
        transport = HTTPTransport(
            url="http://localhost:8080",
            timeout=60
        )
        assert transport.url == "http://localhost:8080"
        assert transport.timeout == 60
        assert transport.session is None

    def test_transport_default_timeout(self):
        """Should use default timeout of 30 seconds."""
        transport = HTTPTransport(url="http://localhost")
        assert transport.timeout == 30

    @pytest.mark.asyncio
    async def test_connect_creates_session(self):
        """Connect should create an aiohttp session."""
        transport = HTTPTransport(url="http://localhost:8080")
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value = MagicMock()
            mock_session.return_value.get = AsyncMock(return_value=MagicMock(status=200))
            
            # Mock health check to return True
            transport.health_check = AsyncMock(return_value=True)
            
            result = await transport.connect()
            assert result is True

    @pytest.mark.asyncio
    async def test_disconnect_closes_session(self):
        """Disconnect should close the session."""
        transport = HTTPTransport(url="http://localhost")
        
        mock_session = MagicMock()
        mock_session.close = AsyncMock()
        transport.session = mock_session
        
        await transport.disconnect()
        mock_session.close.assert_called_once()


class TestMCPServerConfiguration:
    """Tests for MCP server configuration patterns."""

    def test_stdio_transport_config(self):
        """Should configure stdio transport correctly."""
        server = MCPServer(
            id="local-server",
            name="Local MCP Server",
            url="stdio://",
            transport="stdio",
            command="python",
            args=["-m", "mcp_server"],
            env={"MCP_MODE": "stdio"}
        )
        assert server.transport == "stdio"
        assert server.command == "python"

    def test_http_transport_config(self):
        """Should configure HTTP transport correctly."""
        server = MCPServer(
            id="remote-server",
            name="Remote MCP Server",
            url="https://mcp.example.com",
            transport="http"
        )
        assert server.transport == "http"
        assert server.url.startswith("https://")

    def test_websocket_transport_config(self):
        """Should configure WebSocket transport correctly."""
        server = MCPServer(
            id="ws-server",
            name="WebSocket Server",
            url="wss://mcp.example.com/ws",
            transport="websocket"
        )
        assert server.transport == "websocket"
        assert server.url.startswith("wss://")


class TestServerStatusTransitions:
    """Tests for server status state transitions."""

    def test_initial_status_unknown(self):
        """New servers should start with UNKNOWN status."""
        server = MCPServer(id="new", name="New", url="http://localhost")
        assert server.status == MCPServerStatus.UNKNOWN

    def test_status_can_be_set(self):
        """Server status should be settable."""
        server = MCPServer(id="test", name="Test", url="http://localhost")
        server.status = MCPServerStatus.CONNECTING
        assert server.status == MCPServerStatus.CONNECTING

    def test_error_message_on_unhealthy(self):
        """Unhealthy servers can have error messages."""
        server = MCPServer(
            id="sick",
            name="Sick Server",
            url="http://localhost",
            status=MCPServerStatus.UNHEALTHY,
            error_message="Connection refused"
        )
        assert server.status == MCPServerStatus.UNHEALTHY
        assert server.error_message == "Connection refused"
