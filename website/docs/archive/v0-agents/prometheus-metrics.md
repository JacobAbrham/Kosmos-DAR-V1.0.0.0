# Prometheus Metrics Agent (DEPRECATED)

:::warning Deprecated Agent
    This agent has been deprecated in KOSMOS V1.0.0. Its responsibilities have been transferred to:
    
    - **Nur PROMETHEUS** - Strategic analytics, optimization, and reporting
    - **SigNoz** - Infrastructure metrics, alerting, SLO tracking
    - **Langfuse** - LLM-specific metrics and cost tracking
    
    See [Nur PROMETHEUS Agent](../../02-architecture/agents/nur-prometheus-strategy) for the strategic analytics agent.

---

**Domain:** Metrics, Alerting & SLO Management  
**Greek Deity:** Prometheus - Titan of Forethought  
**Status:** ~~Active~~ **DEPRECATED**  
**Version:** 1.0.0  
**Deprecated In:** V1.0.0  
**Replaced By:** Nur PROMETHEUS

---

## Overview

Prometheus is the **metrics and alerting** agent, managing alert rules, SLO tracking, and metric analysis. Named after the titan who gave fire to humanity, Prometheus provides the insights needed for proactive system management.

### Key Capabilities

- **Alert Management** - Create, silence, acknowledge alerts
- **SLO Tracking** - Monitor service level objectives
- **Metric Queries** - Execute PromQL queries
- **Threshold Management** - Configure alert thresholds
- **Anomaly Detection** - Identify metric anomalies

### Supported Actions

| Action | Description | Required Params |
|--------|-------------|-----------------|
| `list_alerts` | Get active alerts | `severity`, `service` |
| `silence_alert` | Silence an alert | `alert_id`, `duration` |
| `query_metrics` | Run PromQL query | `query`, `time_range` |
| `get_slo_status` | Check SLO compliance | `slo_name` |
| `create_alert_rule` | Create alert rule | `rule_spec` |

### MCP Connections

| MCP Server | Purpose |
|------------|---------|
| alertmanager-mcp | Alert management |

---

## Deprecation Rationale

The original Prometheus agent was narrowly focused on infrastructure metrics. In V1.0.0:

1. **Infrastructure metrics** moved to SigNoz (unified observability platform)
2. **LLM cost/performance** moved to Langfuse (LLM observability)
3. **Strategic analytics** elevated to **Nur PROMETHEUS** agent

The new **Nur PROMETHEUS** ("Light of Prometheus") agent focuses on:
- Strategic planning and trend prediction
- Data analysis and recommendation generation
- System-wide optimization insights
- Financial analytics and portfolio analysis (holding company features)
- ESG reporting and subsidiary benchmarking

This represents an evolution from operational metrics to strategic intelligence.

---

**Last Updated:** 2025-12-12  
**Archived:** 2025-12-13
