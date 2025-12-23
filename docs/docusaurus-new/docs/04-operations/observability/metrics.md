# Metrics & Prometheus

**Document Type:** Operations Guide  
**Owner:** SRE Team  
**Last Updated:** 2025-12-13  
**Status:** 🟢 Active

---

## Overview

KOSMOS uses Prometheus for metrics collection, storage, and alerting. This document covers metric definitions, collection configuration, and common PromQL queries.

---

## Prometheus Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Prometheus Stack                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │                    Prometheus Server                              │  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐   │  │
│   │  │   Scraper   │  │    TSDB     │  │     Rule Engine         │   │  │
│   │  │             │  │             │  │  (Recording + Alerting) │   │  │
│   │  └──────┬──────┘  └─────────────┘  └───────────┬─────────────┘   │  │
│   └─────────┼──────────────────────────────────────┼─────────────────┘  │
│             │                                      │                     │
│             ▼                                      ▼                     │
│   ┌─────────────────────────┐            ┌─────────────────────────┐   │
│   │    Service Discovery    │            │      AlertManager       │   │
│   │  (Kubernetes, Static)   │            │   (Slack, PagerDuty)    │   │
│   └─────────────────────────┘            └─────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Prometheus Configuration

### Server Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: kosmos-production
    environment: production

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

  # Kubernetes service discovery
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - kosmos-core
            - kosmos-db
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
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: kubernetes_namespace
      - source_labels: [__meta_kubernetes_pod_name]
        action: replace
        target_label: kubernetes_pod_name
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: replace
        target_label: app

  # Agent endpoints
  - job_name: 'kosmos-agents'
    kubernetes_sd_configs:
      - role: endpoints
        namespaces:
          names:
            - kosmos-core
    relabel_configs:
      - source_labels: [__meta_kubernetes_service_label_app_kubernetes_io_component]
        action: keep
        regex: agent
      - source_labels: [__meta_kubernetes_service_name]
        action: replace
        target_label: service

  # PostgreSQL exporter
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  # Dragonfly metrics
  - job_name: 'dragonfly'
    static_configs:
      - targets: ['dragonfly:6379']

  # NATS metrics
  - job_name: 'nats'
    static_configs:
      - targets: ['nats:8222']
```

### Kubernetes Deployment

```yaml
# prometheus-deployment.yaml
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
          - '--storage.tsdb.retention.size=50GB'
          - '--web.enable-lifecycle'
          - '--web.enable-admin-api'
        ports:
        - containerPort: 9090
        resources:
          requests:
            cpu: 500m
            memory: 2Gi
          limits:
            cpu: 2
            memory: 4Gi
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
        - name: rules
          mountPath: /etc/prometheus/rules
        - name: data
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
      - name: data
        persistentVolumeClaim:
          claimName: prometheus-data
```

---

## Metric Definitions

### Agent Metrics

```python
# agent_metrics.py
from prometheus_client import Counter, Histogram, Gauge, Info

# Request metrics
AGENT_REQUESTS = Counter(
    'kosmos_agent_requests_total',
    'Total number of requests to agent',
    ['agent', 'method', 'status']
)

AGENT_REQUEST_DURATION = Histogram(
    'kosmos_agent_request_duration_seconds',
    'Request duration in seconds',
    ['agent', 'method'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

AGENT_ERRORS = Counter(
    'kosmos_agent_errors_total',
    'Total number of errors',
    ['agent', 'error_type']
)

AGENT_ACTIVE_SESSIONS = Gauge(
    'kosmos_agent_active_sessions',
    'Number of active sessions',
    ['agent']
)

# Agent info
AGENT_INFO = Info(
    'kosmos_agent',
    'Agent information',
    ['agent']
)

# Usage example
def handle_request(agent_name: str, method: str):
    with AGENT_REQUEST_DURATION.labels(agent=agent_name, method=method).time():
        try:
            result = process_request()
            AGENT_REQUESTS.labels(agent=agent_name, method=method, status='success').inc()
            return result
        except Exception as e:
            AGENT_REQUESTS.labels(agent=agent_name, method=method, status='error').inc()
            AGENT_ERRORS.labels(agent=agent_name, error_type=type(e).__name__).inc()
            raise
```

### LLM Metrics

```python
# llm_metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Token usage
LLM_TOKENS = Counter(
    'kosmos_llm_tokens_total',
    'Total tokens used',
    ['provider', 'model', 'direction']  # direction: input/output
)

# Cost tracking
LLM_COST = Counter(
    'kosmos_llm_cost_dollars_total',
    'Estimated cost in dollars',
    ['provider', 'model']
)

# Latency
LLM_LATENCY = Histogram(
    'kosmos_llm_latency_seconds',
    'LLM response latency',
    ['provider', 'model'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
)

# Cache metrics
LLM_CACHE_HITS = Counter(
    'kosmos_llm_cache_hits_total',
    'Semantic cache hits',
    ['cache_type']
)

LLM_CACHE_MISSES = Counter(
    'kosmos_llm_cache_misses_total',
    'Semantic cache misses',
    ['cache_type']
)

# Rate limiting
LLM_RATE_LIMIT_HITS = Counter(
    'kosmos_llm_rate_limit_hits_total',
    'Rate limit hits',
    ['provider']
)

# Example usage
async def call_llm(prompt: str, model: str = "mistral-7b"):
    start_time = time.time()
    
    # Check cache first
    cached = await check_cache(prompt)
    if cached:
        LLM_CACHE_HITS.labels(cache_type='semantic').inc()
        return cached
    
    LLM_CACHE_MISSES.labels(cache_type='semantic').inc()
    
    try:
        response = await llm_client.generate(prompt, model=model)
        
        # Record metrics
        duration = time.time() - start_time
        LLM_LATENCY.labels(provider='huggingface', model=model).observe(duration)
        LLM_TOKENS.labels(provider='huggingface', model=model, direction='input').inc(response.input_tokens)
        LLM_TOKENS.labels(provider='huggingface', model=model, direction='output').inc(response.output_tokens)
        
        # Calculate cost (example rates)
        cost = (response.input_tokens * 0.0001 + response.output_tokens * 0.0002) / 1000
        LLM_COST.labels(provider='huggingface', model=model).inc(cost)
        
        return response
    except RateLimitError:
        LLM_RATE_LIMIT_HITS.labels(provider='huggingface').inc()
        raise
```

### Infrastructure Metrics

```python
# infrastructure_metrics.py
from prometheus_client import Gauge, Counter

# Database metrics
DB_CONNECTIONS_ACTIVE = Gauge(
    'kosmos_db_connections_active',
    'Active database connections',
    ['database', 'pool']
)

DB_CONNECTIONS_IDLE = Gauge(
    'kosmos_db_connections_idle',
    'Idle database connections',
    ['database', 'pool']
)

DB_QUERY_DURATION = Histogram(
    'kosmos_db_query_duration_seconds',
    'Database query duration',
    ['database', 'operation'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

# Cache metrics
CACHE_HIT_RATIO = Gauge(
    'kosmos_cache_hit_ratio',
    'Cache hit ratio',
    ['cache']
)

CACHE_MEMORY_BYTES = Gauge(
    'kosmos_cache_memory_bytes',
    'Cache memory usage in bytes',
    ['cache']
)

# Queue metrics
QUEUE_DEPTH = Gauge(
    'kosmos_queue_depth',
    'Message queue depth',
    ['queue', 'stream']
)

QUEUE_CONSUMER_LAG = Gauge(
    'kosmos_queue_consumer_lag',
    'Consumer lag in messages',
    ['queue', 'consumer']
)

# Storage metrics
STORAGE_BYTES = Gauge(
    'kosmos_storage_bytes_total',
    'Total storage used in bytes',
    ['bucket', 'storage_class']
)

STORAGE_OBJECTS = Gauge(
    'kosmos_storage_objects_total',
    'Total number of objects',
    ['bucket']
)
```

---

## Recording Rules

```yaml
# recording-rules.yml
groups:
  - name: kosmos-agent-rules
    interval: 30s
    rules:
      # Request rate per agent
      - record: kosmos:agent_request_rate:5m
        expr: sum(rate(kosmos_agent_requests_total[5m])) by (agent)

      # Error rate per agent
      - record: kosmos:agent_error_rate:5m
        expr: |
          sum(rate(kosmos_agent_requests_total{status="error"}[5m])) by (agent)
          /
          sum(rate(kosmos_agent_requests_total[5m])) by (agent)

      # P99 latency per agent
      - record: kosmos:agent_latency_p99:5m
        expr: |
          histogram_quantile(0.99, 
            sum(rate(kosmos_agent_request_duration_seconds_bucket[5m])) by (agent, le)
          )

      # P50 latency per agent
      - record: kosmos:agent_latency_p50:5m
        expr: |
          histogram_quantile(0.50, 
            sum(rate(kosmos_agent_request_duration_seconds_bucket[5m])) by (agent, le)
          )

  - name: kosmos-llm-rules
    interval: 30s
    rules:
      # Token rate per model
      - record: kosmos:llm_token_rate:5m
        expr: sum(rate(kosmos_llm_tokens_total[5m])) by (model, direction)

      # Cost rate per model (dollars/hour)
      - record: kosmos:llm_cost_rate_hourly:5m
        expr: sum(rate(kosmos_llm_cost_dollars_total[5m])) by (model) * 3600

      # Cache hit ratio
      - record: kosmos:llm_cache_hit_ratio:5m
        expr: |
          sum(rate(kosmos_llm_cache_hits_total[5m]))
          /
          (sum(rate(kosmos_llm_cache_hits_total[5m])) + sum(rate(kosmos_llm_cache_misses_total[5m])))

      # LLM P99 latency
      - record: kosmos:llm_latency_p99:5m
        expr: |
          histogram_quantile(0.99, 
            sum(rate(kosmos_llm_latency_seconds_bucket[5m])) by (model, le)
          )

  - name: kosmos-slo-rules
    interval: 30s
    rules:
      # Availability (% of time up)
      - record: kosmos:availability:30d
        expr: avg_over_time(up{job="kosmos-agents"}[30d])

      # Error budget remaining
      - record: kosmos:error_budget_remaining:30d
        expr: |
          1 - (
            sum(increase(kosmos_agent_requests_total{status="error"}[30d]))
            /
            sum(increase(kosmos_agent_requests_total[30d]))
          ) / 0.001  # 99.9% SLO = 0.1% error budget
```

---

## Common PromQL Queries

### Agent Performance

```promql
# Request rate by agent (last 5 minutes)
sum(rate(kosmos_agent_requests_total[5m])) by (agent)

# Error rate percentage
100 * sum(rate(kosmos_agent_requests_total{status="error"}[5m])) by (agent)
/ sum(rate(kosmos_agent_requests_total[5m])) by (agent)

# P99 latency by agent
histogram_quantile(0.99, sum(rate(kosmos_agent_request_duration_seconds_bucket[5m])) by (agent, le))

# Active sessions
sum(kosmos_agent_active_sessions) by (agent)

# Top 5 slowest agents
topk(5, histogram_quantile(0.99, sum(rate(kosmos_agent_request_duration_seconds_bucket[5m])) by (agent, le)))
```

### LLM Usage

```promql
# Token usage rate (tokens/second)
sum(rate(kosmos_llm_tokens_total[5m])) by (model, direction)

# Estimated hourly cost
sum(rate(kosmos_llm_cost_dollars_total[5m])) * 3600

# Cache hit ratio
sum(rate(kosmos_llm_cache_hits_total[5m])) 
/ (sum(rate(kosmos_llm_cache_hits_total[5m])) + sum(rate(kosmos_llm_cache_misses_total[5m])))

# LLM latency distribution
histogram_quantile(0.50, sum(rate(kosmos_llm_latency_seconds_bucket[5m])) by (le))  # P50
histogram_quantile(0.95, sum(rate(kosmos_llm_latency_seconds_bucket[5m])) by (le))  # P95
histogram_quantile(0.99, sum(rate(kosmos_llm_latency_seconds_bucket[5m])) by (le))  # P99
```

### Infrastructure Health

```promql
# Database connection pool utilization
kosmos_db_connections_active / (kosmos_db_connections_active + kosmos_db_connections_idle)

# Cache hit ratio
kosmos_cache_hit_ratio

# Queue depth (should be low)
kosmos_queue_depth

# Consumer lag (should be near zero)
kosmos_queue_consumer_lag

# Storage growth rate (bytes/hour)
rate(kosmos_storage_bytes_total[1h]) * 3600
```

### SLO Tracking

```promql
# Current availability (30-day window)
avg_over_time(up{job="kosmos-agents"}[30d]) * 100

# Error budget consumption (30-day window)
# SLO: 99.9% availability = 0.1% error budget
100 * (
  sum(increase(kosmos_agent_requests_total{status="error"}[30d]))
  / sum(increase(kosmos_agent_requests_total[30d]))
) / 0.001

# Burn rate (how fast error budget is being consumed)
sum(rate(kosmos_agent_requests_total{status="error"}[1h]))
/ sum(rate(kosmos_agent_requests_total[1h]))
/ 0.001 * 720  # 720 = 30 days in hours
```

---

## Metric Endpoints

### FastAPI Integration

```python
# metrics_endpoint.py
from fastapi import FastAPI
from prometheus_client import make_asgi_app, REGISTRY
from prometheus_client.multiprocess import MultiProcessCollector

app = FastAPI()

# Add prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Custom health endpoint with metrics
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "metrics": {
            "active_sessions": AGENT_ACTIVE_SESSIONS._value.get(),
            "request_count": AGENT_REQUESTS._value.sum()
        }
    }
```

### Kubernetes ServiceMonitor

```yaml
# servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: kosmos-agents
  namespace: kosmos-observability
  labels:
    release: prometheus
spec:
  selector:
    matchLabels:
      app.kubernetes.io/component: agent
  namespaceSelector:
    matchNames:
      - kosmos-core
  endpoints:
  - port: metrics
    interval: 15s
    path: /metrics
    scheme: http
```

---

## Best Practices

### Naming Conventions

```
# Format: <namespace>_<subsystem>_<name>_<unit>

# Good examples:
kosmos_agent_requests_total
kosmos_llm_tokens_total
kosmos_db_query_duration_seconds
kosmos_cache_memory_bytes

# Bad examples:
requests                    # Missing namespace
agent_request_count        # Missing namespace, use _total suffix
llm_latency_ms             # Use base units (seconds, not ms)
```

### Cardinality Management

```python
# AVOID high cardinality labels
# Bad: user_id as label (millions of unique values)
REQUESTS.labels(user_id=user.id).inc()  # DON'T DO THIS

# Good: aggregate by user type or tier
REQUESTS.labels(user_tier=user.tier).inc()  # tier: free/pro/enterprise

# Track unique users separately
UNIQUE_USERS = Gauge('kosmos_unique_users_total', 'Unique users')
```

---

## Related Documentation

- [Grafana Dashboards](dashboards)
- [Alerting Rules](alerting)
- [SLA/SLO Definitions](../sla-slo)

---

**Document Owner:** sre@nuvanta-holding.com
