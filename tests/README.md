# KOSMOS Documentation Tests

This directory contains test files for validating the KOSMOS documentation repository and MCP integrations.

## Test Files

### MCP Integration Tests

| File | Description | Command |
|------|-------------|---------|
| `test_context7.js` | Context7 MCP server basic tests | `node tests/test_context7.js` |
| `test_context7_integration.js` | Context7 MCP integration tests | `node tests/test_context7_integration.js` |
| `test_memory_server.js` | Memory MCP server tests | `node tests/test_memory_server.js` |
| `test_memory_server_comprehensive.js` | Comprehensive memory server tests | `node tests/test_memory_server_comprehensive.js` |
| `test_sequential_thinking.js` | Sequential thinking MCP tests | `node tests/test_sequential_thinking.js` |

### Validation Tests

| File | Description | Command |
|------|-------------|---------|
| `validate_mcp_config.py` | MCP configuration validator | `python tests/validate_mcp_config.py` |

## Running Tests

### Prerequisites

```bash
# Python dependencies
pip install -r requirements.txt

# Node.js (for MCP tests)
node --version  # Requires Node 18+
```

### Run All Tests

```bash
# Python validation
python scripts/validate_all.py

# Individual MCP tests
node tests/test_context7.js
node tests/test_memory_server.js

# MCP config validation
python tests/validate_mcp_config.py
```

### CI/CD Integration

Tests are automatically run via GitHub Actions on:
- Push to `main` or `develop` branches
- Pull requests
- Manual workflow dispatch

See `.github/workflows/validate.yml` for the full test pipeline.

## Adding New Tests

1. Place test files in this directory
2. Follow naming convention: `test_*.js` or `test_*.py`
3. Update this README with test documentation
4. Add to CI/CD workflow if needed

## Test Coverage

| Category | Coverage |
|----------|----------|
| Schema Validation | 100% |
| YAML Validation | 100% |
| MCP Configuration | 100% |
| Documentation Links | 100% |
| Volume Structure | 100% |
