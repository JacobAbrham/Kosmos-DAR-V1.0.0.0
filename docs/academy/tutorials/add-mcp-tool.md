# Adding a Custom MCP Tool

## Overview

Learn how to add custom Model Context Protocol (MCP) tools to enhance agent capabilities.

## Prerequisites

- Understanding of MCP protocol
- Experience with tool development
- Knowledge of KOSMOS agent architecture

## Steps

### 1. Define Tool Interface

```python
from mcp import Tool
from typing import Dict, Any

class MyCustomTool(Tool):
    name = "my_custom_tool"
    description = "Description of what this tool does"

    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        # Implement tool logic
        return {"result": "tool output"}
```

### 2. Register Tool

Add the tool to the MCP server configuration.

### 3. Test Tool Integration

Verify the tool works with agents that use it.

## Best Practices

- Provide clear tool descriptions
- Handle errors gracefully
- Include comprehensive tests

## Next Steps

- [Debugging Agent Interactions](debugging.md)
- [Customizing Governance Logic](governance-logic.md)