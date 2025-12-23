# Langfuse Integration

**Document Type:** Operations Guide  
**Owner:** MLOps Team  
**Last Updated:** 2025-12-13  
**Status:** 🟢 Active

---

## Overview

Langfuse provides LLM observability, prompt management, and evaluation capabilities for KOSMOS. It enables tracing of LLM interactions, cost tracking, prompt versioning, and quality evaluation across all AI agents.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Langfuse Integration Architecture                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                     KOSMOS Agents                                │   │
│   ├─────────────┬─────────────┬─────────────┬─────────────┬─────────┤   │
│   │    Zeus     │   Athena    │   Hermes    │   Apollo    │   ...   │   │
│   │ Orchestrator│  Knowledge  │   Comms     │  Analytics  │         │   │
│   └──────┬──────┴──────┬──────┴──────┬──────┴──────┬──────┴─────────┘   │
│          │             │             │             │                    │
│          └─────────────┴──────┬──────┴─────────────┘                    │
│                               │                                          │
│                    ┌──────────▼──────────┐                              │
│                    │  Langfuse SDK       │                              │
│                    │  (Python Client)    │                              │
│                    └──────────┬──────────┘                              │
│                               │                                          │
│                    ┌──────────▼──────────┐                              │
│                    │   Langfuse Cloud    │                              │
│                    │   or Self-Hosted    │                              │
│                    │                     │                              │
│                    │  ┌───────────────┐  │                              │
│                    │  │    Traces     │  │                              │
│                    │  ├───────────────┤  │                              │
│                    │  │    Prompts    │  │                              │
│                    │  ├───────────────┤  │                              │
│                    │  │  Evaluations  │  │                              │
│                    │  ├───────────────┤  │                              │
│                    │  │   Datasets    │  │                              │
│                    │  └───────────────┘  │                              │
│                    └────────────────────┘                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Deployment Options

### Option 1: Langfuse Cloud (Recommended for Staging/Dev)

```python
# Configuration for Langfuse Cloud
LANGFUSE_PUBLIC_KEY = "pk-lf-..."
LANGFUSE_SECRET_KEY = "sk-lf-..."
LANGFUSE_HOST = "https://cloud.langfuse.com"
```

### Option 2: Self-Hosted (Recommended for Production)

```yaml
# langfuse-deployment.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: langfuse
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: langfuse
  namespace: langfuse
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
        image: langfuse/langfuse:2
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: langfuse-secrets
              key: database-url
        - name: NEXTAUTH_URL
          value: "https://langfuse.kosmos.nuvanta-holding.com"
        - name: NEXTAUTH_SECRET
          valueFrom:
            secretKeyRef:
              name: langfuse-secrets
              key: nextauth-secret
        - name: SALT
          valueFrom:
            secretKeyRef:
              name: langfuse-secrets
              key: salt
        - name: ENCRYPTION_KEY
          valueFrom:
            secretKeyRef:
              name: langfuse-secrets
              key: encryption-key
        resources:
          requests:
            cpu: "200m"
            memory: "512Mi"
          limits:
            cpu: "1"
            memory: "2Gi"
---
apiVersion: v1
kind: Service
metadata:
  name: langfuse
  namespace: langfuse
spec:
  selector:
    app: langfuse
  ports:
  - port: 3000
    targetPort: 3000
---
apiVersion: traefik.containo.us/v1alpha1
kind: IngressRoute
metadata:
  name: langfuse
  namespace: langfuse
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`langfuse.kosmos.nuvanta-holding.com`)
      kind: Rule
      services:
        - name: langfuse
          port: 3000
  tls:
    secretName: langfuse-tls
```

---

## SDK Integration

### Installation

```bash
pip install langfuse
```

### Basic Configuration

```python
# langfuse_config.py
import os
from langfuse import Langfuse

# Initialize Langfuse client
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
)

# Verify connection
langfuse.auth_check()
```

### LangChain Integration

```python
# langchain_integration.py
from langfuse.callback import CallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

# Create Langfuse callback handler
langfuse_handler = CallbackHandler(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
)

# Use with LangChain
llm = ChatOpenAI(
    model="gpt-4",
    callbacks=[langfuse_handler],
)

response = llm([HumanMessage(content="Hello, world!")])
```

### LangGraph Integration

```python
# langgraph_integration.py
from langfuse.decorators import observe, langfuse_context
from langgraph.graph import StateGraph, END
from typing import TypedDict

class AgentState(TypedDict):
    messages: list
    context: dict
    
@observe(as_type="generation")
async def call_llm(state: AgentState) -> AgentState:
    """LLM call with automatic Langfuse tracing."""
    # Add metadata to trace
    langfuse_context.update_current_observation(
        metadata={
            "agent": "zeus",
            "task_type": "orchestration",
        }
    )
    
    response = await llm.ainvoke(state["messages"])
    
    # Track token usage
    langfuse_context.update_current_observation(
        usage={
            "input": response.usage.prompt_tokens,
            "output": response.usage.completion_tokens,
        }
    )
    
    return {"messages": state["messages"] + [response]}

@observe()
async def process_request(request: dict) -> dict:
    """Main request handler with full trace."""
    langfuse_context.update_current_trace(
        user_id=request.get("user_id"),
        session_id=request.get("session_id"),
        tags=["production", "zeus-orchestrator"],
    )
    
    # Build and run graph
    graph = StateGraph(AgentState)
    graph.add_node("llm", call_llm)
    graph.set_entry_point("llm")
    graph.add_edge("llm", END)
    
    app = graph.compile()
    result = await app.ainvoke({"messages": [request["message"]], "context": {}})
    
    return result
```

---

## Tracing

### Trace Hierarchy

```
Trace (Request)
├── Span (Agent Processing)
│   ├── Generation (LLM Call 1)
│   │   ├── Input tokens: 150
│   │   ├── Output tokens: 200
│   │   └── Latency: 1.2s
│   ├── Span (Tool Execution)
│   │   └── Event (Database Query)
│   └── Generation (LLM Call 2)
│       ├── Input tokens: 300
│       ├── Output tokens: 150
│       └── Latency: 0.8s
└── Score (Quality Evaluation)
```

### Manual Tracing

```python
# manual_tracing.py
from langfuse import Langfuse

langfuse = Langfuse()

def process_with_tracing(user_input: str, user_id: str):
    # Create trace
    trace = langfuse.trace(
        name="user-request",
        user_id=user_id,
        metadata={"source": "api", "version": "1.0.0"},
        tags=["production"],
    )
    
    # Create span for preprocessing
    preprocess_span = trace.span(
        name="preprocessing",
        input={"raw_input": user_input},
    )
    processed_input = preprocess(user_input)
    preprocess_span.end(output={"processed_input": processed_input})
    
    # Create generation for LLM call
    generation = trace.generation(
        name="main-llm-call",
        model="mistral-7b",
        model_parameters={"temperature": 0.7, "max_tokens": 500},
        input=[{"role": "user", "content": processed_input}],
    )
    
    # Call LLM
    response = call_llm(processed_input)
    
    # End generation with output and usage
    generation.end(
        output=response.content,
        usage={
            "input": response.usage.prompt_tokens,
            "output": response.usage.completion_tokens,
            "total": response.usage.total_tokens,
        },
        metadata={"finish_reason": response.finish_reason},
    )
    
    # Add score
    trace.score(
        name="user-feedback",
        value=1,  # 1 = positive, 0 = negative
        comment="User marked as helpful",
    )
    
    return response.content
```

### Trace Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | string | Descriptive name for the trace |
| `user_id` | string | User identifier for filtering |
| `session_id` | string | Session grouping |
| `input` | any | Request input data |
| `output` | any | Response output data |
| `metadata` | dict | Custom key-value pairs |
| `tags` | list | Filterable tags |
| `version` | string | Application version |

---

## Prompt Management

### Creating Prompts

```python
# prompt_management.py
from langfuse import Langfuse

langfuse = Langfuse()

# Create a prompt
langfuse.create_prompt(
    name="zeus-routing",
    prompt="""You are Zeus, the orchestrator agent for KOSMOS.
    
Your task is to analyze the user request and route it to the appropriate specialist agent.

Available agents:
- athena: Knowledge retrieval and document analysis
- hermes: Communication and messaging
- apollo: Analytics and reporting
- hephaestus: Development and code generation

User request: {{user_request}}

Respond with JSON containing:
- target_agent: The agent to route to
- reasoning: Brief explanation of your choice
- context: Any context to pass to the target agent
""",
    config={
        "model": "mistral-7b",
        "temperature": 0.3,
        "max_tokens": 200,
    },
    labels=["production"],
)
```

### Using Prompts

```python
# Using managed prompts
def route_request(user_request: str) -> dict:
    # Fetch prompt from Langfuse
    prompt = langfuse.get_prompt("zeus-routing")
    
    # Compile with variables
    compiled_prompt = prompt.compile(user_request=user_request)
    
    # Create generation linked to prompt
    generation = langfuse.generation(
        name="routing-decision",
        prompt=prompt,  # Links to prompt version
        input=compiled_prompt,
    )
    
    # Call LLM
    response = call_llm(compiled_prompt, **prompt.config)
    
    generation.end(output=response)
    
    return json.loads(response)
```

### Prompt Versioning

```python
# Version management
# Langfuse automatically versions prompts

# Get specific version
prompt_v1 = langfuse.get_prompt("zeus-routing", version=1)

# Get production version (labeled)
prompt_prod = langfuse.get_prompt("zeus-routing", label="production")

# Promote to production
langfuse.create_prompt(
    name="zeus-routing",
    prompt="...",
    labels=["production"],  # This becomes the new production version
)
```

---

## Evaluations

### Automated Scoring

```python
# evaluations.py
from langfuse import Langfuse
from langfuse.decorators import observe

langfuse = Langfuse()

@observe()
async def evaluate_response(trace_id: str, response: str, expected: str):
    """Evaluate response quality."""
    
    # Semantic similarity score
    similarity = calculate_similarity(response, expected)
    langfuse.score(
        trace_id=trace_id,
        name="semantic-similarity",
        value=similarity,
    )
    
    # Factual accuracy (using LLM as judge)
    accuracy_prompt = f"""
    Evaluate the factual accuracy of this response:
    Response: {response}
    Expected: {expected}
    
    Score from 0 to 1 where 1 is perfectly accurate.
    """
    accuracy = await llm_judge(accuracy_prompt)
    langfuse.score(
        trace_id=trace_id,
        name="factual-accuracy",
        value=accuracy,
    )
    
    # Toxicity check
    toxicity = check_toxicity(response)
    langfuse.score(
        trace_id=trace_id,
        name="toxicity",
        value=1 - toxicity,  # Higher is better (less toxic)
    )
```

### Human Evaluation Pipeline

```python
# human_evaluation.py
def create_evaluation_dataset():
    """Create dataset for human evaluation."""
    
    dataset = langfuse.create_dataset(
        name="zeus-routing-evaluation",
        description="Evaluation dataset for Zeus routing decisions",
    )
    
    # Add items from production traces
    traces = langfuse.fetch_traces(
        name="user-request",
        tags=["production"],
        limit=100,
    )
    
    for trace in traces:
        langfuse.create_dataset_item(
            dataset_name="zeus-routing-evaluation",
            input=trace.input,
            expected_output=trace.output,
            metadata={"trace_id": trace.id},
        )
    
    return dataset

def run_evaluation(dataset_name: str):
    """Run evaluation on dataset."""
    
    dataset = langfuse.get_dataset(dataset_name)
    
    for item in dataset.items:
        # Run current model
        with langfuse.trace(name="evaluation-run") as trace:
            result = process_request(item.input)
            
            # Compare with expected
            trace.score(
                name="matches-expected",
                value=1 if result == item.expected_output else 0,
            )
```

### Score Types

| Score Name | Range | Description |
|------------|-------|-------------|
| `semantic-similarity` | 0-1 | Embedding-based similarity |
| `factual-accuracy` | 0-1 | LLM-judged accuracy |
| `toxicity` | 0-1 | Toxicity detection (higher = safer) |
| `user-feedback` | 0-1 | User thumbs up/down |
| `latency-sla` | 0-1 | Met latency SLA |
| `cost-efficiency` | 0-1 | Cost vs. budget |

---

## Datasets

### Creating Test Datasets

```python
# datasets.py
def create_routing_dataset():
    """Create golden dataset for routing tests."""
    
    dataset = langfuse.create_dataset(
        name="routing-golden-set",
        description="Golden test cases for Zeus routing",
    )
    
    test_cases = [
        {
            "input": "Can you summarize the Q3 report?",
            "expected": {"target_agent": "athena", "task": "summarization"},
        },
        {
            "input": "Send an email to the team about the meeting",
            "expected": {"target_agent": "hermes", "task": "email"},
        },
        {
            "input": "Show me sales trends for last month",
            "expected": {"target_agent": "apollo", "task": "analytics"},
        },
    ]
    
    for case in test_cases:
        langfuse.create_dataset_item(
            dataset_name="routing-golden-set",
            input=case["input"],
            expected_output=case["expected"],
        )
```

### Running Experiments

```python
# experiments.py
async def run_experiment(dataset_name: str, model_version: str):
    """Run A/B experiment with new model version."""
    
    dataset = langfuse.get_dataset(dataset_name)
    
    results = []
    for item in dataset.items:
        trace = langfuse.trace(
            name="experiment",
            metadata={
                "experiment": f"routing-{model_version}",
                "dataset_item_id": item.id,
            },
        )
        
        result = await process_request(item.input)
        
        # Score against expected
        is_correct = result == item.expected_output
        trace.score(name="correctness", value=1 if is_correct else 0)
        
        results.append({"item_id": item.id, "correct": is_correct})
    
    # Calculate aggregate metrics
    accuracy = sum(r["correct"] for r in results) / len(results)
    print(f"Model {model_version} accuracy: {accuracy:.2%}")
    
    return results
```

---

## Analytics Queries

### Cost Analysis

```python
# Query cost by model
traces = langfuse.fetch_traces(
    from_timestamp=datetime.now() - timedelta(days=7),
)

cost_by_model = {}
for trace in traces:
    for gen in trace.observations:
        if gen.type == "GENERATION":
            model = gen.model
            cost = calculate_cost(gen.usage)
            cost_by_model[model] = cost_by_model.get(model, 0) + cost

print("Cost by model (last 7 days):")
for model, cost in sorted(cost_by_model.items(), key=lambda x: -x[1]):
    print(f"  {model}: ${cost:.2f}")
```

### Latency Analysis

```python
# Query latency percentiles
traces = langfuse.fetch_traces(
    name="user-request",
    from_timestamp=datetime.now() - timedelta(days=1),
)

latencies = [t.latency for t in traces if t.latency]
p50 = np.percentile(latencies, 50)
p95 = np.percentile(latencies, 95)
p99 = np.percentile(latencies, 99)

print(f"Latency (last 24h): P50={p50:.2f}s, P95={p95:.2f}s, P99={p99:.2f}s")
```

---

## Access URLs

| Environment | URL | Purpose |
|-------------|-----|---------|
| Development | http://localhost:3001 | Local Langfuse |
| Staging | https://langfuse.staging.kosmos.nuvanta-holding.com | Staging traces |
| Production | https://langfuse.kosmos.nuvanta-holding.com | Production observability |

---

## Related Documentation

- [Prometheus Setup](prometheus)
- [LLM Operations Dashboard](grafana#llm-operations-dashboard)
- [Model Cards](../../03-engineering/model-cards/README)

---

**Document Owner:** mlops@nuvanta-holding.com
