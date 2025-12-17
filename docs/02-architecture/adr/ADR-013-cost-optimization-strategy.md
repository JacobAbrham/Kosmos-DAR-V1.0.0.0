# ADR-013: Cost Optimization Strategy

**Status:** Accepted  
**Date:** 2025-12-13  
**Decision Makers:** Architecture Team, FinOps Team  

---

## Context

LLM inference costs represent 60-80% of KOSMOS operational expenses. Without proactive cost management, monthly costs could exceed $100,000 for moderate usage. We need strategies to optimize costs while maintaining service quality.

### Cost Drivers

| Component | % of Total | Growth Rate |
|-----------|------------|-------------|
| LLM API calls | 65% | High |
| Vector embeddings | 15% | Medium |
| Infrastructure | 12% | Low |
| Storage | 5% | Low |
| Network | 3% | Low |

### Options Considered

#### Option A: No Optimization

Pass all requests directly to LLM providers.

**Pros:**
- Simplest implementation
- No additional complexity

**Cons:**
- Highest cost (~$0.05 per request average)
- Linear cost scaling
- No cost predictability

#### Option B: Aggressive Caching Only

Cache all LLM responses.

**Pros:**
- Significant cost reduction (40-60%)
- Fast response for cached queries

**Cons:**
- High cache storage costs
- Stale responses for time-sensitive queries
- Low hit rate for unique queries

#### Option C: Multi-Layered Optimization (Selected)

Combine multiple strategies: semantic caching, model routing, prompt optimization, and usage controls.

**Pros:**
- 50-70% cost reduction
- Maintains quality for complex queries
- Provides cost predictability
- Enables per-tenant cost control

**Cons:**
- Implementation complexity
- Requires ongoing tuning
- Additional infrastructure

---

## Decision

We implement **Multi-Layered Cost Optimization** with the following strategies:

### 1. Semantic Cache

Cache responses based on query embedding similarity, not exact match.

```python
class SemanticCache:
    def __init__(self, similarity_threshold: float = 0.95):
        self.threshold = similarity_threshold
        self.redis = Redis()
        self.embedder = EmbeddingModel()
    
    async def get(self, query: str) -> Optional[str]:
        query_embedding = await self.embedder.embed(query)
        
        # Search for similar cached queries
        similar = await self.redis.ft().search(
            Query(f"@embedding:[VECTOR_RANGE 0.05 $vec]")
            .sort_by("__vector_score")
            .return_field("response")
            .dialect(2),
            {"vec": query_embedding.tobytes()}
        )
        
        if similar.docs and similar.docs[0].score >= self.threshold:
            return similar.docs[0].response
        return None
    
    async def set(self, query: str, response: str, ttl: int = 3600):
        embedding = await self.embedder.embed(query)
        await self.redis.hset(
            f"cache:{hash(query)}",
            mapping={"query": query, "response": response, "embedding": embedding}
        )
        await self.redis.expire(f"cache:{hash(query)}", ttl)
```

**Expected savings:** 30-40% of LLM costs

### 2. Intelligent Model Routing

Route requests to appropriate model based on complexity.

```python
class ModelRouter:
    """Route queries to cost-appropriate models"""
    
    MODELS = {
        "simple": {"name": "mistral-7b", "cost_per_1k": 0.0002},
        "medium": {"name": "claude-3-haiku", "cost_per_1k": 0.00025},
        "complex": {"name": "claude-3-sonnet", "cost_per_1k": 0.003},
        "expert": {"name": "claude-3-opus", "cost_per_1k": 0.015},
    }
    
    async def classify_complexity(self, query: str) -> str:
        """Classify query complexity"""
        # Fast heuristics first
        if len(query) < 50 and not any(kw in query.lower() for kw in ["analyze", "compare", "explain"]):
            return "simple"
        
        # Use classifier for ambiguous cases
        classification = await self.classifier.predict(query)
        return classification
    
    async def route(self, query: str, user_tier: str) -> dict:
        complexity = await self.classify_complexity(query)
        
        # Apply tier-based routing
        if user_tier == "free":
            return self.MODELS[min(complexity, "medium")]
        elif user_tier == "pro":
            return self.MODELS[complexity]
        else:  # enterprise
            return self.MODELS[complexity]  # No restrictions
```

**Expected savings:** 20-30% of LLM costs

### 3. Prompt Optimization

Reduce token usage through compression and optimization.

```python
class PromptOptimizer:
    """Optimize prompts to reduce token usage"""
    
    async def optimize(self, messages: list[dict]) -> list[dict]:
        optimized = []
        
        for msg in messages:
            content = msg["content"]
            
            # Remove redundant whitespace
            content = " ".join(content.split())
            
            # Compress conversation history (summarize old messages)
            if msg.get("summarizable"):
                content = await self.summarize(content)
            
            # Remove verbose system instructions for follow-ups
            if msg["role"] == "system" and self.is_continuation:
                content = self.compress_system_prompt(content)
            
            optimized.append({**msg, "content": content})
        
        return optimized
```

**Expected savings:** 10-15% of token costs

### 4. Usage Controls & Budgets

Implement per-tenant budgets and rate limits.

```python
class UsageBudget:
    """Track and enforce usage budgets"""
    
    async def check_budget(self, tenant_id: str, estimated_cost: float) -> bool:
        budget = await self.get_tenant_budget(tenant_id)
        current_usage = await self.get_current_usage(tenant_id)
        
        if current_usage + estimated_cost > budget.monthly_limit:
            if budget.hard_limit:
                raise BudgetExceededException(
                    f"Monthly budget of ${budget.monthly_limit} exceeded"
                )
            else:
                await self.notify_budget_warning(tenant_id, current_usage)
        
        return True
    
    async def record_usage(self, tenant_id: str, tokens: int, model: str, cost: float):
        await self.redis.hincrby(
            f"usage:{tenant_id}:{current_month()}",
            "tokens", tokens
        )
        await self.redis.hincrbyfloat(
            f"usage:{tenant_id}:{current_month()}",
            "cost", cost
        )
```

---

## Cost Tracking Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Request Processing                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Request → [Semantic Cache] → Cache Hit? → Return Cached           │
│                    ↓                                                 │
│               Cache Miss                                             │
│                    ↓                                                 │
│            [Model Router] → Select Model                             │
│                    ↓                                                 │
│           [Prompt Optimizer] → Reduce Tokens                         │
│                    ↓                                                 │
│            [Budget Check] → Within Budget?                           │
│                    ↓              ↓                                  │
│                   Yes            No → Rate Limit/Notify              │
│                    ↓                                                 │
│              [LLM Inference]                                         │
│                    ↓                                                 │
│            [Cache Response]                                          │
│                    ↓                                                 │
│            [Record Usage]                                            │
│                    ↓                                                 │
│               Response                                               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Consequences

### Positive

- 50-70% reduction in LLM costs
- Predictable per-tenant costs
- Improved response latency (cached responses)
- Sustainable scaling economics

### Negative

- Added complexity in request pipeline
- Potential quality variation with model routing
- Cache maintenance overhead
- Requires ongoing model cost monitoring

### Metrics

| Metric | Target |
|--------|--------|
| Cache hit rate | >30% |
| Avg cost per request | <$0.02 |
| Budget accuracy | ±5% |
| Latency impact | <50ms |

---

## Related

- [LLM Observability](../../04-operations/observability/llm-observability.md)
- [ADR-006: LLM Provider Strategy](ADR-006-llm-provider-strategy.md)
- [Metrics Reference](../../04-operations/observability/metrics.md)
