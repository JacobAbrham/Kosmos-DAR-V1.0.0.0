# Context7 MCP Server Setup Guide

## Overview

The Context7 MCP (Model Context Protocol) server has been successfully configured to provide up-to-date code documentation and library information directly to your AI coding assistant.

## Configuration

The server is configured in `blackbox_mcp_settings.json` with the following details:

```json
"github.com/upstash/context7-mcp": {
  "command": "npx",
  "args": [
    "-y",
    "@upstash/context7-mcp"
  ]
}
```

## Server Details

- **Server Name**: `github.com/upstash/context7-mcp`
- **Package**: `@upstash/context7-mcp`
- **Installation Method**: Automatic via `npx` (will install if not present)
- **Node.js Requirement**: >= v18.0.0 (Current: v25.2.1 ✅)

## Available Tools

The Context7 MCP server provides two main tools:

### 1. `resolve-library-id`
Resolves a general library name into a Context7-compatible library ID.

**Parameters:**
- `libraryName` (required): The name of the library to search for

**Example Usage:**
- Input: `"react"`
- Output: `{ libraryID: "/facebook/react", confidence: 0.95 }`

### 2. `get-library-docs`
Fetches documentation for a library using a Context7-compatible library ID.

**Parameters:**
- `context7CompatibleLibraryID` (required): Exact library ID (e.g., "/facebook/react")
- `topic` (optional): Focus the docs on a specific topic (e.g., "hooks", "routing")
- `page` (optional): Page number for pagination (1-10)

## How to Use

### Method 1: Explicit Invocation
Add `use context7` to your coding prompts:

```
Create a Next.js middleware that checks for a valid JWT in cookies
and redirects unauthenticated users to /login. use context7
```

### Method 2: Library-Specific Invocation
Use the library ID directly if you know it:

```
Implement basic authentication with Supabase. use library /supabase/supabase for API and docs.
```

### Method 3: Automatic Rules (Recommended)
Configure your MCP client to automatically invoke Context7 for code-related questions. Add a rule like:

```
Always use context7 when I need code generation, setup or configuration steps, or
library/API documentation. This means you should automatically use the Context7 MCP
tools to resolve library id and get library docs without me having to explicitly ask.
```

## Benefits

- ✅ **No outdated code examples**: Gets documentation directly from source
- ✅ **No hallucinated APIs**: Only real, existing APIs are documented
- ✅ **Version-specific documentation**: Accurate for current library versions
- ✅ **Direct from source**: Code examples come from actual library source code

## Supported Clients

The Context7 MCP server works with any MCP-compatible client including:
- Cursor
- Claude Code
- VS Code
- Windsurf
- And many others...

## Testing

A test script `test_context7.js` is available to demonstrate the server's capabilities:

```bash
node test_context7.js
```

## Troubleshooting

1. **Server not starting**: Ensure Node.js v18+ is installed
2. **Installation issues**: The server uses `npx` which automatically handles installation
3. **Network issues**: The server may require internet access to fetch documentation

## Additional Resources

- [Context7 Official Website](https://context7.com)
- [GitHub Repository](https://github.com/upstash/context7-mcp)
- [MCP Documentation](https://modelcontextprotocol.io)

## Version Information

- **Context7 MCP Package**: `@upstash/context7-mcp` (latest)
- **Node.js Version**: v25.2.1 ✅
- **Configuration Status**: ✅ Successfully configured
