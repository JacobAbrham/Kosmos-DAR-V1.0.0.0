# Distributed Tracing

**Document Type:** Operations Guide  
**Owner:** SRE Team  
**Last Updated:** 2025-12-13  
**Status:** 🟢 Active

---

## Overview

KOSMOS uses OpenTelemetry (OTLP) for distributed tracing with Jaeger as the backend. Tracing enables end-to-end visibility into request flows across the multi-agent architecture.

---

## Tracing Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Distributed Tracing Stack                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                         Jaeger UI                                │   │
│   │                 (Trace Visualization)                            │   │
│   └───────────────────────────┬─────────────────────────────────────┘   │
│                               │                                          │
│                               ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                      Jaeger Backend                              │   │
│   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐    │   │
│   │   │  Collector  │  │    Query    │  │    Storage          │    │   │
│   │   │   (OTLP)    │  │   Service   │  │  (Elasticsearch)    │    │   │
│   │   └──────┬──────┘  └─────────────┘  └─────────────────────┘    │   │
│   └──────────┼──────────────────────────────────────────────────────┘   │
│              │                                                           │
│   ┌──────────┼──────────────────────────────────────────────────────┐   │
│   │          │            OTEL Collector (Optional)                  │   │
│   │   ┌──────▼──────┐                                               │   │
│   │   │  Receivers  │  →  Processors  →  Exporters                  │   │
│   │   └─────────────┘                                               │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│              │                                                           │
│   ┌──────────▼──────────────────────────────────────────────────────┐   │
│   │                    Application Layer                             │   │
│   │   ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌────────────┐  │   │
│   │   │   Zeus    │  │  Athena   │  │  Hermes   │  │   Chronos  │  │   │
│   │   │  (OTLP)   │  │  (OTLP)   │  │  (OTLP)   │  │   (OTLP)   │  │   │
│   │   └───────────┘  └───────────┘  └───────────┘  └────────────┘  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Trace Context

### Trace Structure

```
Trace (trace_id: abc123)
│
├── Span: HTTP Request (span_id: span1, parent: none)
│   ├── Attributes: http.method=POST, http.url=/api/v1/orchestrate
│   │
│   └── Span: Zeus Orchestration (span_id: span2, parent: span1)
│       ├── Attributes: agent=zeus, operation=route
│       │
│       ├── Span: Athena Query (span_id: span3, parent: span2)
│       │   ├── Attributes: agent=athena, operation=search
│       │   │
│       │   └── Span: PostgreSQL Query (span_id: span4, parent: span3)
│       │       └── Attributes: db.system=postgresql, db.statement=SELECT...
│       │
│       └── Span: LLM Call (span_id: span5, parent: span2)
│           └── Attributes: llm.model=mistral-7b, llm.tokens=1234
```

### W3C Trace Context Headers

```http
traceparent: 00-abc123def456789012345678901234-span123456789012-01
tracestate: kosmos=agent:zeus
```

---

## OpenTelemetry Configuration

### Python SDK Setup

```python
# tracing.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat

def configure_tracing(service_name: str, version: str = "1.0.0"):
    """Configure OpenTelemetry tracing."""
    
    # Create resource with service info
    resource = Resource.create({
        SERVICE_NAME: service_name,
        SERVICE_VERSION: version,
        "deployment.environment": os.getenv("ENVIRONMENT", "development"),
        "service.namespace": "kosmos",
    })
    
    # Create tracer provider
    provider = TracerProvider(resource=resource)
    
    # Configure OTLP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger-collector:4317"),
        insecure=True,
    )
    
    # Add batch processor for efficiency
    provider.add_span_processor(
        BatchSpanProcessor(
            otlp_exporter,
            max_queue_size=2048,
            max_export_batch_size=512,
            schedule_delay_millis=5000,
        )
    )
    
    # Set global tracer provider
    trace.set_tracer_provider(provider)
    
    # Configure propagator (W3C TraceContext + B3 for compatibility)
    set_global_textmap(B3MultiFormat())
    
    return trace.get_tracer(service_name)

# Auto-instrumentation
def instrument_app(app):
    """Add automatic instrumentation."""
    FastAPIInstrumentor.instrument_app(app)
    HTTPXClientInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument()
```

### Manual Instrumentation

```python
# manual_tracing.py
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from functools import wraps

tracer = trace.get_tracer(__name__)

def traced(operation_name: str = None):
    """Decorator for tracing functions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            name = operation_name or func.__name__
            with tracer.start_as_current_span(name) as span:
                try:
                    result = await func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        return wrapper
    return decorator

# Usage
@traced("athena.semantic_search")
async def semantic_search(query: str, top_k: int = 10):
    span = trace.get_current_span()
    span.set_attribute("search.query_length", len(query))
    span.set_attribute("search.top_k", top_k)
    
    results = await vector_store.search(query, top_k)
    
    span.set_attribute("search.result_count", len(results))
    return results

# Context propagation
async def call_downstream_agent(agent: str, payload: dict):
    """Call another agent with trace context."""
    span = trace.get_current_span()
    span.set_attribute("downstream.agent", agent)
    
    # Headers automatically include trace context with instrumentation
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://{agent}:8000/api/v1/process",
            json=payload
        )
    return response.json()
```

### LLM Call Tracing

```python
# llm_tracing.py
from opentelemetry import trace
from opentelemetry.trace import SpanKind

tracer = trace.get_tracer("kosmos.llm")

async def traced_llm_call(
    prompt: str,
    model: str,
    **kwargs
) -> str:
    """Trace LLM API calls."""
    with tracer.start_as_current_span(
        "llm.generate",
        kind=SpanKind.CLIENT,
    ) as span:
        # Set semantic attributes
        span.set_attribute("llm.system", "huggingface")
        span.set_attribute("llm.model", model)
        span.set_attribute("llm.prompt.tokens", count_tokens(prompt))
        
        start_time = time.time()
        
        try:
            response = await llm_client.generate(
                prompt=prompt,
                model=model,
                **kwargs
            )
            
            # Record response metrics
            duration = time.time() - start_time
            span.set_attribute("llm.response.tokens", response.output_tokens)
            span.set_attribute("llm.duration_ms", duration * 1000)
            span.set_attribute("llm.total_tokens", response.total_tokens)
            
            # Add event for completion
            span.add_event("llm.completion", {
                "finish_reason": response.finish_reason
            })
            
            return response.text
            
        except Exception as e:
            span.record_exception(e)
            span.set_attribute("llm.error", str(e))
            raise
```

---

## Jaeger Configuration

### Kubernetes Deployment

```yaml
# jaeger-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger
  namespace: kosmos-observability
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jaeger
  template:
    metadata:
      labels:
        app: jaeger
    spec:
      containers:
      - name: jaeger
        image: jaegertracing/all-in-one:1.52
        env:
        - name: COLLECTOR_OTLP_ENABLED
          value: "true"
        - name: SPAN_STORAGE_TYPE
          value: "elasticsearch"
        - name: ES_SERVER_URLS
          value: "http://elasticsearch:9200"
        - name: ES_INDEX_PREFIX
          value: "jaeger"
        ports:
        - containerPort: 16686  # UI
          name: ui
        - containerPort: 4317   # OTLP gRPC
          name: otlp-grpc
        - containerPort: 4318   # OTLP HTTP
          name: otlp-http
        - containerPort: 14268  # Jaeger HTTP
          name: jaeger-http
        resources:
          requests:
            cpu: 200m
            memory: 512Mi
          limits:
            cpu: 1
            memory: 2Gi
---
apiVersion: v1
kind: Service
metadata:
  name: jaeger-collector
  namespace: kosmos-observability
spec:
  selector:
    app: jaeger
  ports:
  - name: otlp-grpc
    port: 4317
    targetPort: 4317
  - name: otlp-http
    port: 4318
    targetPort: 4318
---
apiVersion: v1
kind: Service
metadata:
  name: jaeger-ui
  namespace: kosmos-observability
spec:
  selector:
    app: jaeger
  ports:
  - name: ui
    port: 16686
    targetPort: 16686
```

### Sampling Configuration

```yaml
# jaeger-sampling.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: jaeger-sampling
  namespace: kosmos-observability
data:
  sampling.json: |
    {
      "service_strategies": [
        {
          "service": "zeus-orchestrator",
          "type": "probabilistic",
          "param": 1.0
        },
        {
          "service": "athena-knowledge",
          "type": "probabilistic",
          "param": 0.5
        }
      ],
      "default_strategy": {
        "type": "probabilistic",
        "param": 0.1
      }
    }
```

### Sampling Strategies

| Strategy | Use Case | Configuration |
|----------|----------|---------------|
| **Always** | Development, debugging | `param: 1.0` |
| **Probabilistic** | Production, high volume | `param: 0.1` (10%) |
| **Rate Limiting** | Cost control | `param: 100` (100/s) |
| **Adaptive** | Dynamic based on traffic | Jaeger Adaptive |

---

## Trace Attributes

### Standard Semantic Conventions

```python
# OpenTelemetry Semantic Conventions
from opentelemetry.semconv.trace import SpanAttributes

# HTTP
span.set_attribute(SpanAttributes.HTTP_METHOD, "POST")
span.set_attribute(SpanAttributes.HTTP_URL, "/api/v1/orchestrate")
span.set_attribute(SpanAttributes.HTTP_STATUS_CODE, 200)
span.set_attribute(SpanAttributes.HTTP_REQUEST_CONTENT_LENGTH, 1234)

# Database
span.set_attribute(SpanAttributes.DB_SYSTEM, "postgresql")
span.set_attribute(SpanAttributes.DB_NAME, "kosmos")
span.set_attribute(SpanAttributes.DB_STATEMENT, "SELECT * FROM...")
span.set_attribute(SpanAttributes.DB_OPERATION, "SELECT")

# Messaging
span.set_attribute(SpanAttributes.MESSAGING_SYSTEM, "nats")
span.set_attribute(SpanAttributes.MESSAGING_DESTINATION, "agent.events")
span.set_attribute(SpanAttributes.MESSAGING_OPERATION, "publish")
```

### KOSMOS Custom Attributes

```python
# Custom semantic conventions for KOSMOS
class KosmosAttributes:
    # Agent attributes
    AGENT_NAME = "kosmos.agent.name"
    AGENT_VERSION = "kosmos.agent.version"
    AGENT_OPERATION = "kosmos.agent.operation"
    
    # LLM attributes
    LLM_MODEL = "kosmos.llm.model"
    LLM_PROVIDER = "kosmos.llm.provider"
    LLM_PROMPT_TOKENS = "kosmos.llm.prompt_tokens"
    LLM_COMPLETION_TOKENS = "kosmos.llm.completion_tokens"
    LLM_TOTAL_TOKENS = "kosmos.llm.total_tokens"
    LLM_COST = "kosmos.llm.cost"
    
    # Tenant attributes
    TENANT_ID = "kosmos.tenant.id"
    USER_ID = "kosmos.user.id"
    
    # Routing attributes
    ROUTE_DECISION = "kosmos.route.decision"
    ROUTE_CONFIDENCE = "kosmos.route.confidence"

# Usage
span.set_attribute(KosmosAttributes.AGENT_NAME, "zeus")
span.set_attribute(KosmosAttributes.LLM_MODEL, "mistral-7b")
span.set_attribute(KosmosAttributes.TENANT_ID, tenant_id)
```

---

## Trace Analysis

### Jaeger UI Features

| Feature | Use Case |
|---------|----------|
| **Search** | Find traces by service, operation, tags |
| **Compare** | Side-by-side trace comparison |
| **Dependencies** | Service dependency graph |
| **Deep Dependency** | Trace-level dependencies |
| **Monitor** | RED metrics from traces |

### Common Search Queries

```
# Slow requests (> 500ms)
service=zeus-orchestrator AND minDuration=500ms

# Error traces
service=zeus-orchestrator AND error=true

# Specific user's traces
service=zeus-orchestrator AND kosmos.user.id=user123

# LLM calls with high token usage
service=athena-knowledge AND kosmos.llm.total_tokens&gt;5000

# Traces with specific route decision
service=zeus-orchestrator AND kosmos.route.decision=athena
```

---

## Grafana Integration

### Tempo/Jaeger Data Source

```yaml
# grafana-datasources.yaml
datasources:
  - name: Jaeger
    type: jaeger
    url: http://jaeger-ui:16686
    access: proxy
    jsonData:
      tracesToLogs:
        datasourceUid: loki
        tags: ['service', 'trace_id']
        mappedTags:
          - key: service
            value: app
        spanStartTimeShift: '-1h'
        spanEndTimeShift: '1h'
        filterByTraceID: true
        filterBySpanID: false
```

### Trace-to-Logs Correlation

```json
{
  "panels": [
    {
      "title": "Trace Timeline",
      "type": "traces",
      "datasource": "Jaeger",
      "targets": [
        {
          "query": "service=${service}",
          "limit": 20
        }
      ],
      "options": {
        "tracesToLogs": {
          "datasourceUid": "loki",
          "spanStartTimeShift": "-5m",
          "spanEndTimeShift": "5m",
          "tags": ["trace_id"]
        }
      }
    }
  ]
}
```

---

## Troubleshooting

### Missing Traces

```bash
# Check OTLP connectivity
curl -X POST http://jaeger-collector:4318/v1/traces \
  -H "Content-Type: application/json" \
  -d '{"resourceSpans":[]}'

# Verify pod can reach collector
kubectl exec -it zeus-0 -n kosmos-core -- \
  nc -zv jaeger-collector.kosmos-observability 4317

# Check for sampling (might be sampled out)
kubectl logs jaeger-0 -n kosmos-observability | grep "span"
```

### High Cardinality

```python
# AVOID: Dynamic values as span names
with tracer.start_span(f"process_{user_id}"):  # BAD
    pass

# GOOD: Use attributes for dynamic values
with tracer.start_span("process_user") as span:
    span.set_attribute("user.id", user_id)  # GOOD
```

---

## Related Documentation

- [Metrics & Prometheus](metrics)
- [Logging](logging)
- [LLM Observability](llm-observability)

---

**Document Owner:** sre@nuvanta-holding.com
