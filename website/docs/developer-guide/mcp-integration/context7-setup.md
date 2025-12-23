# Context7 MCP Server Setup

**External Documentation Lookup for KOSMOS Agents**

---

## Overview

The Context7 MCP server provides up-to-date code documentation and library information directly to KOSMOS agents, primarily used by Athena for knowledge retrieval about external libraries and frameworks.

### Server Details

| Property | Value |
|----------|-------|
| Server Name | `context7-mcp` |
| Package | `@upstash/context7-mcp` |
| Primary Agent | Athena |
| Status | Active |

---

## Configuration

### MCP Settings

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_CONTEXT7_ENABLED` | Enable/disable server | `true` |
| `MCP_CONTEXT7_TIMEOUT_MS` | Request timeout | `30000` |

---

## Available Tools

### 1. resolve-library-id

Resolves a general library name into a Context7-compatible library ID.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `libraryName` | string | Yes | Library name to search |

**Example:**

```python
result = await client.call_tool(
    "resolve-library-id",
    {"libraryName": "react"}
)
# Returns: {"libraryID": "/facebook/react", "confidence": 0.95}
```

### 2. get-library-docs

Fetches documentation for a library using its Context7-compatible ID.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `context7CompatibleLibraryID` | string | Yes | Library ID (e.g., "/facebook/react") |
| `topic` | string | No | Focus topic (e.g., "hooks") |
| `page` | integer | No | Page number (1-10) |

**Example:**

```python
result = await client.call_tool(
    "get-library-docs",
    {
        "context7CompatibleLibraryID": "/facebook/react",
        "topic": "hooks"
    }
)
```

---

## Integration with Athena

Athena uses Context7 for external library documentation:

```python
class AthenaAgent(BaseAgent):
    async def get_external_docs(
        self,
        library: str,
        topic: str = None
    ) -> Documentation:
        """Retrieve external library documentation."""
        # Resolve library ID
        client = self.mcp_clients["context7"]
        lib_info = await client.call_tool(
            "resolve-library-id",
            {"libraryName": library}
        )
        
        # Get documentation
        docs = await client.call_tool(
            "get-library-docs",
            {
                "context7CompatibleLibraryID": lib_info["libraryID"],
                "topic": topic
            }
        )
        
        return self._parse_docs(docs)
```

---

## Benefits

- **No outdated examples** - Documentation fetched from source
- **No hallucinated APIs** - Only real, existing APIs documented
- **Version-specific** - Accurate for current library versions
- **Direct from source** - Code examples from actual library code

---

## Troubleshooting

### Server Not Starting

```bash
# Check Node.js version (requires v18+)
node --version

# Test npx availability
npx --version

# Manual server test
npx -y @upstash/context7-mcp
```

### Connection Issues

```python
# Test connection
async with MCPClient("context7") as client:
    tools = await client.list_tools()
    print(f"Connected, {len(tools)} tools available")
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ECONNREFUSED` | Server not running | Start MCP server |
| `Timeout` | Slow network | Increase timeout |
| `LibraryNotFound` | Unknown library | Check library name |

---

## Testing

Test script available:

```bash
node test_context7.js
```

Expected output:
- Tool list verification
- Library resolution test
- Documentation retrieval test

---

## Resources

- [Context7 Official Website](https://context7.com)
- [GitHub Repository](https://github.com/upstash/context7-mcp)
- [MCP Protocol Documentation](https://modelcontextprotocol.io)

---

**Last Updated:** 2025-12-12  
**Document Owner:** Engineering Team
