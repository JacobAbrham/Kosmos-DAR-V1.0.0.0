# Apollo Monitoring Agent (DEPRECATED)

!!! warning "Deprecated Agent"
    This agent has been deprecated in KOSMOS V1.0.0. Its responsibilities have been absorbed by:
    
    - **Nur PROMETHEUS** - Analytics, metrics, and strategic insights
    - **SigNoz** - Infrastructure observability
    - **Langfuse** - LLM-specific observability
    
    See [Nur PROMETHEUS](../../02-architecture/agents/nur-prometheus-strategy.md) for the replacement agent.

---

**Domain:** Monitoring, Dashboards & System Health  
**Greek Deity:** Apollo - God of Light and Truth  
**Status:** ~~Active~~ **DEPRECATED**  
**Version:** 1.0.0
**Deprecated In:** V1.0.0

---

## Overview

Apollo is the **monitoring and observability** agent, providing visibility into system health, dashboards, and operational status. Named after the god of truth and light, Apollo illuminates the state of all KOSMOS systems.

### Key Capabilities

- **Health Checks** - Monitor service health
- **Dashboard Queries** - Query Grafana dashboards
- **Log Analysis** - Search and analyze logs
- **Trace Inspection** - Examine distributed traces
- **Status Reports** - Generate status summaries

### Supported Actions

| Action | Description | Required Params |
|--------|-------------|-----------------|
| `check_health` | Service health check | `service_name` |
| `query_dashboard` | Get dashboard data | `dashboard_id`, `time_range` |
| `search_logs` | Search Loki logs | `query`, `time_range` |
| `get_trace` | Retrieve trace | `trace_id` |
| `status_report` | Generate status report | `scope` |

### MCP Connections

| MCP Server | Purpose |
|------------|---------|
| prometheus-mcp | Metrics queries |
| grafana-mcp | Dashboard integration |

---

## Deprecation Rationale

Apollo's functionality was too narrowly focused on infrastructure monitoring. In V1.0.0:

1. **Infrastructure monitoring** moved to SigNoz (unified observability)
2. **LLM observability** moved to Langfuse
3. **Strategic analytics** elevated to Nur PROMETHEUS agent

This consolidation reduces agent count while improving capability coverage.

---

**Last Updated:** 2025-12-12  
**Archived:** 2025-12-13
