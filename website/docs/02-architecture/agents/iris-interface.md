# Iris Interface Agent

**Domain:** User Interface, Visualization & Presentation  
**Greek Deity:** Iris - Goddess of the Rainbow  
**Status:** Active  
**Version:** 1.0.0

---

## Overview

Iris is the **interface and visualization** agent, responsible for rendering UI components, data visualization, and presentation formatting. Named after the goddess who bridges heaven and earth, Iris connects KOSMOS capabilities to user-facing interfaces.

### Key Capabilities

- **Component Rendering** - Generate UI components
- **Data Visualization** - Create charts and graphs
- **Format Conversion** - Convert between formats
- **Template Rendering** - Render dynamic templates
- **Accessibility** - Ensure accessible output

### Supported Actions

| Action | Description | Required Params |
|--------|-------------|-----------------|
| `render_component` | Generate UI component | `component_type`, `data` |
| `create_chart` | Generate visualization | `chart_type`, `data`, `options` |
| `render_template` | Render Jinja template | `template`, `context` |
| `convert_format` | Convert output format | `content`, `source_format`, `target_format` |
| `generate_report` | Create formatted report | `report_type`, `data` |

### MCP Connections

| MCP Server | Purpose |
|------------|---------|
| ui-components-mcp | Component library |

---

**Last Updated:** 2025-12-12


## Auto-Detected Tools

| Tool Name | Status | Source |
|-----------|--------|--------|
| `convert_format` | Active | `src/agents/iris/main.py` |
| `create_chart` | Active | `src/agents/iris/main.py` |
| `evaluate_proposal` | Active | `src/agents/iris/main.py` |
| `process_query` | Active | `src/agents/iris/main.py` |
| `render_component` | Active | `src/agents/iris/main.py` |
| `render_template` | Active | `src/agents/iris/main.py` |
