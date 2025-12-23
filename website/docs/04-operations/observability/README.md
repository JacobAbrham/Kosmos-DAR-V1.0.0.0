# Observability

**Document Type:** Operations Guide  
**Owner:** SRE Team  
**Reviewers:** Platform Engineering, Security  
**Review Cadence:** Quarterly  
**Last Updated:** 2025-12-13  
**Status:** 🟢 Active

---

## Overview

KOSMOS implements a comprehensive observability stack following the three pillars: **Metrics**, **Logs**, and **Traces**. Additionally, specialized **LLM Observability** is provided through Langfuse for AI-specific monitoring.

---

## Observability Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      KOSMOS Observability Stack                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         Visualization Layer                          │   │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐  │   │
│   │  │   Grafana   │  │  Langfuse   │  │      AlertManager           │  │   │
│   │  │ Dashboards  │  │     UI      │  │   Notifications             │  │   │
│   │  └──────┬──────┘  └──────┬──────┘  └─────────────┬───────────────┘  │   │
│   └─────────┼────────────────┼───────────────────────┼──────────────────┘   │
│             │                │                       │                       │
│   ┌─────────┼────────────────┼───────────────────────┼──────────────────┐   │
│   │         │          Storage Layer                 │                  │   │
│   │  ┌──────▼──────┐  ┌──────▼──────┐  ┌────────────▼────────────────┐ │   │
│   │  │ Prometheus  │  │  Langfuse   │  │          Loki               │ │   │
│   │  │   (TSDB)    │  │  Postgres   │  │    (Log Aggregation)        │ │   │
│   │  └──────┬──────┘  └─────────────┘  └────────────┬────────────────┘ │   │
│   └─────────┼───────────────────────────────────────┼──────────────────┘   │
│             │                                       │                       │
│   ┌─────────┼───────────────────────────────────────┼──────────────────┐   │
│   │         │           Collection Layer            │                  │   │
│   │  ┌──────▼──────┐  ┌─────────────┐  ┌───────────▼────────────────┐ │   │
│   │  │   Metrics   │  │   Traces    │  │          Logs              │ │   │
│   │  │  Exporters  │  │   (OTLP)    │  │       (Promtail)           │ │   │
│   │  └──────┬──────┘  └──────┬──────┘  └───────────┬────────────────┘ │   │
│   └─────────┼────────────────┼─────────────────────┼────────────────────┘   │
│             │                │                     │                        │
│   ┌─────────▼────────────────▼─────────────────────▼────────────────────┐   │
│   │                        Application Layer                             │   │
│   │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────────────┐ │   │
│   │  │   Zeus    │  │  Athena   │  │  Hermes   │  │  Other Agents     │ │   │
│   │  └───────────┘  └───────────┘  └───────────┘  └───────────────────┘ │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Overview

| Component | Purpose | Port | Namespace |
|-----------|---------|------|-----------|
| **Prometheus** | Metrics collection & storage | 9090 | kosmos-observability |
| **Grafana** | Visualization & dashboards | 3000 | kosmos-observability |
| **AlertManager** | Alert routing & notifications | 9093 | kosmos-observability |
| **Loki** | Log aggregation | 3100 | kosmos-observability |
| **Promtail** | Log shipping | - | kosmos-observability |
| **Langfuse** | LLM observability | 3001 | kosmos-observability |
| **Jaeger** | Distributed tracing | 16686 | kosmos-observability |

---

## Documents in This Section

| Document | Description | Status |
|----------|-------------|--------|
| [Metrics & Prometheus](metrics) | Metric types, exporters, PromQL queries | ✅ Complete |
| [Grafana Dashboards](dashboards) | Dashboard catalog, templates | ✅ Complete |
| [Alerting Rules](alerting) | Alert definitions, routing, escalation | ✅ Complete |
| [Logging](logging) | Centralized logging with Loki | ✅ Complete |
| [Tracing](tracing) | Distributed tracing with Jaeger/OTLP | ✅ Complete |
| [LLM Observability](llm-observability) | Langfuse integration, prompt monitoring | ✅ Complete |

---

## Quick Start

### Accessing Dashboards

```bash
# Port-forward Grafana (staging/production)
kubectl port-forward svc/grafana 3000:3000 -n kosmos-observability

# Port-forward Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n kosmos-observability

# Port-forward Langfuse
kubectl port-forward svc/langfuse 3001:3000 -n kosmos-observability
```

### Local Development

```yaml
# docker-compose.observability.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:v2.48.0
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:10.2.0
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_AUTH_ANONYMOUS_ENABLED=true
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning

  loki:
    image: grafana/loki:2.9.0
    ports:
      - "3100:3100"
    volumes:
      - loki-data:/loki

  promtail:
    image: grafana/promtail:2.9.0
    volumes:
      - /var/log:/var/log:ro
      - ./promtail.yml:/etc/promtail/promtail.yml

volumes:
  prometheus-data:
  grafana-data:
  loki-data:
```

---

## Key Metrics by Domain

### Agent Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `kosmos_agent_requests_total` | Counter | Total requests per agent |
| `kosmos_agent_request_duration_seconds` | Histogram | Request latency |
| `kosmos_agent_errors_total` | Counter | Error count by type |
| `kosmos_agent_active_sessions` | Gauge | Current active sessions |

### LLM Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `kosmos_llm_tokens_total` | Counter | Token usage (input/output) |
| `kosmos_llm_cost_dollars` | Counter | Estimated cost |
| `kosmos_llm_latency_seconds` | Histogram | LLM response time |
| `kosmos_llm_cache_hits_total` | Counter | Semantic cache hits |

### Infrastructure Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `kosmos_db_connections_active` | Gauge | Active DB connections |
| `kosmos_cache_hit_ratio` | Gauge | Dragonfly cache hit rate |
| `kosmos_queue_depth` | Gauge | NATS queue depth |
| `kosmos_storage_bytes` | Gauge | MinIO storage usage |

---

## SLI/SLO Integration

| SLI | Target SLO | Measurement |
|-----|------------|-------------|
| Availability | 99.9% | `up{job="kosmos"}` |
| Latency (p99) | < 500ms | `histogram_quantile(0.99, ...)` |
| Error Rate | < 0.1% | `rate(errors) / rate(requests)` |
| Throughput | > 100 req/s | `rate(requests[5m])` |

See [SLA/SLO Documentation](../sla-slo) for detailed definitions.

---

## Related Documentation

- [SLA/SLO Definitions](../sla-slo)
- [Incident Response](../incident-response/README)
- [Infrastructure Overview](../infrastructure/README)

---

**Document Owner:** sre@nuvanta-holding.com  
**On-Call:** oncall@nuvanta-holding.com
