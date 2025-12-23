# Prometheus Setup

**Document Type:** Operations Guide  
**Owner:** SRE Team  
**Last Updated:** 2025-12-13  
**Status:** 🟢 Active

---

## Overview

Prometheus is the core metrics collection and storage system for KOSMOS. This document covers deployment, configuration, scrape targets, recording rules, and operational procedures.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Prometheus Architecture                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│   │    Zeus     │  │  PostgreSQL │  │   NATS      │  │  Dragonfly  │   │
│   │  :8000/     │  │  :9187      │  │  :8222/     │  │  :6379      │   │
│   │  metrics    │  │  exporter   │  │  metrics    │  │  metrics    │   │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘   │
│          │                │                │                │          │
│          └────────────────┴────────────────┴────────────────┘          │
│                                    │                                    │
│                                    ▼                                    │
│                         ┌─────────────────────┐                        │
│                         │     Prometheus      │                        │
│                         │    :9090            │                        │
│                         │                     │                        │
│                         │  ┌───────────────┐  │                        │
│                         │  │   TSDB        │  │                        │
│                         │  │  (15 days)    │  │                        │
│                         │  └───────────────┘  │                        │
│                         └──────────┬──────────┘                        │
│                                    │                                    │
│                    ┌───────────────┼───────────────┐                   │
│                    ▼               ▼               ▼                   │
│             ┌───────────┐   ┌───────────┐   ┌───────────┐             │
│             │  Grafana  │   │Alertmanager│  │  Thanos   │             │
│             │  :3000    │   │  :9093     │  │ (future)  │             │
│             └───────────┘   └───────────┘   └───────────┘             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Deployment

### Kubernetes Manifest

```yaml
# prometheus-deployment.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: kosmos-observability
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: kosmos-observability
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
      external_labels:
        cluster: kosmos-production
        
    alerting:
      alertmanagers:
        - static_configs:
            - targets:
              - alertmanager:9093
              
    rule_files:
      - /etc/prometheus/rules/*.yml
      
    scrape_configs:
      # Prometheus self-monitoring
      - job_name: 'prometheus'
        static_configs:
          - targets: ['localhost:9090']
          
      # Kubernetes API server
      - job_name: 'kubernetes-apiservers'
        kubernetes_sd_configs:
          - role: endpoints
        scheme: https
        tls_config:
          ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
        relabel_configs:
          - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
            action: keep
            regex: default;kubernetes;https
            
      # Kubernetes nodes
      - job_name: 'kubernetes-nodes'
        kubernetes_sd_configs:
          - role: node
        scheme: https
        tls_config:
          ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
        relabel_configs:
          - action: labelmap
            regex: __meta_kubernetes_node_label_(.+)
            
      # Kubernetes pods with prometheus.io annotations
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
            action: replace
            target_label: __metrics_path__
            regex: (.+)
          - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
            action: replace
            regex: ([^:]+)(?::\d+)?;(\d+)
            replacement: $1:$2
            target_label: __address__
          - action: labelmap
            regex: __meta_kubernetes_pod_label_(.+)
          - source_labels: [__meta_kubernetes_namespace]
            action: replace
            target_label: kubernetes_namespace
          - source_labels: [__meta_kubernetes_pod_name]
            action: replace
            target_label: kubernetes_pod_name
            
      # KOSMOS agents (ServiceMonitor equivalent)
      - job_name: 'kosmos-agents'
        kubernetes_sd_configs:
          - role: service
            namespaces:
              names:
                - kosmos-core
        relabel_configs:
          - source_labels: [__meta_kubernetes_service_label_app_kubernetes_io_part_of]
            action: keep
            regex: kosmos
          - source_labels: [__meta_kubernetes_service_name]
            action: replace
            target_label: service
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: kosmos-observability
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      serviceAccountName: prometheus
      containers:
      - name: prometheus
        image: prom/prometheus:v2.48.0
        args:
          - '--config.file=/etc/prometheus/prometheus.yml'
          - '--storage.tsdb.path=/prometheus'
          - '--storage.tsdb.retention.time=15d'
          - '--web.enable-lifecycle'
          - '--web.enable-admin-api'
        ports:
        - containerPort: 9090
        resources:
          requests:
            cpu: "500m"
            memory: "2Gi"
          limits:
            cpu: "2"
            memory: "4Gi"
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
        - name: rules
          mountPath: /etc/prometheus/rules
        - name: storage
          mountPath: /prometheus
        livenessProbe:
          httpGet:
            path: /-/healthy
            port: 9090
          initialDelaySeconds: 30
          periodSeconds: 15
        readinessProbe:
          httpGet:
            path: /-/ready
            port: 9090
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: config
        configMap:
          name: prometheus-config
      - name: rules
        configMap:
          name: prometheus-rules
      - name: storage
        persistentVolumeClaim:
          claimName: prometheus-storage
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: prometheus-storage
  namespace: kosmos-observability
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
  storageClassName: local-path-retain
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: kosmos-observability
spec:
  selector:
    app: prometheus
  ports:
  - port: 9090
    targetPort: 9090
```

### RBAC Configuration

```yaml
# prometheus-rbac.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: prometheus
  namespace: kosmos-observability
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: prometheus
rules:
- apiGroups: [""]
  resources:
  - nodes
  - nodes/proxy
  - services
  - endpoints
  - pods
  verbs: ["get", "list", "watch"]
- apiGroups: ["extensions"]
  resources:
  - ingresses
  verbs: ["get", "list", "watch"]
- nonResourceURLs: ["/metrics"]
  verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: prometheus
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: prometheus
subjects:
- kind: ServiceAccount
  name: prometheus
  namespace: kosmos-observability
```

---

## Scrape Targets

### Application Metrics

| Service | Endpoint | Interval | Labels |
|---------|----------|----------|--------|
| Zeus Orchestrator | `:8000/metrics` | 15s | `agent=zeus` |
| Athena Knowledge | `:8001/metrics` | 15s | `agent=athena` |
| Hermes Communications | `:8002/metrics` | 15s | `agent=hermes` |
| API Gateway | `:8080/metrics` | 15s | `component=gateway` |

### Infrastructure Metrics

| Service | Exporter | Port | Metrics |
|---------|----------|------|---------|
| PostgreSQL | postgres_exporter | 9187 | Connections, queries, replication |
| Dragonfly | Built-in | 6379 | Memory, commands, clients |
| NATS | Built-in | 8222 | Messages, subscriptions |
| K3s Nodes | node_exporter | 9100 | CPU, memory, disk, network |

### Exporter Deployments

```yaml
# postgres-exporter.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-exporter
  namespace: kosmos-db
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres-exporter
  template:
    metadata:
      labels:
        app: postgres-exporter
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9187"
    spec:
      containers:
      - name: exporter
        image: prometheuscommunity/postgres-exporter:v0.15.0
        env:
        - name: DATA_SOURCE_NAME
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: exporter-dsn
        ports:
        - containerPort: 9187
        resources:
          requests:
            cpu: "50m"
            memory: "64Mi"
          limits:
            cpu: "200m"
            memory: "128Mi"
```

---

## Recording Rules

### Agent Performance Rules

```yaml
# recording-rules-agents.yml
groups:
- name: kosmos-agents
  interval: 30s
  rules:
  # Request rate by agent
  - record: kosmos:agent:request_rate_5m
    expr: sum(rate(http_requests_total{job="kosmos-agents"}[5m])) by (agent)
    
  # Error rate by agent
  - record: kosmos:agent:error_rate_5m
    expr: |
      sum(rate(http_requests_total{job="kosmos-agents",status=~"5.."}[5m])) by (agent)
      /
      sum(rate(http_requests_total{job="kosmos-agents"}[5m])) by (agent)
      
  # P99 latency by agent
  - record: kosmos:agent:latency_p99_5m
    expr: |
      histogram_quantile(0.99, 
        sum(rate(http_request_duration_seconds_bucket{job="kosmos-agents"}[5m])) 
        by (agent, le)
      )
      
  # Agent task success rate
  - record: kosmos:agent:task_success_rate_5m
    expr: |
      sum(rate(agent_tasks_total{status="success"}[5m])) by (agent)
      /
      sum(rate(agent_tasks_total[5m])) by (agent)
```

### LLM Performance Rules

```yaml
# recording-rules-llm.yml
groups:
- name: kosmos-llm
  interval: 30s
  rules:
  # LLM request rate
  - record: kosmos:llm:request_rate_5m
    expr: sum(rate(llm_requests_total[5m])) by (provider, model)
    
  # LLM latency percentiles
  - record: kosmos:llm:latency_p50_5m
    expr: |
      histogram_quantile(0.50, 
        sum(rate(llm_request_duration_seconds_bucket[5m])) by (provider, model, le)
      )
  - record: kosmos:llm:latency_p99_5m
    expr: |
      histogram_quantile(0.99, 
        sum(rate(llm_request_duration_seconds_bucket[5m])) by (provider, model, le)
      )
      
  # Token consumption rate
  - record: kosmos:llm:tokens_per_minute
    expr: sum(rate(llm_tokens_total[1m])) by (provider, model, type) * 60
    
  # Estimated hourly cost
  - record: kosmos:llm:cost_per_hour
    expr: |
      sum(increase(llm_cost_dollars[1h])) by (provider, model)
```

### Infrastructure Rules

```yaml
# recording-rules-infra.yml
groups:
- name: kosmos-infrastructure
  interval: 30s
  rules:
  # PostgreSQL connection utilization
  - record: kosmos:postgres:connection_utilization
    expr: |
      pg_stat_activity_count{state="active"} 
      / 
      pg_settings_max_connections
      
  # PostgreSQL replication lag
  - record: kosmos:postgres:replication_lag_bytes
    expr: pg_replication_lag_bytes
    
  # Cache hit ratio
  - record: kosmos:postgres:cache_hit_ratio
    expr: |
      pg_stat_database_blks_hit 
      / 
      (pg_stat_database_blks_hit + pg_stat_database_blks_read)
      
  # Dragonfly memory usage
  - record: kosmos:dragonfly:memory_usage_ratio
    expr: |
      dragonfly_used_memory_bytes 
      / 
      dragonfly_maxmemory_bytes
      
  # NATS message rate
  - record: kosmos:nats:message_rate_5m
    expr: sum(rate(nats_messages_total[5m])) by (stream)
```

---

## Application Instrumentation

### Python (FastAPI) Instrumentation

```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Response
import time

# Define metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status', 'agent']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint', 'agent'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

LLM_REQUEST_LATENCY = Histogram(
    'llm_request_duration_seconds',
    'LLM request latency',
    ['provider', 'model'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

LLM_TOKENS = Counter(
    'llm_tokens_total',
    'LLM tokens consumed',
    ['provider', 'model', 'type']  # type: input, output
)

LLM_COST = Counter(
    'llm_cost_dollars',
    'Estimated LLM cost in dollars',
    ['provider', 'model']
)

AGENT_TASKS = Counter(
    'agent_tasks_total',
    'Agent tasks processed',
    ['agent', 'task_type', 'status']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections',
    ['agent']
)

# Middleware for automatic instrumentation
class PrometheusMiddleware:
    def __init__(self, app: FastAPI, agent_name: str):
        self.app = app
        self.agent_name = agent_name
        
    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return
            
        start_time = time.time()
        
        # Track request
        async def send_wrapper(message):
            if message['type'] == 'http.response.start':
                duration = time.time() - start_time
                status = message['status']
                method = scope['method']
                path = scope['path']
                
                REQUEST_COUNT.labels(
                    method=method,
                    endpoint=path,
                    status=status,
                    agent=self.agent_name
                ).inc()
                
                REQUEST_LATENCY.labels(
                    method=method,
                    endpoint=path,
                    agent=self.agent_name
                ).observe(duration)
                
            await send(message)
            
        await self.app(scope, receive, send_wrapper)

# Metrics endpoint
def setup_metrics(app: FastAPI):
    @app.get("/metrics")
    async def metrics():
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
```

### LLM Call Instrumentation

```python
# llm_metrics.py
import time
from contextlib import contextmanager
from typing import Optional

@contextmanager
def track_llm_call(provider: str, model: str):
    """Context manager to track LLM call metrics."""
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        LLM_REQUEST_LATENCY.labels(
            provider=provider,
            model=model
        ).observe(duration)

def record_llm_usage(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cost: Optional[float] = None
):
    """Record LLM token usage and cost."""
    LLM_TOKENS.labels(
        provider=provider,
        model=model,
        type='input'
    ).inc(input_tokens)
    
    LLM_TOKENS.labels(
        provider=provider,
        model=model,
        type='output'
    ).inc(output_tokens)
    
    if cost is not None:
        LLM_COST.labels(
            provider=provider,
            model=model
        ).inc(cost)

# Usage example
async def call_llm(prompt: str) -> str:
    with track_llm_call(provider="huggingface", model="mistral-7b"):
        response = await llm_client.generate(prompt)
        
    record_llm_usage(
        provider="huggingface",
        model="mistral-7b",
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        cost=calculate_cost(response.usage)
    )
    
    return response.text
```

---

## Operations

### Health Check

```bash
# Check Prometheus health
curl -s http://prometheus:9090/-/healthy
# Expected: Prometheus Server is Healthy.

# Check targets
curl -s http://prometheus:9090/api/v1/targets | jq '.data.activeTargets | length'

# Check for down targets
curl -s http://prometheus:9090/api/v1/targets | \
  jq '.data.activeTargets[] | select(.health != "up") | {job: .labels.job, health: .health}'
```

### Configuration Reload

```bash
# Hot reload configuration (no restart required)
curl -X POST http://prometheus:9090/-/reload

# Verify config
curl -s http://prometheus:9090/api/v1/status/config | jq '.data.yaml' | head -50
```

### Storage Management

```bash
# Check TSDB status
curl -s http://prometheus:9090/api/v1/status/tsdb | jq '.'

# Check disk usage
kubectl exec -n kosmos-observability prometheus-0 -- df -h /prometheus

# Delete old data (admin API must be enabled)
curl -X POST 'http://prometheus:9090/api/v1/admin/tsdb/delete_series?match[]={job="old-job"}'
curl -X POST http://prometheus:9090/api/v1/admin/tsdb/clean_tombstones
```

### Backup and Restore

```bash
# Snapshot TSDB
curl -X POST http://prometheus:9090/api/v1/admin/tsdb/snapshot
# Returns: {"status":"success","data":{"name":"20251213T120000Z-abc123"}}

# Copy snapshot
kubectl cp kosmos-observability/prometheus-0:/prometheus/snapshots/20251213T120000Z-abc123 \
  ./prometheus-backup/

# Restore (requires Prometheus restart)
kubectl cp ./prometheus-backup/20251213T120000Z-abc123 \
  kosmos-observability/prometheus-0:/prometheus/
kubectl rollout restart deployment/prometheus -n kosmos-observability
```

---

## Troubleshooting

### Target Not Being Scraped

```bash
# 1. Check service discovery
curl -s 'http://prometheus:9090/api/v1/targets?state=any' | \
  jq '.data.activeTargets[] | select(.labels.job == "kosmos-agents")'

# 2. Verify annotations on pod
kubectl get pod zeus-0 -n kosmos-core -o jsonpath='{.metadata.annotations}'
# Should include: prometheus.io/scrape: "true"

# 3. Check network connectivity
kubectl exec -n kosmos-observability prometheus-0 -- \
  wget -qO- http://zeus.kosmos-core:8000/metrics | head -10
```

### High Cardinality Issues

```bash
# Find high cardinality metrics
curl -s http://prometheus:9090/api/v1/status/tsdb | \
  jq '.data.seriesCountByMetricName | to_entries | sort_by(-.value) | .[0:10]'

# Find labels with high cardinality
curl -s 'http://prometheus:9090/api/v1/label/__name__/values' | jq '.data | length'
```

### Memory Issues

```bash
# Check Prometheus memory
kubectl top pod -n kosmos-observability prometheus-0

# Reduce memory with recording rules instead of high-cardinality queries
# Add to prometheus.yml:
#   query.max-samples: 50000000
```

---

## Related Documentation

- [Grafana Dashboards](grafana)
- [Alerting Rules](alerting)
- [SLA/SLO Definitions](../sla-slo)

---

**Document Owner:** sre@nuvanta-holding.com
