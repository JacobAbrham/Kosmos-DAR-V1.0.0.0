# Grafana Dashboards

**Document Type:** Operations Guide  
**Owner:** SRE Team  
**Last Updated:** 2025-12-13  
**Status:** 🟢 Active

---

## Overview

KOSMOS uses Grafana for visualization, dashboards, and metric exploration. This document catalogs available dashboards, their purposes, and customization guidelines.

---

## Dashboard Catalog

### Core Dashboards

| Dashboard | UID | Purpose | Refresh |
|-----------|-----|---------|---------|
| [KOSMOS Overview](#kosmos-overview) | `kosmos-overview` | System-wide health and KPIs | 30s |
| [Agent Performance](#agent-performance) | `kosmos-agents` | Individual agent metrics | 15s |
| [LLM Analytics](#llm-analytics) | `kosmos-llm` | Token usage, costs, latency | 1m |
| [Infrastructure](#infrastructure) | `kosmos-infra` | DB, cache, queue health | 30s |
| [SLO Dashboard](#slo-dashboard) | `kosmos-slo` | Error budgets, availability | 5m |

### Operational Dashboards

| Dashboard | UID | Purpose | Refresh |
|-----------|-----|---------|---------|
| [On-Call View](#on-call-view) | `kosmos-oncall` | Alerts, incidents, runbook links | 10s |
| [Deployment Tracker](#deployment-tracker) | `kosmos-deploy` | Release tracking, canary status | 30s |
| [Cost Analytics](#cost-analytics) | `kosmos-cost` | Resource costs, projections | 1h |

---

## KOSMOS Overview

**UID:** `kosmos-overview`  
**Purpose:** Executive view of system health

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                     KOSMOS System Overview                       │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│  Availability │  Error Rate  │   Latency    │  Active Users    │
│    99.95%     │    0.02%     │   142ms p99  │     1,234        │
├──────────────┴──────────────┴──────────────┴───────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Request Rate (last 24h)                     │   │
│  │  [═══════════════════════════════════════════════════]  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
├────────────────────────────┬────────────────────────────────────┤
│     Agent Health Matrix    │         Error Distribution         │
│  Zeus      ● ● ● ● ●      │  [Pie chart of error types]        │
│  Athena    ● ● ● ● ●      │                                    │
│  Hermes    ● ● ● ● ○      │                                    │
│  Chronos   ● ● ● ● ●      │                                    │
├────────────────────────────┴────────────────────────────────────┤
│                    LLM Token Usage (24h)                        │
│  Input: 2.4M tokens  │  Output: 1.8M tokens  │  Cost: $42.50   │
└─────────────────────────────────────────────────────────────────┘
```

### Panel Definitions

```json
{
  "panels": [
    {
      "title": "Availability (30d)",
      "type": "stat",
      "targets": [
        {
          "expr": "avg_over_time(up{job=\"kosmos-agents\"}[30d]) * 100",
          "legendFormat": "Availability %"
        }
      ],
      "fieldConfig": {
        "defaults": {
          "thresholds": {
            "steps": [
              {"color": "red", "value": 99},
              {"color": "yellow", "value": 99.5},
              {"color": "green", "value": 99.9}
            ]
          },
          "unit": "percent"
        }
      }
    },
    {
      "title": "Error Rate (5m)",
      "type": "stat",
      "targets": [
        {
          "expr": "100 * sum(rate(kosmos_agent_requests_total{status=\"error\"}[5m])) / sum(rate(kosmos_agent_requests_total[5m]))",
          "legendFormat": "Error %"
        }
      ],
      "fieldConfig": {
        "defaults": {
          "thresholds": {
            "steps": [
              {"color": "green", "value": 0},
              {"color": "yellow", "value": 0.1},
              {"color": "red", "value": 1}
            ]
          },
          "unit": "percent"
        }
      }
    },
    {
      "title": "P99 Latency",
      "type": "stat",
      "targets": [
        {
          "expr": "histogram_quantile(0.99, sum(rate(kosmos_agent_request_duration_seconds_bucket[5m])) by (le)) * 1000",
          "legendFormat": "P99 ms"
        }
      ],
      "fieldConfig": {
        "defaults": {
          "thresholds": {
            "steps": [
              {"color": "green", "value": 0},
              {"color": "yellow", "value": 300},
              {"color": "red", "value": 500}
            ]
          },
          "unit": "ms"
        }
      }
    }
  ]
}
```

---

## Agent Performance

**UID:** `kosmos-agents`  
**Purpose:** Detailed agent-level metrics

### Variables

| Variable | Query | Multi-select |
|----------|-------|--------------|
| `$agent` | `label_values(kosmos_agent_requests_total, agent)` | Yes |
| `$method` | `label_values(kosmos_agent_requests_total{agent=~"$agent"}, method)` | Yes |
| `$interval` | `1m, 5m, 15m, 1h` | No |

### Key Panels

```yaml
panels:
  - title: Request Rate by Agent
    type: timeseries
    query: |
      sum(rate(kosmos_agent_requests_total{agent=~"$agent"}[$interval])) by (agent)
    legend: "{{ agent }}"

  - title: Error Rate by Agent
    type: timeseries
    query: |
      100 * sum(rate(kosmos_agent_requests_total{agent=~"$agent", status="error"}[$interval])) by (agent)
      / sum(rate(kosmos_agent_requests_total{agent=~"$agent"}[$interval])) by (agent)
    legend: "{{ agent }}"
    thresholds:
      - value: 0.1
        color: yellow
      - value: 1
        color: red

  - title: Latency Distribution
    type: heatmap
    query: |
      sum(increase(kosmos_agent_request_duration_seconds_bucket{agent=~"$agent"}[$interval])) by (le)

  - title: Latency Percentiles
    type: timeseries
    queries:
      - expr: histogram_quantile(0.50, sum(rate(kosmos_agent_request_duration_seconds_bucket{agent=~"$agent"}[$interval])) by (agent, le))
        legend: "{{ agent }} P50"
      - expr: histogram_quantile(0.95, sum(rate(kosmos_agent_request_duration_seconds_bucket{agent=~"$agent"}[$interval])) by (agent, le))
        legend: "{{ agent }} P95"
      - expr: histogram_quantile(0.99, sum(rate(kosmos_agent_request_duration_seconds_bucket{agent=~"$agent"}[$interval])) by (agent, le))
        legend: "{{ agent }} P99"

  - title: Active Sessions
    type: gauge
    query: |
      sum(kosmos_agent_active_sessions{agent=~"$agent"}) by (agent)
    max: 100

  - title: Error Breakdown
    type: piechart
    query: |
      sum(increase(kosmos_agent_errors_total{agent=~"$agent"}[24h])) by (error_type)
```

---

## LLM Analytics

**UID:** `kosmos-llm`  
**Purpose:** LLM usage, costs, and performance

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                       LLM Analytics                              │
├────────────────┬────────────────┬────────────────┬──────────────┤
│  Total Tokens  │  Input Tokens  │ Output Tokens  │  Est. Cost   │
│    4.2M        │     2.4M       │     1.8M       │    $42.50    │
├────────────────┴────────────────┴────────────────┴──────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Token Usage Over Time                       │   │
│  │  [Stacked area chart: input vs output tokens]           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Cost Projection (30 days)                   │   │
│  │  Current: $42.50/day  │  Projected: $1,275/month        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
├──────────────────────────────┬──────────────────────────────────┤
│     Latency Distribution     │        Cache Performance         │
│  [Histogram of LLM latency]  │  Hit Rate: 34%                   │
│                              │  Hits: 12,450 │ Misses: 24,120  │
├──────────────────────────────┴──────────────────────────────────┤
│                    Model Usage Breakdown                        │
│  mistral-7b: 78%  │  mixtral-8x7b: 18%  │  other: 4%           │
└─────────────────────────────────────────────────────────────────┘
```

### Key Panels

```yaml
panels:
  - title: Token Usage (24h)
    type: stat
    queries:
      - expr: sum(increase(kosmos_llm_tokens_total[24h]))
        legendFormat: Total
      - expr: sum(increase(kosmos_llm_tokens_total{direction="input"}[24h]))
        legendFormat: Input
      - expr: sum(increase(kosmos_llm_tokens_total{direction="output"}[24h]))
        legendFormat: Output

  - title: Estimated Daily Cost
    type: stat
    query: |
      sum(increase(kosmos_llm_cost_dollars_total[24h]))
    unit: currencyUSD
    thresholds:
      - value: 50
        color: green
      - value: 100
        color: yellow
      - value: 200
        color: red

  - title: Token Rate by Model
    type: timeseries
    query: |
      sum(rate(kosmos_llm_tokens_total[5m])) by (model)

  - title: LLM Latency (P99)
    type: timeseries
    query: |
      histogram_quantile(0.99, sum(rate(kosmos_llm_latency_seconds_bucket[5m])) by (model, le)) * 1000
    unit: ms

  - title: Cache Hit Ratio
    type: gauge
    query: |
      sum(rate(kosmos_llm_cache_hits_total[5m])) 
      / (sum(rate(kosmos_llm_cache_hits_total[5m])) + sum(rate(kosmos_llm_cache_misses_total[5m]))) * 100
    unit: percent
    min: 0
    max: 100
    thresholds:
      - value: 20
        color: red
      - value: 40
        color: yellow
      - value: 60
        color: green

  - title: Rate Limit Events
    type: timeseries
    query: |
      sum(increase(kosmos_llm_rate_limit_hits_total[5m])) by (provider)
```

---

## Infrastructure

**UID:** `kosmos-infra`  
**Purpose:** Database, cache, and queue health

### Key Panels

```yaml
panels:
  # PostgreSQL
  - title: Database Connections
    type: gauge
    queries:
      - expr: kosmos_db_connections_active{database="kosmos"}
        legendFormat: Active
      - expr: kosmos_db_connections_idle{database="kosmos"}
        legendFormat: Idle
    max: 100

  - title: Query Latency (P99)
    type: timeseries
    query: |
      histogram_quantile(0.99, sum(rate(kosmos_db_query_duration_seconds_bucket[5m])) by (operation, le)) * 1000
    unit: ms

  # Dragonfly Cache
  - title: Cache Hit Ratio
    type: gauge
    query: kosmos_cache_hit_ratio{cache="dragonfly"} * 100
    unit: percent
    thresholds:
      - value: 80
        color: red
      - value: 90
        color: yellow
      - value: 95
        color: green

  - title: Cache Memory Usage
    type: timeseries
    query: kosmos_cache_memory_bytes{cache="dragonfly"}
    unit: bytes

  # NATS
  - title: Queue Depth
    type: timeseries
    query: kosmos_queue_depth
    thresholds:
      - value: 100
        color: yellow
      - value: 1000
        color: red

  - title: Consumer Lag
    type: timeseries
    query: kosmos_queue_consumer_lag
    thresholds:
      - value: 10
        color: yellow
      - value: 100
        color: red

  # Storage
  - title: MinIO Storage Usage
    type: timeseries
    query: kosmos_storage_bytes_total
    unit: bytes
```

---

## SLO Dashboard

**UID:** `kosmos-slo`  
**Purpose:** SLO tracking and error budget

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                        SLO Dashboard                             │
├────────────────────────────────┬────────────────────────────────┤
│      30-Day Availability       │     Error Budget Remaining     │
│           99.95%               │           78.5%                │
│     [████████████████████░]    │     [████████████████░░░░░]    │
│        Target: 99.9%           │                                │
├────────────────────────────────┴────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           Error Budget Burn Rate (Rolling)               │   │
│  │  [Line chart showing burn rate over time]               │   │
│  │  --- 1x burn rate (sustainable)                         │   │
│  │  --- 2x burn rate (warning)                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                     SLI Breakdown by Agent                       │
│  Agent      Availability   Latency P99   Error Rate   Status   │
│  ─────────────────────────────────────────────────────────────  │
│  Zeus       99.98%         124ms         0.01%        ✅       │
│  Athena     99.95%         156ms         0.03%        ✅       │
│  Hermes     99.87%         342ms         0.08%        ⚠️       │
│  Chronos    99.99%         89ms          0.01%        ✅       │
└─────────────────────────────────────────────────────────────────┘
```

### Key Panels

```yaml
panels:
  - title: 30-Day Availability
    type: gauge
    query: avg_over_time(up{job="kosmos-agents"}[30d]) * 100
    unit: percent
    min: 99
    max: 100
    thresholds:
      - value: 99.0
        color: red
      - value: 99.5
        color: yellow
      - value: 99.9
        color: green

  - title: Error Budget Remaining
    type: gauge
    query: |
      (1 - (
        sum(increase(kosmos_agent_requests_total{status="error"}[30d]))
        / sum(increase(kosmos_agent_requests_total[30d]))
      ) / 0.001) * 100
    unit: percent
    min: 0
    max: 100
    thresholds:
      - value: 25
        color: red
      - value: 50
        color: yellow
      - value: 75
        color: green

  - title: Burn Rate
    type: timeseries
    query: |
      sum(rate(kosmos_agent_requests_total{status="error"}[1h]))
      / sum(rate(kosmos_agent_requests_total[1h]))
      / 0.001 * 720
    thresholds:
      - value: 1
        color: green
      - value: 2
        color: yellow
      - value: 10
        color: red

  - title: SLI Table
    type: table
    queries:
      - expr: avg_over_time(up{job="kosmos-agents"}[30d]) * 100
        format: table
        legendFormat: Availability
      - expr: histogram_quantile(0.99, sum(rate(kosmos_agent_request_duration_seconds_bucket[30d])) by (agent, le)) * 1000
        format: table
        legendFormat: Latency P99
```

---

## On-Call View

**UID:** `kosmos-oncall`  
**Purpose:** Streamlined view for on-call engineers

### Features

- Current active alerts with severity
- Recent deployments
- Quick links to runbooks
- Key health indicators
- Incident timeline

```yaml
panels:
  - title: Active Alerts
    type: alertlist
    options:
      showOptions:
        alertName: true
        current: true
        pending: true
        firing: true
      sortOrder: importance
      stateFilter:
        firing: true
        pending: true

  - title: Recent Deployments
    type: table
    datasource: GitHub
    query: |
      SELECT timestamp, version, status, author
      FROM deployments
      WHERE timestamp > NOW() - INTERVAL '24 hours'
      ORDER BY timestamp DESC

  - title: Runbook Links
    type: text
    content: |
      ## Quick Links
      - [Prompt Injection Response](../incident-response/prompt-injection)
      - [Model Degradation](../incident-response/model-degradation)
      - [Cost Spike](../incident-response/cost-spike)
      - [High Error Rate](../incident-response/high-error-rate)
```

---

## Deployment Tracker {#deployment-tracker}

**UID:** `kosmos-deploy`  
**Purpose:** Track releases, canary deployments, and rollback status

### Features

- Release timeline with version tags
- Canary deployment status (% traffic routing)
- Deployment health metrics
- Rollback history
- GitHub integration for commit info

```yaml
panels:
  - title: Release Timeline
    type: state-timeline
    datasource: GitHub
    query: |
      SELECT timestamp, version, environment, status
      FROM deployments
      WHERE timestamp > NOW() - INTERVAL '7 days'
      ORDER BY timestamp DESC

  - title: Canary Status
    type: gauge
    datasource: Prometheus
    query: |
      sum(kosmos_deployment_canary_traffic_percent) by (version)
    thresholds:
      - value: 0
        color: blue
      - value: 50
        color: yellow
      - value: 100
        color: green

  - title: Deployment Health
    type: timeseries
    queries:
      - expr: rate(kosmos_agent_requests_total{deployment="canary"}[5m])
        legend: Canary Request Rate
      - expr: rate(kosmos_agent_requests_total{deployment="stable"}[5m])
        legend: Stable Request Rate
      - expr: rate(kosmos_agent_requests_total{deployment="canary",status="error"}[5m])
        legend: Canary Error Rate
```

---

## Cost Analytics {#cost-analytics}

**UID:** `kosmos-cost`  
**Purpose:** Monitor resource costs and project spending trends

### Features

- LLM token costs by model and agent
- Infrastructure costs (compute, storage, network)
- Cost projections based on usage trends
- Budget alerts and thresholds
- Cost optimization recommendations

```yaml
panels:
  - title: Total Daily Cost
    type: stat
    datasource: Prometheus
    query: |
      sum(increase(kosmos_cost_usd_total[24h]))
    fieldConfig:
      unit: currencyUSD
      thresholds:
        - value: 100
          color: green
        - value: 500
          color: yellow
        - value: 1000
          color: red

  - title: Cost by Service
    type: piechart
    datasource: Prometheus
    query: |
      sum(increase(kosmos_cost_usd_total[24h])) by (service)
    legend: "{{ service }}"

  - title: LLM Token Costs
    type: timeseries
    queries:
      - expr: sum(rate(kosmos_llm_cost_usd[1h])) by (model)
        legend: "{{ model }}"
    fieldConfig:
      unit: currencyUSD

  - title: 30-Day Cost Projection
    type: stat
    datasource: Prometheus
    query: |
      sum(avg_over_time(kosmos_cost_usd_total[7d])) * 30
    fieldConfig:
      unit: currencyUSD
      color: blue

  - title: Cost Optimization Alerts
    type: table
    datasource: Alertmanager
    query: |
      ALERTS{alertname=~".*CostOptimization.*"}
```

---

## Dashboard Provisioning

### Grafana Provisioning Config

```yaml
# provisioning/dashboards/dashboards.yml
apiVersion: 1

providers:
  - name: 'KOSMOS Dashboards'
    orgId: 1
    folder: 'KOSMOS'
    folderUid: 'kosmos'
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /etc/grafana/dashboards
```

### Dashboard as Code

```bash
# Export dashboard
curl -H "Authorization: Bearer $GRAFANA_TOKEN" \
  "http://localhost:3000/api/dashboards/uid/kosmos-overview" \
  | jq '.dashboard' > dashboards/kosmos-overview.json

# Import dashboard
curl -X POST -H "Authorization: Bearer $GRAFANA_TOKEN" \
  -H "Content-Type: application/json" \
  -d @dashboards/kosmos-overview.json \
  "http://localhost:3000/api/dashboards/db"
```

---

## Related Documentation

- [Metrics & Prometheus](metrics)
- [Alerting Rules](alerting)
- [SLA/SLO Definitions](../sla-slo)

---

**Document Owner:** sre@nuvanta-holding.com
