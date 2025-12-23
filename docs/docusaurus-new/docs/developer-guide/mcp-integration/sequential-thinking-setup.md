# Sequential Thinking MCP Setup

**Multi-Step Reasoning for Complex Problem Solving**

---

## Overview

The Sequential Thinking MCP server provides structured, step-by-step reasoning capabilities for complex problem solving. Used primarily by Zeus for task decomposition, planning, and multi-step workflows.

### Server Details

| Property | Value |
|----------|-------|
| Server Name | `sequential-thinking` |
| Package | `@modelcontextprotocol/server-sequential-thinking` |
| Primary Agent | Zeus |
| Status | Active |

---

## Configuration

### MCP Settings

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_SEQUENTIAL_THINKING_ENABLED` | Enable/disable server | `true` |
| `MCP_SEQUENTIAL_THINKING_TIMEOUT_MS` | Request timeout | `60000` |

---

## Key Features

1. **Step-by-Step Problem Solving** - Break down complex problems into manageable steps
2. **Dynamic Thought Adjustment** - Adjust total thoughts as understanding evolves
3. **Thought Revision** - Revise and refine previous thoughts
4. **Alternative Reasoning Paths** - Branch into alternative reasoning paths
5. **Context Maintenance** - Maintain context across multiple thinking steps

---

## Available Tools

### sequential_thinking

Facilitates detailed, step-by-step thinking for problem-solving and analysis.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `thought` | string | Yes | Current thinking step |
| `nextThoughtNeeded` | boolean | Yes | Whether another step is needed |
| `thoughtNumber` | integer | Yes | Current thought number |
| `totalThoughts` | integer | Yes | Estimated total thoughts |
| `isRevision` | boolean | No | Revises previous thinking |
| `revisesThought` | integer | No | Which thought is reconsidered |
| `branchFromThought` | integer | No | Branching point |
| `branchId` | string | No | Branch identifier |
| `needsMoreThoughts` | boolean | No | More thoughts needed than estimated |

---

## Usage Examples

### Basic Sequential Thinking

```python
async def think_step_by_step(problem: str) -> list[str]:
    """Use sequential thinking for problem decomposition."""
    client = await get_mcp_client("sequential-thinking")
    thoughts = []
    
    # Step 1: Initial analysis
    result = await client.call_tool(
        "sequential_thinking",
        {
            "thought": f"Analyzing problem: {problem}",
            "nextThoughtNeeded": True,
            "thoughtNumber": 1,
            "totalThoughts": 5
        }
    )
    thoughts.append(result)
    
    # Continue steps...
    step = 2
    while result.get("nextThoughtNeeded"):
        result = await client.call_tool(
            "sequential_thinking",
            {
                "thought": generate_next_thought(thoughts),
                "nextThoughtNeeded": step < result["totalThoughts"],
                "thoughtNumber": step,
                "totalThoughts": result["totalThoughts"]
            }
        )
        thoughts.append(result)
        step += 1
    
    return thoughts
```

### Revising Previous Thoughts

```python
# Revise step 2 based on new understanding
revision = await client.call_tool(
    "sequential_thinking",
    {
        "thought": "Reconsidering the data model approach...",
        "nextThoughtNeeded": True,
        "thoughtNumber": 4,
        "totalThoughts": 6,
        "isRevision": True,
        "revisesThought": 2
    }
)
```

### Branching Reasoning

```python
# Branch into alternative approach
branch = await client.call_tool(
    "sequential_thinking",
    {
        "thought": "Exploring alternative microservices design...",
        "nextThoughtNeeded": True,
        "thoughtNumber": 1,
        "totalThoughts": 3,
        "branchFromThought": 3,
        "branchId": "alternative-1"
    }
)
```

---

## Integration with Zeus

Zeus uses sequential thinking for complex task orchestration:

```python
class ZeusOrchestrator(BaseAgent):
    async def plan_complex_task(
        self,
        task: str,
        context: dict
    ) -> TaskPlan:
        """Plan complex multi-agent task."""
        client = self.mcp_clients["sequential-thinking"]
        
        # Decompose task
        thoughts = []
        thought_num = 1
        total_thoughts = 5  # Initial estimate
        
        # Initial analysis
        result = await client.call_tool(
            "sequential_thinking",
            {
                "thought": f"Analyzing task: {task}. Context: {context}",
                "nextThoughtNeeded": True,
                "thoughtNumber": thought_num,
                "totalThoughts": total_thoughts
            }
        )
        thoughts.append(result)
        
        # Continue planning
        while result.get("nextThoughtNeeded"):
            thought_num += 1
            
            # Adjust total if needed
            if result.get("needsMoreThoughts"):
                total_thoughts = result["totalThoughts"]
            
            result = await client.call_tool(
                "sequential_thinking",
                {
                    "thought": self._generate_next_thought(thoughts, task),
                    "nextThoughtNeeded": thought_num < total_thoughts,
                    "thoughtNumber": thought_num,
                    "totalThoughts": total_thoughts
                }
            )
            thoughts.append(result)
        
        return self._thoughts_to_plan(thoughts)
```

---

## Use Cases

| Use Case | Example |
|----------|---------|
| Task Decomposition | Breaking "implement feature X" into subtasks |
| Architecture Planning | Designing system components and interactions |
| Problem Analysis | Understanding complex user requirements |
| Decision Making | Evaluating options with structured reasoning |
| Debugging | Step-by-step diagnosis of issues |

---

## Thinking Patterns

### Linear Thinking

```
Step 1 → Step 2 → Step 3 → Step 4 → Conclusion
```

### Iterative Refinement

```
Step 1 → Step 2 → Revise 1 → Step 3 → Revise 2 → Conclusion
```

### Branching Exploration

```
Step 1 → Step 2 → Branch A → A1 → A2
                ↘ Branch B → B1 → B2
                   Merge → Conclusion
```

---

## Troubleshooting

### Long Thinking Chains

If thinking takes too long:
- Set reasonable `totalThoughts` limits
- Use early termination conditions
- Consider breaking into sub-problems

### Thought Loops

If revisions create loops:
- Track revision history
- Limit revision depth
- Force progression after N revisions

### Context Loss

If context is lost between steps:
- Include relevant context in each thought
- Use summary thoughts periodically
- Persist state to memory server

---

## Testing

Test script available:

```bash
node test_sequential_thinking.js
```

Demonstrates:
- Multi-step architecture design
- Dynamic thought adjustment
- Revision capability
- Context maintenance

---

**Last Updated:** 2025-12-12  
**Document Owner:** Engineering Team
