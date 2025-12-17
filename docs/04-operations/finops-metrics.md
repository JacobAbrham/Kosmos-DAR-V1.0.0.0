# FinOps Metrics

**Financial Operations for AI Systems**

> "Track every token, optimize every dollar, forecast every trend."

---

## 📋 Overview

FinOps (Financial Operations) for AI systems involves tracking, analyzing, and optimizing the costs associated with training, deploying, and running AI models. Unlike traditional infrastructure costs, AI costs scale with usage and can be highly variable.

### Key Cost Drivers

- **Token Usage** - API costs for LLM providers (OpenAI, Anthropic, etc.)
- **Compute** - GPU/TPU costs for training and inference
- **Storage** - Model artifacts, training data, logs
- **Networking** - Data transfer, API calls
- **Monitoring** - Observability tools and logging

---

## 💰 Cost Tracking

### Cost per Request

```python
# Calculate cost per request
cost_per_request = (
    input_tokens * input_token_cost +
    output_tokens * output_token_cost +
    infrastructure_cost_per_second * latency_seconds +
    monitoring_cost_per_request
)

# Example for Document Summarizer
input_tokens = 450
output_tokens = 125
input_token_cost = $0.00001  # $0.01 per 1K tokens
output_token_cost = $0.00003  # $0.03 per 1K tokens
infrastructure_cost = $0.0001
monitoring_cost = $0.00005

total_cost = (450 * 0.00001) + (125 * 0.00003) + 0.0001 + 0.00005
         = $0.0045 + $0.00375 + $0.0001 + $0.00005
         = $0.0084 per request
```

### Monthly Cost Projection

| Model | Requests/Day | Cost/Request | Daily Cost | Monthly Cost |
|-------|--------------|--------------|------------|--------------|
| Document Summarizer | 500K | $0.0084 | $4,200 | $126,000 |
| Code Reviewer | 300K | $0.0112 | $3,360 | $100,800 |
| Sentiment Analyzer | 200K | $0.0045 | $900 | $27,000 |
| **Total** | **1M** | - | **$8,460** | **$253,800** |

---

## 📊 Cost Breakdown

### By Model

```yaml
cost_breakdown:
  document_summarizer:
    monthly_cost: $126,000
    percentage: 49.6%
    requests: 15M
    cost_per_request: $0.0084
    
  code_reviewer:
    monthly_cost: $100,800
    percentage: 39.7%
    requests: 9M
    cost_per_request: $0.0112
    
  sentiment_analyzer:
    monthly_cost: $27,000
    percentage: 10.6%
    requests: 6M
    cost_per_request: $0.0045
```

### By Cost Type

```yaml
infrastructure:
  compute:
    training: $8,100
    inference: $32,400
    total: $40,500
    percentage: 16%
    
  api_calls:
    openai_api: $180,000
    anthropic_api: $25,000
    total: $205,000
    percentage: 81%
    
  storage:
    model_artifacts: $1,500
    training_data: $800
    logs: $400
    total: $2,700
    percentage: 1%
    
  networking:
    data_transfer: $1,500
    cdn: $530
    total: $2,030
    percentage: 1%
    
  monitoring:
    datadog: $2,000
    sentry: $570
    total: $2,570
    percentage: 1%
```

---

## 🎯 Cost Optimization Strategies

### 1. Token Optimization

**Reduce Input Tokens:**
```python
# Before: Full document
prompt = f"Summarize: {full_document}"  # 5000 tokens

# After: Truncate intelligently
prompt = f"Summarize: {truncate_smart(full_document, max=2000)}"  # 2000 tokens
# Savings: 60% reduction in input costs
```

**Optimize Output Tokens:**
```yaml
# Set appropriate max_tokens
max_tokens: 200  # Instead of 1000
# Only generate what's needed
```

### 2. Model Selection

| Use Case | Current Model | Cost/Req | Alternative | Cost/Req | Savings |
|----------|---------------|----------|-------------|----------|---------|
| Simple summaries | GPT-4 | $0.0084 | GPT-3.5-Turbo | $0.0021 | 75% |
| Sentiment analysis | GPT-4 | $0.0112 | Fine-tuned BERT | $0.0008 | 93% |
| Code review | GPT-4 | $0.0112 | GPT-4-Turbo | $0.0084 | 25% |

### 3. Caching

```python
# Cache frequent requests
cache_hit_rate = 35%
average_cost_per_request = $0.0084

# With caching
cache_cost = $0.0001  # Redis lookup
actual_llm_calls = requests * (1 - cache_hit_rate)

# Monthly savings
monthly_requests = 15_000_000
without_cache = monthly_requests * $0.0084 = $126,000
with_cache = (monthly_requests * 0.65 * $0.0084) + (monthly_requests * 0.35 * $0.0001)
           = $81,900 + $525 = $82,425
savings = $43,575/month (35%)
```

### 4. Batch Processing

```python
# Instead of real-time processing
# Batch non-urgent requests

# Hourly batch processing
batch_discount = 0.20  # 20% discount for batch API
cost_with_batch = cost_per_request * (1 - batch_discount)
```

### 5. Rate Limiting

```yaml
rate_limits:
  per_user: 100/hour
  per_ip: 200/hour
  burst_limit: 10/minute

# Prevents abuse and cost spikes
# Implement tiered pricing for high-volume users
```

---

## 📈 Budget Management

### Monthly Budget

```yaml
monthly_budget:
  allocated: $250,000
  current_spend: $253,800
  variance: +$3,800 (1.5% over budget) 🔴
  forecast_month_end: $258,000
  action_required: true
```

### Budget Alerts

```yaml
alerts:
  - threshold: 75%
    current: 101.5%
    status: CRITICAL
    action: "Immediate optimization required"
    
  - threshold: 90%
    current: 101.5%
    status: CRITICAL
    action: "Freeze non-critical spending"
    
  - threshold: 100%
    current: 101.5%
    status: CRITICAL
    action: "Executive approval for overspend"
```

### Cost Allocation

```yaml
# Charge back to business units
business_units:
  engineering:
    models: [code_reviewer]
    cost: $100,800
    
  marketing:
    models: [sentiment_analyzer]
    cost: $27,000
    
  operations:
    models: [document_summarizer]
    cost: $126,000
```

---

## 🔍 Cost Monitoring

### Real-Time Dashboard

```python
# Cost monitoring script
from prometheus_client import Gauge

# Metrics
cost_gauge = Gauge('model_cost_usd', 'Cost in USD', ['model', 'period'])
requests_gauge = Gauge('model_requests', 'Request count', ['model'])

# Track costs
def track_request_cost(model_id, input_tokens, output_tokens):
    cost = calculate_cost(input_tokens, output_tokens)
    cost_gauge.labels(model=model_id, period='hourly').set(cost)
    requests_gauge.labels(model=model_id).inc()
    
    # Alert if over budget
    if cost > hourly_budget:
        send_alert(f"Model {model_id} over hourly budget")
```

### Cost Anomaly Detection

```python
# Detect unusual cost spikes
def detect_cost_anomaly(model_id):
    current_cost = get_current_hourly_cost(model_id)
    historical_avg = get_30day_avg_cost(model_id)
    std_dev = get_cost_std_dev(model_id)
    
    # Alert if 3 standard deviations above mean
    if current_cost > (historical_avg + 3 * std_dev):
        alert = {
            "severity": "high",
            "model": model_id,
            "current_cost": current_cost,
            "expected_cost": historical_avg,
            "anomaly_score": (current_cost - historical_avg) / std_dev
        }
        send_cost_anomaly_alert(alert)
```

---

## 📋 Cost Optimization Checklist

### Weekly Tasks
- [ ] Review top 10 costliest models
- [ ] Check for cache hit rate opportunities
- [ ] Identify wasteful requests
- [ ] Review token usage patterns
- [ ] Update cost forecasts

### Monthly Tasks
- [ ] Compare actual vs budget
- [ ] Analyze cost trends
- [ ] Review model alternatives
- [ ] Evaluate new pricing options
- [ ] Conduct cost optimization sprint
- [ ] Update budget allocations

### Quarterly Tasks
- [ ] Comprehensive cost audit
- [ ] Renegotiate API contracts
- [ ] Evaluate Reserved Instances
- [ ] Update cost models
- [ ] Strategic planning for next quarter

---

## 🔗 Related Documentation

- **[SLA/SLO](sla-slo.md)** - Service level objectives
- **[Drift Detection](drift-detection.md)** - Monitor model performance
- **[Model Cards](../03-engineering/model-cards/README.md)** - Model documentation
- **[Volume I: Governance](../01-governance/index.md)** - Budget approval processes

---

## 📞 FinOps Contacts

| Role | Contact |
|------|---------|
| **FinOps Lead** | finops@nuvanta-holding.com |
| **CFO** | cfo@nuvanta-holding.com |
| **DevOps** | devops@nuvanta-holding.com |

---

**Last Updated:** 2025-12-11  
**Document Owner:** FinOps Lead  
**Next Review:** 2026-01-11

---

[← Back to Volume IV](index.md) | [Drift Detection →](drift-detection.md)
