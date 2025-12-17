# Hephaestus Tooling Agent

**Domain:** Tool Creation, Code Operations & Build Management  
**Greek Deity:** Hephaestus - God of Fire and Forge  
**Status:** Active  
**Version:** 1.0.0

---

## Overview

Hephaestus is the **tooling and creation** agent, responsible for code generation, file operations, and build management. Named after the divine craftsman, Hephaestus creates and manages tools that other agents and users need.

### Key Capabilities

- **Code Generation** - Generate code from specifications
- **File Operations** - Read, write, modify files
- **Build Management** - Trigger and monitor builds
- **Tool Registration** - Register new MCP tools
- **Script Execution** - Run approved scripts

### Supported Actions

| Action | Description | Required Params |
|--------|-------------|-----------------|
| `generate_code` | Create code from spec | `spec`, `language` |
| `read_file` | Read file contents | `path` |
| `write_file` | Write file contents | `path`, `content` |
| `run_build` | Trigger build pipeline | `project`, `branch` |
| `execute_script` | Run approved script | `script_id`, `params` |

### MCP Connections

| MCP Server | Purpose |
|------------|---------|
| filesystem-mcp | File system operations |
| github-mcp | Repository operations |

---

**Last Updated:** 2025-12-12
