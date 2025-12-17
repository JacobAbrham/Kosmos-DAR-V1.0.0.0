# Pre-Flight Cost Governance

!!! warning "Financial Control"
    Every tool call in KOSMOS is subject to pre-flight cost estimation and governance checks, ensuring financial accountability and preventing runaway costs.

## Overview

Spec C defines the middleware logic that intercepts all tool calls before execution, estimates costs, and enforces approval thresholds.

```
┌─────────────────────────────────────────────────────────────────┐
│                    TOOL CALL FLOW                               │
│                                                                 │
│  Agent Request                                                  │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────────┐                                           │
│  │   INTERCEPT     │◄─── Zeus Middleware (LangGraph Decorator)  │
│  └────────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │    ESTIMATE     │◄─── Query Cost Registry (Dragonfly)        │
│  └────────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │     CHECK       │◄─── Apply Governance Rules                 │
│  └────────┬────────┘                                           │
│           │                                                     │
│     ┌─────┴─────┐                                              │
│     │           │                                               │
│     ▼           ▼                                               │
│ [< $50]    [$50-$100]    [> $100]                              │
│     │           │            │                                  │
│     ▼           ▼            ▼                                  │
│  EXECUTE   PENTARCHY    HUMAN INTERRUPT                         │
│            VOTE                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Cost Registry

### Architecture

The Cost Registry is maintained in Dragonfly (Redis-compatible) for sub-millisecond lookups:

```
┌─────────────────────────────────────────────┐
│              COST REGISTRY                   │
│              (Dragonfly)                     │
├─────────────────────────────────────────────┤
│                                             │
│  LLM Costs (from LiteLLM/Langfuse)          │
│  ├── model:gpt-4-turbo → $0.01/1K tokens    │
│  ├── model:qwen-72b → $0.008/1K tokens      │
│  ├── model:llama3.2:3b → $0.00001/1K tokens │
│  └── model:nomic-embed → $0.00001/1K tokens │
│                                             │
│  Infrastructure Costs                        │
│  ├── compute:ecs.g7.large → $0.05/hour      │
│  ├── storage:essd-pl1 → $0.0001/GB/hour     │
│  └── network:egress → $0.08/GB              │
│                                             │
│  Tool Costs                                  │
│  ├── mcp:github-create-repo → $0.00        │
│  ├── mcp:alibaba-provision-ecs → $50+      │
│  └── mcp:stripe-charge → variable          │
│                                             │
└─────────────────────────────────────────────┘
```

## Middleware Implementation

### LangGraph Decorator

```python
from functools import wraps
from langgraph.prebuilt import ToolNode
import asyncio

def cost_governance(func):
    """Pre-flight cost governance decorator for tool calls."""
    
    @wraps(func)
    async def wrapper(state, config, *args, **kwargs):
        tool_call = state.get("current_tool_call")
        
        # 1. INTERCEPT: Extract tool call details
        tool_name = tool_call.get("name")
        tool_params = tool_call.get("parameters", {})
        
        # 2. ESTIMATE: Query Cost Registry
        estimate = await estimate_cost(tool_name, tool_params)
        
        # 3. CHECK: Apply governance rules
        decision = await check_governance(estimate)
        
        if decision == "EXECUTE":
            # Cost < $50: Auto-approve
            return await func(state, config, *args, **kwargs)
            
        elif decision == "PENTARCHY_VOTE":
            # Cost $50-$100: Trigger AI vote
            vote_result = await trigger_pentarchy_vote(
                tool_call, estimate
            )
            if vote_result.approved:
                return await func(state, config, *args, **kwargs)
            else:
                return create_rejection_response(vote_result)
                
        else:  # decision == "HUMAN_INTERRUPT"
            # Cost > $100: Require human approval
            approval = await request_human_approval(
                tool_call, estimate
            )
            if approval.approved:
                return await func(state, config, *args, **kwargs)
            else:
                return create_rejection_response(approval)
    
    return wrapper
```

## Cost Tracking

### Real-Time Monitoring

```sql
-- Track actual vs estimated costs
CREATE TABLE cost_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool_call_id UUID NOT NULL,
    estimated_cost DECIMAL(12,4) NOT NULL,
    actual_cost DECIMAL(12,4),
    variance_pct DECIMAL(5,2),
    agent_id VARCHAR(50) NOT NULL,
    tool_name VARCHAR(100) NOT NULL,
    governance_decision VARCHAR(20) NOT NULL,
    approved_by VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_cost_tracking_agent ON cost_tracking(agent_id);
CREATE INDEX idx_cost_tracking_tool ON cost_tracking(tool_name);
CREATE INDEX idx_cost_tracking_created ON cost_tracking(created_at);
```

### Budget Alerts

```yaml
# cost-alerts.yaml
alerts:
  - name: daily_budget_80pct
    condition: daily_spend > (daily_budget * 0.8)
    severity: warning
    notify: [operator_alpha]
    
  - name: daily_budget_exceeded
    condition: daily_spend > daily_budget
    severity: critical
    notify: [operator_alpha, operator_beta]
    action: pause_non_critical
    
  - name: estimation_variance_high
    condition: avg_variance_pct > 25
    severity: warning
    notify: [hephaestus]
    action: recalibrate_estimates
```

## Configuration

### Governance Thresholds

```yaml
# cost-governance-config.yaml
thresholds:
  auto_approve_max: 50          # USD - no approval needed
  pentarchy_vote_max: 100       # USD - AI vote required
  human_required_above: 100     # USD - human approval required
  
budgets:
  daily_limit: 500              # USD
  weekly_limit: 2500            # USD
  monthly_limit: 10000          # USD
  
categories:
  llm_inference:
    daily_limit: 200
    alert_threshold: 0.8
  infrastructure:
    daily_limit: 200
    alert_threshold: 0.7
  tools:
    daily_limit: 100
    alert_threshold: 0.9
```

## Monitoring Dashboard

### Key Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `cost.daily_spend` | Total spend today | > 80% budget |
| `cost.estimation_accuracy` | Estimated vs actual | < 75% |
| `cost.pentarchy_approval_rate` | AI vote success rate | < 70% |
| `cost.human_response_time` | Time to human decision | > 4 hours |

---

## See Also

- [Pentarchy Governance](pentarchy-governance.md) — Multi-agent voting
- [FinOps Metrics](../04-operations/finops-metrics.md) — Financial operations
- [LiteLLM Configuration](../02-architecture/cloud-inference.md) — LLM cost routing

---

**Source:** Spec C of [Digital Agentic Realm](../00-executive/digital-agentic-realm.md)
