# MCP Custom Server Development

**Last Updated:** 2025-12-13

## Overview

Guide for developing custom Model Context Protocol (MCP) servers for KOSMOS.

## MCP Server Basics

An MCP server provides tools, resources, and prompts that can be consumed by AI agents through a standardized protocol.

### Server Components

1. **Tools:** Functions that agents can invoke
2. **Resources:** Data sources that agents can query
3. **Prompts:** Reusable prompt templates

## Quick Start

### TypeScript MCP Server

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

// Create server instance
const server = new Server(
  {
    name: "kosmos-custom-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
      resources: {},
    },
  }
);

// Define tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "search_knowledge_base",
        description: "Search the KOSMOS knowledge base",
        inputSchema: {
          type: "object",
          properties: {
            query: {
              type: "string",
              description: "Search query",
            },
            limit: {
              type: "number",
              description: "Maximum results",
              default: 10,
            },
          },
          required: ["query"],
        },
      },
    ],
  };
});

// Implement tool execution
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "search_knowledge_base") {
    const { query, limit = 10 } = request.params.arguments as {
      query: string;
      limit?: number;
    };

    // Implement search logic
    const results = await searchKnowledgeBase(query, limit);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(results, null, 2),
        },
      ],
    };
  }

  throw new Error(`Unknown tool: ${request.params.name}`);
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("KOSMOS Custom MCP Server running");
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
```

### Python MCP Server

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio

# Create server
app = Server("kosmos-custom-server")

# Define tool
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="analyze_sentiment",
            description="Analyze sentiment of text",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to analyze"
                    }
                },
                "required": ["text"]
            }
        )
    ]

# Implement tool
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "analyze_sentiment":
        text = arguments["text"]
        
        # Implement sentiment analysis
        sentiment = analyze_sentiment(text)
        
        return [
            TextContent(
                type="text",
                text=f"Sentiment: {sentiment}"
            )
        ]
    
    raise ValueError(f"Unknown tool: {name}")

# Run server
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())
```

## Adding Resources

```typescript
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: [
      {
        uri: "kosmos://docs/governance",
        name: "Governance Documentation",
        description: "KOSMOS governance policies",
        mimeType: "text/plain",
      },
    ],
  };
});

server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const uri = request.params.uri;
  
  if (uri === "kosmos://docs/governance") {
    const content = await loadGovernanceDocs();
    return {
      contents: [
        {
          uri,
          mimeType: "text/plain",
          text: content,
        },
      ],
    };
  }
  
  throw new Error(`Resource not found: ${uri}`);
});
```

## Packaging and Distribution

### package.json
```json
{
  "name": "@kosmos/mcp-custom-server",
  "version": "1.0.0",
  "type": "module",
  "bin": {
    "kosmos-custom-server": "./dist/index.js"
  },
  "files": ["dist"],
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.5.0"
  },
  "scripts": {
    "build": "tsc",
    "prepare": "npm run build"
  }
}
```

### Publishing
```bash
# Build
npm run build

# Test locally
npx -y . arg1 arg2

# Publish
npm publish --access public
```

## Configuration

Add to MCP settings:
```json
{
  "mcpServers": {
    "kosmos-custom": {
      "command": "npx",
      "args": ["-y", "@kosmos/mcp-custom-server"]
    }
  }
}
```

## Best Practices

1. **Error Handling:** Always validate inputs and handle errors gracefully
2. **Logging:** Use structured logging for debugging
3. **Security:** Validate and sanitize all inputs
4. **Performance:** Implement caching where appropriate
5. **Documentation:** Document all tools, resources, and prompts
6. **Versioning:** Use semantic versioning
7. **Testing:** Write unit tests for all tools

## Testing

```typescript
import { describe, it, expect } from "vitest";

describe("search_knowledge_base", () => {
  it("should return results for valid query", async () => {
    const result = await callTool({
      name: "search_knowledge_base",
      arguments: { query: "governance" },
    });
    
    expect(result.content).toBeDefined();
    expect(result.content[0].type).toBe("text");
  });
});
```

## Related Documentation

- [MCP Integration](README)
- [Memory Server Setup](../MCP_MEMORY_SERVER_SETUP)
- [Sequential Thinking Setup](../MCP_SEQUENTIAL_THINKING_SETUP)
