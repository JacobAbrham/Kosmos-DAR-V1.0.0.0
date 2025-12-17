# Model Degradation Response

**Runbook for Model Performance Degradation**

---

## 🚨 Severity Classification

| Severity | Degradation Level | Response Time |
|----------|-------------------|---------------|
| P0 (Critical) | >20% accuracy drop | 5 minutes |
| P1 (High) | 10-20% accuracy drop | 15 minutes |
| P2 (Medium) | 5-10% accuracy drop | 1 hour |
| P3 (Low) | <5% accuracy drop | 24 hours |

---

## 📊 Detection Triggers

### Automated Alerts

```yaml
alerts:
  - name: CriticalAccuracyDrop
    condition: accuracy < baseline * 0.80
    severity: P0
    
  - name: HighLatencySpike
    condition: p95_latency > slo * 2
    severity: P1
    
  - name: ErrorRateSpike
    condition: error_rate > 0.05
    severity: P1
    
  - name: DriftDetected
    condition: drift_score > 0.3
    severity: P2
```

---

## 🔧 Response Procedures

### Phase 1: Immediate Assessment (0-5 minutes)

1. **Confirm alert is valid**
   ```bash
   # Check current metrics
   curl -s https://api.kosmos.nuvanta-holding.com/health/model/{model_id}
   
   # Verify against baseline
   kubectl logs -l app=drift-detector --tail=100
   ```

2. **Assess scope of impact**
   - Which model(s) affected?
   - Which features/endpoints impacted?
   - How many users affected?

3. **Notify stakeholders**
   ```bash
   # Slack notification
   /incident start "Model degradation detected on {model_id}"
   ```

### Phase 2: Triage (5-15 minutes)

1. **Identify root cause category**

   | Category | Indicators | Likely Cause |
   |----------|------------|--------------|
   | Data Drift | Distribution shift | Input data changed |
   | Model Issue | Sudden accuracy drop | Model corruption |
   | Infrastructure | Latency spikes | Resource constraints |
   | External | Provider errors | LLM provider issue |

2. **Check recent changes**
   ```bash
   # Recent deployments
   kubectl rollout history deployment/{model-deployment}
   
   # Recent config changes
   git log --oneline -10
   ```

3. **Determine if rollback needed**
   - If recent deployment caused issue → rollback
   - If data drift → activate fallback model

### Phase 3: Mitigation

#### Option A: Rollback to Previous Version

```bash
# Rollback deployment
kubectl rollout undo deployment/{model-deployment}

# Verify rollback
kubectl rollout status deployment/{model-deployment}
```

#### Option B: Activate Fallback Model

```bash
# Switch traffic to fallback
kubectl patch service {model-service} -p '{"spec":{"selector":{"version":"fallback"}}}'
```

#### Option C: Traffic Reduction

```bash
# Reduce traffic to affected model
kubectl scale deployment/{model-deployment} --replicas=1
```

#### Option D: Kill Switch (Critical Only)

See [Kill Switch Protocol](../../01-governance/kill-switch-protocol.md)

### Phase 4: Recovery

1. **Investigate root cause**
   - Analyze drift metrics
   - Review data pipeline logs
   - Check LLM provider status

2. **Implement fix**
   - Data issue: Retrain with corrected data
   - Model issue: Deploy fixed model version
   - Infrastructure: Scale resources

3. **Validate fix**
   ```bash
   # Run validation tests
   python scripts/validate_model.py --model {model_id}
   
   # Check metrics
   curl -s https://api.kosmos.nuvanta-holding.com/metrics/model/{model_id}
   ```

4. **Restore full service**
   ```bash
   # Gradual traffic increase
   kubectl scale deployment/{model-deployment} --replicas=3
   ```

---

## 📋 Post-Incident

### Documentation Required

- Incident timeline
- Root cause analysis
- Actions taken
- Prevention measures

### Follow-up Actions

- [ ] Update monitoring thresholds if needed
- [ ] Add new test cases for detected issue
- [ ] Update runbook if procedures changed
- [ ] Schedule post-mortem meeting

---

## 📞 Escalation Path

1. ML Engineering On-Call
2. ML Engineering Lead
3. VP Engineering
4. CTO (P0 only)

---

**Last Updated:** 2025-12-12  
**Document Owner:** ML Engineering Lead

[← Back to Incident Response](README.md)
