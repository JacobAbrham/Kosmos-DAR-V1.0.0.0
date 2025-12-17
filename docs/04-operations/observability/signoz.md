# SigNoz Observability

**Unified Observability for KOSMOS**

!!! abstract "All-in-One Observability"
    SigNoz provides unified metrics, traces, and logs in a single platform, replacing the traditional Prometheus + Grafana + Jaeger stack with reduced operational overhead.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SIGNOZ ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │               SigNoz Query Service                   │   │
│  │                  (Web UI + API)                      │   │
│  └─────────────────────────┬───────────────────────────┘   │
│                            │                               │
│  ┌─────────────────────────▼───────────────────────────┐   │
│  │              ClickHouse (Storage)                    │   │
│  │         Metrics │ Traces │ Logs                      │   │
│  └─────────────────────────▲───────────────────────────┘   │
│                            │                               │
│  ┌─────────────────────────┴───────────────────────────┐   │
│  │           OpenTelemetry Collector                    │   │
│  │      OTLP Receiver │ Processors │ Exporters         │   │
│  └─────────────────────────▲───────────────────────────┘   │
│                            │                               │
│       ┌────────────────────┼────────────────────┐         │
│       │                    │                    │         │
│  ┌────┴────┐         ┌────┴────┐         ┌────┴────┐    │
│  │ Agents  │         │   MCP   │         │  Infra  │    │
│  │ (OTEL)  │         │ Servers │         │  (K3s)  │    │
│  └─────────┘         └─────────┘         └─────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation

### Helm Installation

```bash
# Add SigNoz Helm repo
helm repo add signoz https://charts.signoz.io
helm repo update

# Create namespace
kubectl create namespace kosmos-observability

# Install with resource constraints for 32GB environment
helm install signoz signoz/signoz \
  --namespace kosmos-observability \
  --values signoz-values.yaml
```

### `signoz-values.yaml`

```yaml
# SigNoz Helm values for KOSMOS (32GB constrained)
global:
  storageClass: local-path

clickhouse:
  replicaCount: 1
  persistence:
    size: 50Gi
  resources:
    requests:
      cpu: 500m
      memory: 2Gi
    limits:
      cpu: 2
      memory: 4Gi
  
  # Retention settings
  ttlExpressionMs: |
    toIntervalSecond(604800)  # 7 days for staging

queryService:
  replicaCount: 1
  resources:
    requests:
      cpu: 200m
      memory: 512Mi
    limits:
      cpu: 1
      memory: 1Gi

frontend:
  replicaCount: 1
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 256Mi

otelCollector:
  replicaCount: 1
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
```

---

## Configuration

### OpenTelemetry Collector Config

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

  # Kubernetes metrics
  k8s_cluster:
    collection_interval: 30s
    node_conditions_to_report:
      - Ready
      - MemoryPressure
      - DiskPressure

  # Host metrics
  hostmetrics:
    collection_interval: 30s
    scrapers:
      cpu:
      memory:
      disk:
      network:

processors:
  batch:
    timeout: 5s
    send_batch_size: 1000
  
  memory_limiter:
    check_interval: 1s
    limit_mib: 400
    spike_limit_mib: 100

  # Add KOSMOS-specific attributes
  attributes:
    actions:
      - key: deployment.environment
        value: staging
        action: upsert
      - key: service.namespace
        value: kosmos
        action: upsert

exporters:
  clickhousetraces:
    endpoint: tcp://clickhouse:9000
    database: signoz_traces
  
  clickhousemetrics:
    endpoint: tcp://clickhouse:9000
    database: signoz_metrics
  
  clickhouselogs:
    endpoint: tcp://clickhouse:9000
    database: signoz_logs

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch, attributes]
      exporters: [clickhousetraces]
    
    metrics:
      receivers: [otlp, k8s_cluster, hostmetrics]
      processors: [memory_limiter, batch, attributes]
      exporters: [clickhousemetrics]
    
    logs:
      receivers: [otlp]
      processors: [memory_limiter, batch, attributes]
      exporters: [clickhouselogs]
```

---

## Agent Instrumentation

### Python Agent SDK

```python
# agents/common/telemetry.py
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource

def init_telemetry(service_name: str):
    resource = Resource.create({
        "service.name": service_name,
        "service.namespace": "kosmos",
        "deployment.environment": os.getenv("ENVIRONMENT", "staging")
    })
    
    # Traces
    trace_provider = TracerProvider(resource=resource)
    trace_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(endpoint="http://signoz-otel-collector:4317")
        )
    )
    trace.set_tracer_provider(trace_provider)
    
    # Metrics
    metric_provider = MeterProvider(
        resource=resource,
        metric_readers=[
            PeriodicExportingMetricReader(
                OTLPMetricExporter(endpoint="http://signoz-otel-collector:4317"),
                export_interval_millis=30000
            )
        ]
    )
    metrics.set_meter_provider(metric_provider)
    
    return trace.get_tracer(service_name), metrics.get_meter(service_name)


# Usage in agent
tracer, meter = init_telemetry("zeus-orchestrator")

task_counter = meter.create_counter(
    "kosmos.tasks.total",
    description="Total tasks processed"
)

@tracer.start_as_current_span("route_task")
def route_task(message: str) -> RoutingResult:
    span = trace.get_current_span()
    span.set_attribute("task.message_length", len(message))
    
    result = perform_routing(message)
    
    span.set_attribute("task.routed_agent", result.agent)
    task_counter.add(1, {"agent": result.agent})
    
    return result
```

---

## Dashboards

### Pre-built Dashboards

| Dashboard | Purpose |
|-----------|---------|
| KOSMOS Overview | System health, agent status |
| Agent Performance | Per-agent latency, throughput |
| MCP Server Health | MCP call success/failure |
| LLM Metrics | Token usage, latency by model |
| Infrastructure | K3s node metrics |

### Custom Dashboard Example

```json
{
  "title": "KOSMOS Agent Performance",
  "panels": [
    {
      "title": "Task Routing Latency (p95)",
      "query": "histogram_quantile(0.95, sum(rate(kosmos_task_duration_seconds_bucket[5m])) by (le, agent))"
    },
    {
      "title": "Tasks per Agent",
      "query": "sum(rate(kosmos_tasks_total[5m])) by (agent)"
    },
    {
      "title": "Error Rate",
      "query": "sum(rate(kosmos_tasks_total{status='error'}[5m])) / sum(rate(kosmos_tasks_total[5m]))"
    }
  ]
}
```

---

## Alerting

### Alert Rules

```yaml
# alerts/kosmos-alerts.yaml
groups:
  - name: kosmos-agents
    rules:
      - alert: AgentHighLatency
        expr: histogram_quantile(0.95, sum(rate(kosmos_task_duration_seconds_bucket[5m])) by (le, agent)) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Agent {{ $labels.agent }} has high latency"
          description: "P95 latency is {{ $value }}s"
      
      - alert: AgentDown
        expr: up{job=~"kosmos-.*"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Agent {{ $labels.job }} is down"
      
      - alert: HighErrorRate
        expr: |
          sum(rate(kosmos_tasks_total{status="error"}[5m])) by (agent) 
          / sum(rate(kosmos_tasks_total[5m])) by (agent) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Agent {{ $labels.agent }} error rate above 5%"
```

### Notification Channels

```yaml
# SigNoz notification config
alertmanager:
  config:
    receivers:
      - name: 'kosmos-team'
        slack_configs:
          - api_url: '${SLACK_WEBHOOK_URL}'
            channel: '#kosmos-alerts'
        email_configs:
          - to: 'ops@nuvanta.local'
    
    route:
      receiver: 'kosmos-team'
      group_by: ['alertname', 'agent']
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 4h
```

---

## Retention & Storage

### Staging (7 days)

```sql
-- ClickHouse TTL settings
ALTER TABLE signoz_traces.signoz_index_v2 
  MODIFY TTL timestamp + INTERVAL 7 DAY;

ALTER TABLE signoz_metrics.samples_v4 
  MODIFY TTL timestamp_ms/1000 + INTERVAL 7 DAY;

ALTER TABLE signoz_logs.logs 
  MODIFY TTL timestamp + INTERVAL 7 DAY;
```

### Production (30 days)

```sql
ALTER TABLE signoz_traces.signoz_index_v2 
  MODIFY TTL timestamp + INTERVAL 30 DAY;
```

---

## Access

| Environment | URL | Auth |
|-------------|-----|------|
| Staging | `https://signoz.staging.kosmos.nuvanta.local` | Zitadel SSO |
| Production | `https://signoz.kosmos.nuvanta.local` | Zitadel SSO |

---

## See Also

- [Langfuse](langfuse.md) — LLM-specific observability
- [ADR-007 Observability Stack](../../02-architecture/adr/ADR-007-observability-stack.md)
- [Alerting Rules](alerting.md)

---

**Last Updated:** December 2025
