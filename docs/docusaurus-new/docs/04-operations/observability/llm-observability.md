# LLM Observability

**Document Type:** Operations Guide  
**Owner:** MLOps Team  
**Last Updated:** 2025-12-13  
**Status:** 🟢 Active

---

## Overview

KOSMOS uses Langfuse for LLM-specific observability, providing visibility into prompt performance, token usage, costs, and model behavior. This complements general observability (Prometheus, Jaeger) with AI-specific insights.

---

## Langfuse Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      LLM Observability Stack                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                       Langfuse UI                                │   │
│   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐    │   │
│   │   │   Traces    │  │  Prompts    │  │    Evaluations      │    │   │
│   │   │   & Spans   │  │  Playground │  │    & Scoring        │    │   │
│   │   └─────────────┘  └─────────────┘  └─────────────────────┘    │   │
│   └───────────────────────────┬─────────────────────────────────────┘   │
│                               │                                          │
│   ┌───────────────────────────┼─────────────────────────────────────┐   │
│   │                  Langfuse Backend                                │   │
│   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐    │   │
│   │   │    API      │  │   Worker    │  │    PostgreSQL       │    │   │
│   │   │   Server    │  │  (Async)    │  │    (Storage)        │    │   │
│   │   └──────┬──────┘  └─────────────┘  └─────────────────────┘    │   │
│   └──────────┼──────────────────────────────────────────────────────┘   │
│              │                                                           │
│   ┌──────────┼──────────────────────────────────────────────────────┐   │
│   │          │            Application Layer                          │   │
│   │   ┌──────▼──────┐  ┌─────────────┐  ┌─────────────────────┐    │   │
│   │   │   Zeus      │  │   Athena    │  │      Hermes         │    │   │
│   │   │ (LangGraph) │  │   (RAG)     │  │   (Communications)  │    │   │
│   │   └─────────────┘  └─────────────┘  └─────────────────────┘    │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Integration

### Python SDK Setup

```python
# langfuse_config.py
import os
from langfuse import Langfuse
from langfuse.decorators import langfuse_context, observe

# Initialize Langfuse client
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
)

# Verify connection
langfuse.auth_check()
```

### LangGraph Integration

```python
# langgraph_tracing.py
from langfuse.callback import CallbackHandler
from langgraph.graph import StateGraph

# Create Langfuse callback handler
langfuse_handler = CallbackHandler(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
    session_id=session_id,
    user_id=user_id,
    metadata={
        "tenant_id": tenant_id,
        "agent": "zeus",
        "environment": os.getenv("ENVIRONMENT"),
    }
)

# Use with LangGraph
async def run_graph(input_data: dict):
    config = {
        "callbacks": [langfuse_handler],
        "configurable": {"thread_id": thread_id}
    }
    
    result = await graph.ainvoke(input_data, config=config)
    
    # Flush traces
    langfuse_handler.flush()
    
    return result
```

### Decorator-Based Tracing

```python
# traced_functions.py
from langfuse.decorators import observe, langfuse_context

@observe(name="semantic_search")
async def semantic_search(query: str, top_k: int = 10):
    """Search with automatic tracing."""
    # Add custom metadata
    langfuse_context.update_current_observation(
        metadata={
            "query_length": len(query),
            "top_k": top_k,
        }
    )
    
    results = await vector_store.search(query, top_k)
    
    # Update with results
    langfuse_context.update_current_observation(
        metadata={
            "result_count": len(results),
        }
    )
    
    return results

@observe(name="generate_response", as_type="generation")
async def generate_response(prompt: str, model: str = "mistral-7b"):
    """LLM call with generation tracking."""
    langfuse_context.update_current_observation(
        model=model,
        model_parameters={
            "temperature": 0.7,
            "max_tokens": 1024,
        },
        input=prompt,
    )
    
    response = await llm_client.generate(prompt, model=model)
    
    langfuse_context.update_current_observation(
        output=response.text,
        usage={
            "input": response.input_tokens,
            "output": response.output_tokens,
            "total": response.total_tokens,
        }
    )
    
    return response.text
```

---

## Trace Hierarchy

### Trace Structure

```
Trace: User Request (trace_id, session_id, user_id)
│
├── Span: Agent Orchestration
│   ├── Generation: Route Decision LLM Call
│   │   ├── Input: "User wants to search knowledge base"
│   │   ├── Output: "Route to Athena"
│   │   └── Usage: {input: 50, output: 10, total: 60}
│   │
│   └── Span: Athena Processing
│       ├── Span: Semantic Search
│       │   └── Metadata: {query_length: 45, results: 5}
│       │
│       └── Generation: Response Synthesis
│           ├── Input: Context + Query
│           ├── Output: Final Response
│           └── Usage: {input: 2000, output: 500, total: 2500}
│
└── Score: User Feedback (rating: 4/5)
```

### Creating Traces Manually

```python
# manual_tracing.py
from langfuse import Langfuse

langfuse = Langfuse()

def process_request(request_id: str, user_id: str, input_text: str):
    # Create trace
    trace = langfuse.trace(
        id=request_id,
        name="user_request",
        user_id=user_id,
        session_id=session_id,
        metadata={
            "tenant_id": tenant_id,
            "source": "api",
        },
        input=input_text,
    )
    
    # Create span for processing
    span = trace.span(
        name="orchestration",
        metadata={"agent": "zeus"},
    )
    
    # Create generation for LLM call
    generation = span.generation(
        name="route_decision",
        model="mistral-7b",
        model_parameters={"temperature": 0.7},
        input=[{"role": "user", "content": input_text}],
    )
    
    # ... LLM call ...
    
    # Update generation with output
    generation.end(
        output={"content": llm_response},
        usage={"input": 100, "output": 50, "total": 150},
    )
    
    # End span
    span.end()
    
    # Update trace with final output
    trace.update(
        output=final_response,
        metadata={"route": selected_agent},
    )
    
    return final_response
```

---

## Prompt Management

### Prompt Versioning

```python
# prompt_management.py
from langfuse import Langfuse

langfuse = Langfuse()

# Get prompt by name and version
def get_prompt(name: str, version: int = None):
    """Fetch prompt from Langfuse."""
    prompt = langfuse.get_prompt(
        name=name,
        version=version,  # None = latest
        label="production",  # or "staging"
    )
    return prompt

# Using prompts
async def generate_with_managed_prompt(context: str, query: str):
    prompt = get_prompt("rag_synthesis")
    
    # Compile prompt with variables
    compiled = prompt.compile(
        context=context,
        query=query,
    )
    
    # Create generation linked to prompt
    generation = langfuse.generation(
        name="rag_synthesis",
        prompt=prompt,  # Links to prompt version
        input=compiled,
    )
    
    response = await llm_client.generate(compiled)
    
    generation.end(
        output=response.text,
        usage={"input": response.input_tokens, "output": response.output_tokens},
    )
    
    return response.text
```

### Prompt Templates

```yaml
# Stored in Langfuse UI
name: rag_synthesis
version: 3
label: production

template: |
  You are a helpful AI assistant. Use the following context to answer the user's question.
  
  Context:
  {{context}}
  
  User Question: {{query}}
  
  Instructions:
  - Answer based only on the provided context
  - If the context doesn't contain the answer, say so
  - Be concise and accurate
  
  Answer:

variables:
  - context
  - query

model_config:
  model: mistral-7b
  temperature: 0.3
  max_tokens: 1024
```

---

## Evaluations & Scoring

### Automated Scoring

```python
# evaluations.py
from langfuse import Langfuse

langfuse = Langfuse()

async def evaluate_response(trace_id: str, response: str, expected: str = None):
    """Add evaluation scores to a trace."""
    
    # Relevance score (0-1)
    relevance = await calculate_relevance(response)
    langfuse.score(
        trace_id=trace_id,
        name="relevance",
        value=relevance,
        comment="Semantic similarity to expected answer",
    )
    
    # Factuality score (0-1) 
    if expected:
        factuality = await check_factuality(response, expected)
        langfuse.score(
            trace_id=trace_id,
            name="factuality",
            value=factuality,
        )
    
    # Toxicity score (0-1, lower is better)
    toxicity = await check_toxicity(response)
    langfuse.score(
        trace_id=trace_id,
        name="toxicity",
        value=toxicity,
    )
    
    # Cost score (actual cost in dollars)
    langfuse.score(
        trace_id=trace_id,
        name="cost",
        value=calculate_cost(trace_id),
        data_type="NUMERIC",
    )
```

### User Feedback Integration

```python
# feedback.py
from fastapi import APIRouter
from langfuse import Langfuse

router = APIRouter()
langfuse = Langfuse()

@router.post("/feedback")
async def submit_feedback(
    trace_id: str,
    rating: int,  # 1-5
    comment: str = None,
):
    """Record user feedback as score."""
    langfuse.score(
        trace_id=trace_id,
        name="user_rating",
        value=rating / 5,  # Normalize to 0-1
        comment=comment,
    )
    
    # Also record as categorical
    langfuse.score(
        trace_id=trace_id,
        name="user_satisfaction",
        value="satisfied" if rating >= 4 else "unsatisfied",
        data_type="CATEGORICAL",
    )
    
    return {"status": "recorded"}
```

---

## Cost Tracking

### Token-Based Cost Calculation

```python
# cost_tracking.py
from langfuse import Langfuse

# Model pricing (per 1K tokens)
MODEL_PRICING = {
    "mistral-7b": {"input": 0.0001, "output": 0.0002},
    "mixtral-8x7b": {"input": 0.0002, "output": 0.0004},
    "gpt-4": {"input": 0.03, "output": 0.06},
}

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost for LLM call."""
    pricing = MODEL_PRICING.get(model, {"input": 0, "output": 0})
    
    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]
    
    return input_cost + output_cost

# Record cost with generation
generation.end(
    output=response.text,
    usage={
        "input": input_tokens,
        "output": output_tokens,
        "total": input_tokens + output_tokens,
        "total_cost": calculate_cost(model, input_tokens, output_tokens),
    }
)
```

### Cost Dashboard Queries

```sql
-- Daily cost by model
SELECT 
    DATE(created_at) as date,
    model,
    SUM(usage_total_cost) as total_cost,
    SUM(usage_input) as input_tokens,
    SUM(usage_output) as output_tokens
FROM generations
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at), model
ORDER BY date DESC;

-- Cost by user
SELECT 
    user_id,
    COUNT(*) as trace_count,
    SUM(usage_total_cost) as total_cost
FROM traces t
JOIN generations g ON t.id = g.trace_id
WHERE t.created_at > NOW() - INTERVAL '7 days'
GROUP BY user_id
ORDER BY total_cost DESC
LIMIT 10;
```

---

## Kubernetes Deployment

### Self-Hosted Langfuse

```yaml
# langfuse-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: langfuse
  namespace: kosmos-observability
spec:
  replicas: 2
  selector:
    matchLabels:
      app: langfuse
  template:
    metadata:
      labels:
        app: langfuse
    spec:
      containers:
      - name: langfuse
        image: langfuse/langfuse:latest
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: langfuse-secrets
              key: database-url
        - name: NEXTAUTH_SECRET
          valueFrom:
            secretKeyRef:
              name: langfuse-secrets
              key: nextauth-secret
        - name: NEXTAUTH_URL
          value: "https://langfuse.kosmos.nuvanta-holding.com"
        - name: SALT
          valueFrom:
            secretKeyRef:
              name: langfuse-secrets
              key: salt
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
  name: langfuse
  namespace: kosmos-observability
spec:
  selector:
    app: langfuse
  ports:
  - port: 3000
    targetPort: 3000
```

---

## Monitoring Queries

### Trace Analytics

```python
# analytics.py
from langfuse import Langfuse

langfuse = Langfuse()

# Get traces with filters
traces = langfuse.fetch_traces(
    name="user_request",
    user_id=user_id,
    from_timestamp=datetime.utcnow() - timedelta(days=7),
    to_timestamp=datetime.utcnow(),
    order_by="timestamp",
    limit=100,
)

# Analyze token usage
total_tokens = sum(
    t.usage.total for t in traces 
    if t.usage
)

# Analyze costs
total_cost = sum(
    t.usage.total_cost for t in traces 
    if t.usage and t.usage.total_cost
)

# Average latency
avg_latency = sum(
    (t.end_time - t.start_time).total_seconds() 
    for t in traces
) / len(traces)
```

### Prometheus Metrics Export

```python
# langfuse_metrics.py
from prometheus_client import Counter, Histogram, Gauge
from langfuse import Langfuse

# Export Langfuse data to Prometheus
LANGFUSE_TOKENS = Counter(
    'langfuse_tokens_total',
    'Total tokens from Langfuse',
    ['model', 'direction']
)

LANGFUSE_COST = Counter(
    'langfuse_cost_dollars_total',
    'Total cost from Langfuse',
    ['model']
)

LANGFUSE_LATENCY = Histogram(
    'langfuse_generation_latency_seconds',
    'Generation latency from Langfuse',
    ['model'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

async def sync_langfuse_metrics():
    """Sync Langfuse metrics to Prometheus."""
    langfuse = Langfuse()
    
    # Fetch recent generations
    generations = langfuse.fetch_generations(
        from_timestamp=datetime.utcnow() - timedelta(minutes=5),
        limit=1000,
    )
    
    for gen in generations:
        if gen.usage:
            LANGFUSE_TOKENS.labels(
                model=gen.model,
                direction='input'
            ).inc(gen.usage.input)
            
            LANGFUSE_TOKENS.labels(
                model=gen.model,
                direction='output'
            ).inc(gen.usage.output)
            
            if gen.usage.total_cost:
                LANGFUSE_COST.labels(model=gen.model).inc(gen.usage.total_cost)
        
        if gen.latency:
            LANGFUSE_LATENCY.labels(model=gen.model).observe(gen.latency)
```

---

## Best Practices

### Do's

- **Always flush** traces before request completion
- **Use session IDs** to group related traces
- **Add user IDs** for user-level analytics
- **Include metadata** for filtering and debugging
- **Score generations** for quality monitoring
- **Version prompts** for A/B testing

### Don'ts

- **Don't log PII** in trace inputs/outputs
- **Don't block** on Langfuse calls (use async)
- **Don't store credentials** in metadata
- **Don't over-sample** in production (use sampling)

---

## Related Documentation

- [Metrics & Prometheus](metrics)
- [Distributed Tracing](tracing)
- [Model Cards](../../03-engineering/model-cards/README)

---

**Document Owner:** mlops@nuvanta-holding.com
