# Creating a New Agent

## Overview

This tutorial guides you through creating a new agent in the KOSMOS system.

## Prerequisites

- Basic understanding of Python
- Familiarity with FastAPI
- Knowledge of the KOSMOS architecture

## Steps

### 1. Define Agent Requirements

Before creating an agent, identify:
- What problem does it solve?
- What capabilities does it need?
- How does it integrate with other agents?

### 2. Create Agent Structure

```python
from kosmos.agents.base import BaseAgent
from kosmos.core.types import AgentConfig

class MyNewAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        # Initialize agent-specific components

    async def process_request(self, request: AgentRequest) -> AgentResponse:
        # Implement agent logic here
        pass
```

### 3. Register Agent

Add your agent to the agent registry in `src/agents/registry.py`.

### 4. Test Agent

Create unit tests and integration tests for your agent.

## Next Steps

- [Adding a Custom MCP Tool](add-mcp-tool.md)
- [Debugging Agent Interactions](debugging.md)