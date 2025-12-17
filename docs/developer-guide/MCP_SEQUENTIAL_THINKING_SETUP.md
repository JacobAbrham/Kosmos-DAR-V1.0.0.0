# Sequential Thinking MCP Server Setup Guide

This guide documents the setup and usage of the Sequential Thinking MCP server for the Kosmos documentation project.

## Overview

The Sequential Thinking MCP server provides a tool for dynamic and reflective problem-solving through a structured thinking process. It enables breaking down complex problems into manageable steps with the ability to revise and refine thoughts as understanding deepens.

## Installation

### Configuration

The Sequential Thinking server has been added to `blackbox_mcp_settings.json`:

```json
{
  "mcpServers": {
    "github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sequential-thinking"
      ]
    }
  }
}
```

### Server Details

- **Package**: `@modelcontextprotocol/server-sequential-thinking`
- **Repository**: https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking
- **Installation Method**: NPX (no local installation required)

## Features

The Sequential Thinking server provides the following capabilities:

1. **Step-by-Step Problem Solving**: Break down complex problems into clear, manageable steps
2. **Dynamic Thought Adjustment**: Adjust the total number of thoughts needed as understanding evolves
3. **Thought Revision**: Revise and refine previous thoughts when new insights emerge
4. **Alternative Reasoning Paths**: Branch into alternative paths of reasoning
5. **Context Maintenance**: Maintain context across multiple thinking steps
6. **Hypothesis Generation**: Generate and verify solution hypotheses

## Available Tools

### sequential_thinking

Facilitates a detailed, step-by-step thinking process for problem-solving and analysis.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `thought` | string | Yes | The current thinking step |
| `nextThoughtNeeded` | boolean | Yes | Whether another thought step is needed |
| `thoughtNumber` | integer | Yes | Current thought number |
| `totalThoughts` | integer | Yes | Estimated total thoughts needed |
| `isRevision` | boolean | No | Whether this revises previous thinking |
| `revisesThought` | integer | No | Which thought is being reconsidered |
| `branchFromThought` | integer | No | Branching point thought number |
| `branchId` | string | No | Branch identifier |
| `needsMoreThoughts` | boolean | No | If more thoughts are needed than initially estimated |

## Use Cases

The Sequential Thinking tool is ideal for:

- **Complex Problem Decomposition**: Breaking down architectural decisions, system designs, or technical challenges
- **Planning and Design**: Creating detailed plans with room for revision and refinement
- **Analysis with Course Correction**: Situations where initial assumptions may need adjustment
- **Scope Discovery**: Problems where the full scope isn't clear initially
- **Context-Heavy Tasks**: Tasks requiring maintained context over multiple steps
- **Information Filtering**: Situations where irrelevant information needs to be filtered out

## Demonstration

A comprehensive demonstration script is available at `test_sequential_thinking.js`. This script showcases:

- Breaking down a complex microservices architecture design
- Dynamic adjustment of thought count
- Revision of previous thinking
- Structured problem-solving process
- Context maintenance across steps

### Running the Demonstration

```bash
node test_sequential_thinking.js
```

The demonstration solves a real-world problem: designing a scalable microservices architecture. It shows how the tool:

1. Analyzes the problem initially
2. Breaks down service components
3. Considers communication patterns
4. Revises data management strategy
5. Plans deployment approach
6. Synthesizes the final architecture

## Example Usage

### Basic Sequential Thinking

```javascript
const step1 = await client.callTool({
  name: 'sequential_thinking',
  arguments: {
    thought: 'First, I need to understand the problem requirements...',
    nextThoughtNeeded: true,
    thoughtNumber: 1,
    totalThoughts: 5
  }
});
```

### Revising Previous Thoughts

```javascript
const revision = await client.callTool({
  name: 'sequential_thinking',
  arguments: {
    thought: 'Actually, I need to reconsider my previous approach...',
    nextThoughtNeeded: true,
    thoughtNumber: 3,
    totalThoughts: 5,
    isRevision: true,
    revisesThought: 2
  }
});
```

### Adjusting Thought Count

```javascript
const adjustment = await client.callTool({
  name: 'sequential_thinking',
  arguments: {
    thought: 'This problem is more complex than initially thought...',
    nextThoughtNeeded: true,
    thoughtNumber: 4,
    totalThoughts: 7,
    needsMoreThoughts: true
  }
});
```

### Branching Reasoning

```javascript
const branch = await client.callTool({
  name: 'sequential_thinking',
  arguments: {
    thought: 'Let me explore an alternative approach...',
    nextThoughtNeeded: true,
    thoughtNumber: 5,
    totalThoughts: 8,
    branchFromThought: 3,
    branchId: 'alternative-approach-a'
  }
});
```

## Integration with Kosmos Documentation

The Sequential Thinking server can be particularly useful for:

1. **Architecture Decision Records (ADRs)**: Breaking down complex architectural decisions into structured reasoning
2. **Model Card Development**: Systematically analyzing model capabilities, limitations, and ethical considerations
3. **Incident Response Planning**: Developing step-by-step response procedures with revision capabilities
4. **Risk Analysis**: Methodically evaluating risks with the ability to adjust as new information emerges
5. **Documentation Planning**: Structuring complex documentation topics with iterative refinement

## Configuration Options

### Disabling Thought Logging

To disable logging of thought information, set the environment variable:

```bash
DISABLE_THOUGHT_LOGGING=true
```

This can be useful in production environments where you want to reduce log verbosity.

## Troubleshooting

### Server Not Starting

If the server fails to start:

1. Ensure Node.js is installed (version 16 or higher)
2. Check that npx is available: `npx --version`
3. Verify network connectivity for package download
4. Check the console for error messages

### Tool Not Available

If the `sequential_thinking` tool is not available:

1. Verify the server is properly configured in `blackbox_mcp_settings.json`
2. Restart the MCP client
3. Check server logs for initialization errors

### Unexpected Responses

If you receive unexpected responses:

1. Ensure all required parameters are provided
2. Verify `thoughtNumber` is sequential
3. Check that `totalThoughts` is reasonable for the problem
4. Review the thought content for clarity

## Best Practices

1. **Start with Clear Problem Statement**: Begin with a well-defined problem in the first thought
2. **Estimate Thoughts Conservatively**: Start with a reasonable estimate and adjust as needed
3. **Use Revisions Thoughtfully**: Revise when new insights genuinely change understanding
4. **Maintain Context**: Each thought should build on previous thoughts
5. **Branch Strategically**: Use branching for genuinely alternative approaches
6. **End Decisively**: Set `nextThoughtNeeded: false` when the problem is solved

## Resources

- **Official Repository**: https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking
- **MCP Documentation**: https://modelcontextprotocol.io
- **Package on NPM**: https://www.npmjs.com/package/@modelcontextprotocol/server-sequential-thinking

## Version History

- **Initial Setup**: Sequential Thinking MCP server configured and demonstrated
- **Configuration File**: Added to `blackbox_mcp_settings.json`
- **Demonstration Script**: Created `test_sequential_thinking.js`
- **Documentation**: Created this setup guide

## Next Steps

1. Run the demonstration script to verify the setup
2. Integrate sequential thinking into documentation workflows
3. Use for complex ADR development
4. Apply to incident response planning
5. Leverage for model card analysis

---

*Last Updated: 2025*
*Maintained by: Kosmos Documentation Team*
