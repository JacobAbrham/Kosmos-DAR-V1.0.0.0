# Cloud Inference Strategy

!!! info "LiteLLM-Centric Architecture"
    KOSMOS uses LiteLLM as the unified gateway for all LLM inference, providing intelligent model routing, cost optimization, and observability integration.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    LLM INFERENCE LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                      ┌─────────────┐                           │
│                      │   LiteLLM   │                           │
│                      │   Gateway   │                           │
│                      └──────┬──────┘                           │
│                             │                                   │
│         ┌───────────────────┼───────────────────┐              │
│         │                   │                   │              │
│         ▼                   ▼                   ▼              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │   Ollama    │    │  HuggingFace│    │   Groq/     │        │
│  │   (Local)   │    │  Inference  │    │  Cerebras   │        │
│  │             │    │  Endpoints  │    │  (Fallback) │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│                                                                 │
│  Models:            Models:            Models:                  │
│  • llama3.2:3b     • Mistral-7B       • llama-3.1-70b         │
│  • nomic-embed     • Qwen-72B         • mixtral-8x7b          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Model Routing Strategy

### Tiered Model Selection

| Tier | Use Case | Model | Cost | Latency |
|------|----------|-------|------|---------|
| **Tier 1** | Complex reasoning | qwen-72b-chat | $$$$ | High |
| **Tier 2** | General tasks | mistral-7b-instruct | $$ | Medium |
| **Tier 3** | Simple/Fast | llama3.2:3b (local) | Free | Low |
| **Embed** | Vector search | nomic-embed-text | Free | Low |

### Routing Logic

```python
def route_model(task_type: str, complexity: str, latency_req: str) -> str:
    """Route to appropriate model based on requirements."""
    
    if task_type == "embedding":
        return "ollama/nomic-embed-text"
    
    if complexity == "high" or task_type in ["reasoning", "analysis"]:
        return "huggingface/Qwen/Qwen2.5-72B-Instruct"
    
    if latency_req == "low" or task_type in ["classification", "extraction"]:
        return "ollama/llama3.2:3b"
    
    # Default: balanced choice
    return "huggingface/mistralai/Mistral-7B-Instruct-v0.3"
```

## LiteLLM Configuration

```yaml
# litellm-config.yaml
model_list:
  # Local models (Ollama)
  - model_name: llama3.2:3b
    litellm_params:
      model: ollama/llama3.2:3b
      api_base: http://ollama:11434
      
  - model_name: nomic-embed-text
    litellm_params:
      model: ollama/nomic-embed-text
      api_base: http://ollama:11434

  # HuggingFace Inference Endpoints
  - model_name: mistral-7b
    litellm_params:
      model: huggingface/mistralai/Mistral-7B-Instruct-v0.3
      api_base: ${HF_ENDPOINT_URL}
      api_key: ${HF_API_KEY}
      
  - model_name: qwen-72b
    litellm_params:
      model: huggingface/Qwen/Qwen2.5-72B-Instruct
      api_base: ${HF_ENDPOINT_URL}
      api_key: ${HF_API_KEY}

  # Fallback providers
  - model_name: groq-llama
    litellm_params:
      model: groq/llama-3.1-70b-versatile
      api_key: ${GROQ_API_KEY}

litellm_settings:
  drop_params: true
  set_verbose: false
  
router_settings:
  routing_strategy: cost-based
  num_retries: 3
  timeout: 120
  fallbacks:
    - mistral-7b: [llama3.2:3b, groq-llama]
    - qwen-72b: [mistral-7b, groq-llama]
```

## Cost Management

### Budget Controls

```yaml
# cost-controls.yaml
budgets:
  daily_limit: 50.00      # USD
  weekly_limit: 250.00
  monthly_limit: 1000.00
  
alerts:
  - threshold: 0.8        # 80% of daily budget
    notify: [operator_alpha]
  - threshold: 0.95       # 95% of daily budget
    notify: [operator_alpha, operator_beta]
    action: throttle
```

## Resource Allocation

### Ollama (Local Inference)

| Resource | Allocation |
|----------|------------|
| RAM | 4 GB |
| VRAM | N/A (CPU mode) |
| CPU | 2 cores |
| Storage | 10 GB (models) |

### LiteLLM Gateway

| Resource | Allocation |
|----------|------------|
| RAM | 256 MB |
| CPU | 0.25 cores |
| Replicas | 1 (staging) |

## Observability

### Langfuse Integration

```yaml
# langfuse-config.yaml
langfuse:
  public_key: ${LANGFUSE_PUBLIC_KEY}
  secret_key: ${LANGFUSE_SECRET_KEY}
  host: http://langfuse:3000
  
  trace_config:
    sample_rate: 1.0      # 100% in staging
    include_prompts: true
    include_completions: true
```

### Key Metrics

| Metric | Description | Alert |
|--------|-------------|-------|
| `llm_request_duration` | Request latency | > 30s |
| `llm_token_usage` | Token consumption | Budget threshold |
| `llm_error_rate` | Error percentage | > 5% |
| `llm_cost_daily` | Daily spend | > 80% budget |

## Failover Strategy

```
Primary: HuggingFace Inference Endpoints
    │
    ├── [Timeout/Error] ──► Retry (3x)
    │
    ├── [Still Failing] ──► Fallback to Ollama (local)
    │
    └── [Ollama Overloaded] ──► Fallback to Groq/Cerebras
```

---

## See Also

- [LLM Provider Strategy ADR](adr/ADR-006-llm-provider-strategy.md)
- [Langfuse Integration](../04-operations/observability/langfuse.md)
- [Cost Governance](../01-governance/cost-governance.md)

---

**Last Updated:** December 2025
