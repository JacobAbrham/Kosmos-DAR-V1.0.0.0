# Logging

**Document Type:** Operations Guide  
**Owner:** SRE Team  
**Last Updated:** 2025-12-13  
**Status:** 🟢 Active

---

## Overview

KOSMOS uses a centralized logging stack based on Grafana Loki for log aggregation, storage, and querying. This document covers logging standards, configuration, and common queries.

---

## Logging Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Logging Stack                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                        Grafana                                   │   │
│   │               (Log Exploration & Dashboards)                     │   │
│   └───────────────────────────┬─────────────────────────────────────┘   │
│                               │                                          │
│                               ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                         Loki                                     │   │
│   │              (Log Aggregation & Storage)                         │   │
│   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐    │   │
│   │   │ Distributor │  │   Ingester  │  │      Querier        │    │   │
│   │   └─────────────┘  └─────────────┘  └─────────────────────┘    │   │
│   └───────────────────────────┬─────────────────────────────────────┘   │
│                               │                                          │
│   ┌───────────────────────────┼─────────────────────────────────────┐   │
│   │                   Collection Layer                               │   │
│   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐    │   │
│   │   │  Promtail   │  │  Promtail   │  │      Promtail       │    │   │
│   │   │  (Node 1)   │  │  (Node 2)   │  │      (Node 3)       │    │   │
│   │   └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘    │   │
│   └──────────┼────────────────┼─────────────────────┼────────────────┘   │
│              │                │                     │                    │
│   ┌──────────▼────────────────▼─────────────────────▼────────────────┐   │
│   │                    Application Pods                               │   │
│   │   ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌────────────┐   │   │
│   │   │   Zeus    │  │  Athena   │  │  Hermes   │  │  Chronos   │   │   │
│   │   │  stdout   │  │  stdout   │  │  stdout   │  │  stdout    │   │   │
│   │   └───────────┘  └───────────┘  └───────────┘  └────────────┘   │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Logging Standards

### Log Format (JSON)

```python
# logging_config.py
import structlog
import logging
from datetime import datetime

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
```

### Standard Log Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `timestamp` | ISO 8601 | Yes | Log event time |
| `level` | string | Yes | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `message` | string | Yes | Human-readable message |
| `service` | string | Yes | Service/agent name |
| `trace_id` | string | Conditional | Distributed trace ID |
| `span_id` | string | Conditional | Span ID for tracing |
| `user_id` | string | Conditional | User identifier (hashed) |
| `tenant_id` | string | Conditional | Tenant identifier |
| `request_id` | string | Conditional | Request correlation ID |
| `error_type` | string | Conditional | Exception class name |
| `error_message` | string | Conditional | Exception message |
| `duration_ms` | number | Conditional | Operation duration |

### Example Log Entries

```json
// INFO - Request completed
{
  "timestamp": "2025-12-13T10:30:45.123Z",
  "level": "INFO",
  "message": "Request completed successfully",
  "service": "zeus-orchestrator",
  "trace_id": "abc123def456",
  "request_id": "req-789",
  "user_id": "usr_hashed_123",
  "tenant_id": "tenant_456",
  "duration_ms": 142,
  "method": "POST",
  "path": "/api/v1/orchestrate",
  "status_code": 200
}

// ERROR - Exception occurred
{
  "timestamp": "2025-12-13T10:30:46.789Z",
  "level": "ERROR",
  "message": "Failed to process request",
  "service": "athena-knowledge",
  "trace_id": "abc123def456",
  "request_id": "req-790",
  "error_type": "DatabaseConnectionError",
  "error_message": "Connection refused to postgres:5432",
  "stack_trace": "Traceback (most recent call last):\n  File..."
}

// WARNING - Rate limit approaching
{
  "timestamp": "2025-12-13T10:30:47.000Z",
  "level": "WARNING",
  "message": "Rate limit threshold approaching",
  "service": "hermes-communications",
  "provider": "huggingface",
  "current_rate": 450,
  "limit": 500,
  "window_seconds": 60
}
```

---

## Log Levels

| Level | When to Use | Examples |
|-------|-------------|----------|
| **DEBUG** | Detailed diagnostic info | Variable values, flow tracing |
| **INFO** | Normal operation events | Request completed, job started |
| **WARNING** | Potential issues | High latency, retry attempts |
| **ERROR** | Errors requiring attention | Failed operations, exceptions |
| **CRITICAL** | System-level failures | Service crash, data corruption |

### Level Configuration by Environment

| Environment | Default Level | Debug Enabled |
|-------------|---------------|---------------|
| Development | DEBUG | Yes |
| Staging | INFO | Configurable |
| Production | INFO | No (requires override) |

---

## Loki Configuration

### Loki Server

```yaml
# loki-config.yaml
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/index
    cache_location: /loki/cache
    shared_store: filesystem

compactor:
  working_directory: /loki/compactor
  shared_store: filesystem

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h  # 7 days
  ingestion_rate_mb: 16
  ingestion_burst_size_mb: 24

chunk_store_config:
  max_look_back_period: 0s

table_manager:
  retention_deletes_enabled: true
  retention_period: 720h  # 30 days
```

### Promtail Configuration

```yaml
# promtail-config.yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push
    tenant_id: kosmos

scrape_configs:
  # Kubernetes pods
  - job_name: kubernetes-pods
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      # Only scrape pods with logging enabled
      - source_labels: [__meta_kubernetes_pod_annotation_logging_enabled]
        action: keep
        regex: true

      # Set namespace label
      - source_labels: [__meta_kubernetes_namespace]
        target_label: namespace

      # Set pod name label
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod

      # Set container name label
      - source_labels: [__meta_kubernetes_pod_container_name]
        target_label: container

      # Set app label
      - source_labels: [__meta_kubernetes_pod_label_app]
        target_label: app

      # Set agent label for KOSMOS agents
      - source_labels: [__meta_kubernetes_pod_label_kosmos_agent]
        target_label: agent

      # Set log file path
      - replacement: /var/log/pods/*$1/*.log
        separator: /
        source_labels:
          - __meta_kubernetes_pod_uid
          - __meta_kubernetes_pod_container_name
        target_label: __path__

    pipeline_stages:
      # Parse JSON logs
      - json:
          expressions:
            level: level
            message: message
            trace_id: trace_id
            service: service
            error_type: error_type

      # Add parsed labels
      - labels:
          level:
          service:
          error_type:

      # Extract timestamp
      - timestamp:
          source: timestamp
          format: RFC3339Nano

      # Drop debug logs in production
      - match:
          selector: '{namespace="kosmos-core"} |= "level=DEBUG"'
          stages:
            - drop:
                expression: ".*"
```

---

## Kubernetes Deployment

```yaml
# loki-deployment.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: loki
  namespace: kosmos-observability
spec:
  serviceName: loki
  replicas: 1
  selector:
    matchLabels:
      app: loki
  template:
    metadata:
      labels:
        app: loki
    spec:
      containers:
      - name: loki
        image: grafana/loki:2.9.0
        args:
          - -config.file=/etc/loki/loki-config.yaml
        ports:
        - containerPort: 3100
          name: http
        - containerPort: 9096
          name: grpc
        resources:
          requests:
            cpu: 200m
            memory: 512Mi
          limits:
            cpu: 1
            memory: 2Gi
        volumeMounts:
        - name: config
          mountPath: /etc/loki
        - name: data
          mountPath: /loki
      volumes:
      - name: config
        configMap:
          name: loki-config
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: local-path-retain
      resources:
        requests:
          storage: 50Gi
---
# promtail-daemonset.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: promtail
  namespace: kosmos-observability
spec:
  selector:
    matchLabels:
      app: promtail
  template:
    metadata:
      labels:
        app: promtail
    spec:
      serviceAccountName: promtail
      containers:
      - name: promtail
        image: grafana/promtail:2.9.0
        args:
          - -config.file=/etc/promtail/promtail-config.yaml
        resources:
          requests:
            cpu: 50m
            memory: 64Mi
          limits:
            cpu: 200m
            memory: 256Mi
        volumeMounts:
        - name: config
          mountPath: /etc/promtail
        - name: pods
          mountPath: /var/log/pods
          readOnly: true
        - name: containers
          mountPath: /var/lib/docker/containers
          readOnly: true
      volumes:
      - name: config
        configMap:
          name: promtail-config
      - name: pods
        hostPath:
          path: /var/log/pods
      - name: containers
        hostPath:
          path: /var/lib/docker/containers
```

---

## LogQL Queries

### Basic Queries

```logql
# All logs from zeus-orchestrator
{app="zeus-orchestrator"}

# Error logs from all agents
{namespace="kosmos-core"} |= "ERROR"

# Logs from specific agent with JSON parsing
{agent="athena"} | json

# Filter by log level
{app="zeus-orchestrator"} | json | level="ERROR"

# Search for specific error type
{namespace="kosmos-core"} | json | error_type="DatabaseConnectionError"
```

### Advanced Queries

```logql
# Error rate by service (logs per second)
sum(rate({namespace="kosmos-core"} | json | level="ERROR" [5m])) by (service)

# Count errors by type in last hour
sum(count_over_time({namespace="kosmos-core"} | json | level="ERROR" [1h])) by (error_type)

# Request latency from logs (if logged)
{app="zeus-orchestrator"} | json | duration_ms > 500

# Logs with specific trace ID (distributed tracing)
{namespace="kosmos-core"} |= "trace_id=abc123def456"

# Recent errors with stack traces
{namespace="kosmos-core"} | json | level="ERROR" | line_format "{{.service}}: {{.message}}\n{{.stack_trace}}"

# Logs around a specific timestamp (context)
{app="zeus-orchestrator"} | json
  | __timestamp__ >= "2025-12-13T10:30:00Z"
  | __timestamp__ <= "2025-12-13T10:35:00Z"
```

### Pattern Matching

```logql
# Parse unstructured logs
{app="legacy-service"} | pattern "<timestamp> <level> <message>"

# Extract fields with regex
{app="nginx"} | regexp "(?P<ip>\\d+\\.\\d+\\.\\d+\\.\\d+).*\"(?P<method>\\w+) (?P<path>\\S+)"

# Log line contains specific pattern
{namespace="kosmos-core"} |~ "(?i)timeout|connection refused"
```

---

## Grafana Integration

### Log Panel Configuration

```json
{
  "datasource": "Loki",
  "targets": [
    {
      "expr": "{namespace=\"kosmos-core\"} | json | level=~\"ERROR|CRITICAL\"",
      "refId": "A"
    }
  ],
  "options": {
    "showTime": true,
    "showLabels": true,
    "showCommonLabels": false,
    "wrapLogMessage": true,
    "prettifyLogMessage": true,
    "enableLogDetails": true,
    "dedupStrategy": "none",
    "sortOrder": "Descending"
  }
}
```

### Derived Fields (Link to Traces)

```yaml
# Grafana datasource config
datasources:
  - name: Loki
    type: loki
    url: http://loki:3100
    jsonData:
      derivedFields:
        - datasourceUid: jaeger
          matcherRegex: '"trace_id":"([^"]+)"'
          name: TraceID
          url: '$${__value.raw}'
```

---

## Sensitive Data Handling

### PII Masking

```python
# pii_masking.py
import re
import structlog

class PIIMaskingProcessor:
    """Mask sensitive data in logs."""
    
    PATTERNS = {
        'email': (r'[\w.-]+@[\w.-]+\.\w+', '[EMAIL]'),
        'phone': (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]'),
        'ssn': (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),
        'credit_card': (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD]'),
        'ip_address': (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP]'),
        'jwt': (r'eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+', '[JWT]'),
    }
    
    def __call__(self, logger, method_name, event_dict):
        for key, value in event_dict.items():
            if isinstance(value, str):
                for pattern_name, (pattern, replacement) in self.PATTERNS.items():
                    value = re.sub(pattern, replacement, value)
                event_dict[key] = value
        return event_dict

# Add to structlog processors
structlog.configure(
    processors=[
        # ... other processors
        PIIMaskingProcessor(),
        structlog.processors.JSONRenderer()
    ]
)
```

### Log Redaction Rules

```yaml
# promtail pipeline stage for redaction
pipeline_stages:
  - replace:
      expression: '(password["\s:=]+)[^"\s,}]+'
      replace: '${1}[REDACTED]'
  - replace:
      expression: '(api[_-]?key["\s:=]+)[^"\s,}]+'
      replace: '${1}[REDACTED]'
  - replace:
      expression: '(secret["\s:=]+)[^"\s,}]+'
      replace: '${1}[REDACTED]'
  - replace:
      expression: '(token["\s:=]+)[^"\s,}]+'
      replace: '${1}[REDACTED]'
```

---

## Retention & Storage

| Environment | Retention | Storage Class |
|-------------|-----------|---------------|
| Development | 7 days | local-path |
| Staging | 14 days | local-path |
| Production | 30 days | local-path-retain |

### Storage Calculation

```
Daily log volume estimate:
- 11 agents × 100 req/s × 500 bytes/log = ~475 MB/hour
- Daily: ~11.4 GB
- 30 days: ~342 GB (before compression)
- With Loki compression (~10x): ~35 GB
```

---

## Related Documentation

- [Metrics & Prometheus](metrics.md)
- [Tracing](tracing.md)
- [Alerting Rules](alerting.md)

---

**Document Owner:** sre@nuvanta-holding.com
