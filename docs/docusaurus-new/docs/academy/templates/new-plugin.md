# Tutorial: Integrating a New Plugin/MCP

**Target Audience:** Developers
**Prerequisites:** Python 3.11, Docker

## Overview
This tutorial guides you through adding a new capability to KOSMOS via a new MCP (Model Context Protocol) server or plugin.

## Step 1: Define the Interface
Describe what your plugin does.

```python
# src/integrations/mcp/my_new_plugin.py
from fastmcp import FastMCP

mcp = FastMCP("my-plugin")

@mcp.tool()
def my_tool(arg1: str) -> str:
    """Description of what the tool does."""
    return f"Processed {arg1}"
```

## Step 2: Register with an Agent
Add your tool to an agent's initialization in `src/agents/`<agent`>/main.py`.

```python
# Inside Agent.__init__
self.mcp.tool()(my_tool)
```

## Step 3: Update Documentation
Run the auto-documentation script to update the agent's capabilities list.

```bash
python3 scripts/auto_doc_agents.py
```

## Step 4: Test
Add a test case in `tests/integration/` to verify the agent can call your new tool.
