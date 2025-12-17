# Cost Spike Response

**Runbook for Unexpected Cost Increases**

---

## 🚨 Severity Classification

| Severity | Cost Increase | Response Time |
|----------|---------------|---------------|
| P0 (Critical) | >100% daily budget | 15 minutes |
| P1 (High) | 50-100% daily budget | 1 hour |
| P2 (Medium) | 25-50% daily budget | 4 hours |
| P3 (Low) | 10-25% daily budget | 24 hours |

---

## 📊 Detection Triggers

### Automated Alerts

```yaml
alerts:
  - name: DailyCostCritical
    condition: daily_cost > daily_budget * 2.0
    severity: P0
    
  - name: DailyCostHigh
    condition: daily_cost > daily_budget * 1.5
    severity: P1
    
  - name: HourlyCostSpike
    condition: hourly_cost > hourly_avg * 3
    severity: P1
    
  - name: TokenUsageSpike
    condition: token_rate > baseline * 5
    severity: P2
```

### Cost Thresholds

| Model | Daily Budget | Warning | Critical |
|-------|--------------|---------|----------|
| MC-001 (Summarizer) | $4,200 | $5,250 | $8,400 |
| MC-002 (Sentiment) | $900 | $1,125 | $1,800 |
| MC-003 (Code Review) | $3,360 | $4,200 | $6,720 |
| **Total** | **$8,460** | **$10,575** | **$16,920** |

---

## 🔧 Response Procedures

### Phase 1: Immediate Assessment (0-15 minutes)

1. **Confirm cost spike**
   ```bash
   # Check current costs
   curl -s https://api.kosmos.nuvanta-holding.com/finops/daily-cost
   
   # Check by model
   curl -s https://api.kosmos.nuvanta-holding.com/finops/cost-by-model
   ```

2. **Identify source**
   - Which model(s) causing spike?
   - Which users/API keys?
   - Which endpoints?

3. **Check for anomalies**
   ```bash
   # Token usage by endpoint
   kubectl logs -l app=api-gateway --tail=500 | grep "token_count"
   
   # Request volume
   curl -s https://api.kosmos.nuvanta-holding.com/metrics/request-volume
   ```

### Phase 2: Root Cause Analysis

| Cause | Indicators | Solution |
|-------|------------|----------|
| Traffic spike | Request volume up | Rate limiting |
| Prompt expansion | Token count up, requests same | Prompt optimization |
| Loop/retry bug | Same user, high requests | Block/fix client |
| Abuse/attack | Unknown API key, high volume | Revoke key, investigate |
| Model change | New deployment, higher costs | Rollback or optimize |

### Phase 3: Mitigation

#### Option A: Enable Rate Limiting

```bash
# Reduce per-user rate limits
kubectl patch configmap rate-limits -p '{"data":{"default":"100/min"}}'

# Apply immediately
kubectl rollout restart deployment/api-gateway
```

#### Option B: Block Abusive Users

```bash
# Identify top consumers
curl -s https://api.kosmos.nuvanta-holding.com/finops/top-users?limit=10

# Revoke API key if abuse detected
curl -X DELETE https://api.kosmos.nuvanta-holding.com/admin/api-keys/{key_id}
```

#### Option C: Reduce Model Tier

```bash
# Switch to cheaper model temporarily
kubectl patch configmap model-config -p '{"data":{"summarizer_model":"gpt-3.5-turbo"}}'
```

#### Option D: Emergency Cost Cap

```bash
# Enable hard cost cap
kubectl patch configmap cost-controls -p '{"data":{"daily_cap_enabled":"true","daily_cap":"10000"}}'
```

### Phase 4: Recovery

1. **Implement long-term fixes**
   - Optimize prompts
   - Add caching for common queries
   - Implement tiered pricing
   - Add user cost limits

2. **Verify costs normalized**
   ```bash
   # Monitor hourly costs
   watch -n 300 "curl -s https://api.kosmos.nuvanta-holding.com/finops/hourly-cost"
   ```

3. **Restore normal operations**
   - Remove temporary rate limits
   - Re-enable paused features
   - Notify affected users

---

## 📋 Prevention Measures

### Proactive Controls

```yaml
cost_controls:
  rate_limiting:
    enabled: true
    per_user: "1000/hour"
    per_org: "10000/hour"
    
  cost_caps:
    per_request: "$0.50"
    per_user_daily: "$100"
    per_org_daily: "$5000"
    
  alerting:
    budget_50: "warning"
    budget_75: "alert"
    budget_90: "critical"
```

### Monitoring Dashboard

- Real-time cost by model
- Cost trend (hourly/daily/weekly)
- Top consumers
- Cost per request trend

---

## 📞 Escalation Path

1. FinOps On-Call
2. ML Engineering Lead
3. VP Engineering
4. CFO (P0 only)

---

## 📋 Post-Incident

### Required Documentation

- Total excess cost incurred
- Root cause
- Timeline of events
- Prevention measures implemented

### Follow-up Actions

- [ ] Update cost alerting thresholds
- [ ] Review and optimize prompts
- [ ] Implement additional controls
- [ ] Update runbook if needed

---

**Last Updated:** 2025-12-12  
**Document Owner:** FinOps Lead

[← Back to Incident Response](README.md)
