import asyncio
import logging
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("iris-agent")

# --- Data Models ---

class ComponentRequest(BaseModel):
    component_type: str
    data: Dict[str, Any]

class ChartRequest(BaseModel):
    chart_type: str
    data: List[Dict[str, Any]]
    options: Optional[Dict[str, Any]] = None

class TemplateRequest(BaseModel):
    template_name: str
    context: Dict[str, Any]

class ConversionRequest(BaseModel):
    content: str
    source_format: str
    target_format: str

class RenderResult(BaseModel):
    content: str
    format: str
    metadata: Optional[Dict[str, Any]] = None

# --- Agent Implementation ---

class IrisAgent:
    def __init__(self):
        self.name = "iris"
        self.version = "1.0.0"
        self.mcp = FastMCP(self.name)
        logger.info(f"Initializing {self.name} Agent v{self.version}")
        
        # Register tools
        self.mcp.tool()(self.render_component)
        self.mcp.tool()(self.create_chart)
        self.mcp.tool()(self.render_template)
        self.mcp.tool()(self.convert_format)

    async def render_component(self, request: ComponentRequest) -> RenderResult:
        logger.info(f"Rendering component: {request.component_type}")
        # Mock rendering
        return RenderResult(
            content=f"<div class='{request.component_type}'>{request.data}</div>",
            format="html"
        )

    async def create_chart(self, request: ChartRequest) -> RenderResult:
        logger.info(f"Creating {request.chart_type} chart")
        # Mock chart generation
        return RenderResult(
            content=f"[Chart: {request.chart_type} with {len(request.data)} points]",
            format="image/png"
        )

    async def render_template(self, request: TemplateRequest) -> RenderResult:
        logger.info(f"Rendering template: {request.template_name}")
        # Mock template rendering
        return RenderResult(
            content=f"Rendered {request.template_name} with context keys: {list(request.context.keys())}",
            format="text"
        )

    async def convert_format(self, request: ConversionRequest) -> RenderResult:
        logger.info(f"Converting from {request.source_format} to {request.target_format}")
        return RenderResult(
            content=f"Converted content ({request.target_format})",
            format=request.target_format
        )
    
    def run(self):
        """Start the Iris MCP server."""
        self.mcp.run()

# --- Entry Point ---

if __name__ == "__main__":
    agent = IrisAgent()
    agent.run()
