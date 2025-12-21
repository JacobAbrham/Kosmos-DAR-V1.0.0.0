"""
MCP API Router - Endpoints for managing MCP servers and tools.
"""
import logging
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from src.integrations.mcp.client import (
    get_mcp_client,
    MCPClient,
    MCPServer,
    MCPServerStatus,
    initialize_default_servers,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp", tags=["mcp"])


# Request/Response Models
class ServerRegistration(BaseModel):
    """Request to register a new MCP server."""
    id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    url: str = Field(default="")
    transport: str = Field(
        default="mock", pattern="^(http|stdio|websocket|mock)$")
    command: Optional[str] = None
    args: List[str] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)


class ServerStatus(BaseModel):
    """MCP server status response."""
    id: str
    name: str
    status: str
    tools_count: int
    last_health_check: Optional[str]
    error: Optional[str]


class ToolInfo(BaseModel):
    """Tool information."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    server_id: str


class ToolInvocation(BaseModel):
    """Request to invoke a tool."""
    arguments: Dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    """Tool invocation result."""
    server_id: str
    tool_name: str
    result: Dict[str, Any]
    success: bool
    error: Optional[str] = None


# Dependency
async def get_client() -> MCPClient:
    """Get the MCP client, initializing if needed."""
    client = get_mcp_client()
    if not client.servers:
        await initialize_default_servers()
    return client


@router.get("/servers", response_model=List[ServerStatus])
async def list_servers(client: MCPClient = Depends(get_client)):
    """List all registered MCP servers."""
    return client.get_server_status()


@router.post("/servers", response_model=ServerStatus)
async def register_server(
    registration: ServerRegistration,
    client: MCPClient = Depends(get_client),
):
    """Register a new MCP server."""
    if registration.id in client.servers:
        raise HTTPException(
            status_code=409, detail=f"Server {registration.id} already registered")

    server = MCPServer(
        id=registration.id,
        name=registration.name,
        url=registration.url,
        transport=registration.transport,
        command=registration.command,
        args=registration.args,
        env=registration.env,
    )

    success = await client.register_server(server)

    if not success:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to server: {server.error_message}"
        )

    status = client.get_server_status()
    return next(s for s in status if s["id"] == registration.id)


@router.delete("/servers/{server_id}")
async def unregister_server(
    server_id: str,
    client: MCPClient = Depends(get_client),
):
    """Unregister an MCP server."""
    if server_id not in client.servers:
        raise HTTPException(
            status_code=404, detail=f"Server {server_id} not found")

    await client.unregister_server(server_id)
    return {"status": "unregistered", "server_id": server_id}


@router.get("/servers/{server_id}/health")
async def check_server_health(
    server_id: str,
    client: MCPClient = Depends(get_client),
):
    """Check health of a specific server."""
    if server_id not in client.servers:
        raise HTTPException(
            status_code=404, detail=f"Server {server_id} not found")

    results = await client.health_check_all()
    status = results.get(server_id, MCPServerStatus.UNKNOWN)

    return {
        "server_id": server_id,
        "status": status.value,
        "healthy": status == MCPServerStatus.HEALTHY,
    }


@router.get("/tools", response_model=List[ToolInfo])
async def list_tools(
    server_id: Optional[str] = None,
    query: Optional[str] = None,
    client: MCPClient = Depends(get_client),
):
    """List available tools, optionally filtered by server or query."""
    if query:
        tools = client.find_tools(query)
    elif server_id:
        if server_id not in client.servers:
            raise HTTPException(
                status_code=404, detail=f"Server {server_id} not found")
        tools = client.servers[server_id].tools
    else:
        tools = client.get_all_tools()

    return [tool.to_dict() for tool in tools]


@router.get("/tools/{server_id}/{tool_name}", response_model=ToolInfo)
async def get_tool(
    server_id: str,
    tool_name: str,
    client: MCPClient = Depends(get_client),
):
    """Get details of a specific tool."""
    tool = client.get_tool(server_id, tool_name)
    if not tool:
        raise HTTPException(
            status_code=404,
            detail=f"Tool {tool_name} not found on server {server_id}"
        )
    return tool.to_dict()


@router.post("/tools/{server_id}/{tool_name}/invoke", response_model=ToolResult)
async def invoke_tool(
    server_id: str,
    tool_name: str,
    invocation: ToolInvocation,
    client: MCPClient = Depends(get_client),
):
    """Invoke a tool on a specific server."""
    try:
        result = await client.invoke_tool(server_id, tool_name, invocation.arguments)
        return ToolResult(
            server_id=server_id,
            tool_name=tool_name,
            result=result,
            success=True,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Tool invocation error: {e}")
        return ToolResult(
            server_id=server_id,
            tool_name=tool_name,
            result={},
            success=False,
            error=str(e),
        )


@router.post("/health")
async def health_check_all(client: MCPClient = Depends(get_client)):
    """Run health check on all servers."""
    results = await client.health_check_all()
    return {
        "servers": {
            server_id: status.value
            for server_id, status in results.items()
        },
        "healthy_count": sum(1 for s in results.values() if s == MCPServerStatus.HEALTHY),
        "total_count": len(results),
    }


@router.get("/stats")
async def get_stats(client: MCPClient = Depends(get_client)):
    """Get MCP system statistics."""
    servers = client.get_server_status()
    tools = client.get_all_tools()

    healthy = sum(1 for s in servers if s["status"] == "healthy")

    return {
        "servers": {
            "total": len(servers),
            "healthy": healthy,
            "unhealthy": len(servers) - healthy,
        },
        "tools": {
            "total": len(tools),
            "by_server": {
                server["id"]: server["tools_count"]
                for server in servers
            },
        },
    }
