# Canary Deployment Playbooks

**Safe, Gradual Rollout Procedures for AI Models**

> "Deploy incrementally, monitor continuously, roll back instantly."

---

## 📋 Overview

Canary deployments enable safe, gradual rollout of AI models by exposing new versions to a small percentage of traffic before full deployment. This approach minimizes risk and enables rapid rollback if issues arise.

### Why Canary Deployments?

- **Risk Mitigation** - Limit blast radius of potential issues
- **Early Detection** - Catch problems before full rollout
- **Rapid Rollback** - Quick reversion if issues detected
- **Performance Validation** - Real-world testing at scale
- **Confidence Building** - Gradual validation increases confidence

---

## 🎯 Canary Deployment Strategy

### Traffic Split Progression

```
Initial: 5% canary, 95% stable
After 1 hour: 10% canary, 90% stable (if healthy)
After 4 hours: 25% canary, 75% stable (if healthy)
After 24 hours: 50% canary, 50% stable (if healthy)
After 48 hours: 100% canary (full rollout)
```

### Health Criteria

For each stage, the canary must meet:
- ✅ Error rate < 1%
- ✅ P95 latency within 20% of baseline
- ✅ No critical errors
- ✅ Fairness metrics within acceptable range
- ✅ Cost per request within budget

---

## 📝 Deployment Phases

### Phase 1: Pre-Deployment (T-24h)

**Preparation Checklist:**
- [ ] Model card reviewed and approved
- [ ] AIBOM generated and validated
- [ ] Security scan passed (no critical/high vulnerabilities)
- [ ] Performance benchmarks meet targets
- [ ] Rollback procedure tested
- [ ] Monitoring dashboards configured
- [ ] Alert thresholds set
- [ ] On-call team notified
- [ ] Stakeholders informed

**Technical Setup:**
```bash
# Tag release
git tag -a v2.1.0 -m "Model v2.1.0 release"
git push origin v2.1.0

# Build container
docker build -t model-summarizer:v2.1.0 .
docker push registry.nuvanta.com/model-summarizer:v2.1.0

# Update Kubernetes manifests
kubectl apply -f k8s/canary-v2.1.0.yaml --dry-run=client
```

---

### Phase 2: Initial Canary (5% Traffic)

**Deployment Commands:**
```bash
# Deploy canary version
kubectl apply -f k8s/canary-v2.1.0.yaml

# Verify pods are running
kubectl get pods -l version=v2.1.0

# Configure traffic split (5% canary)
kubectl apply -f k8s/traffic-split-5percent.yaml

# Verify traffic split
kubectl describe virtualservice model-summarizer
```

**Monitoring (First Hour):**
```bash
# Watch error rates
kubectl logs -l version=v2.1.0 --tail=100 -f

# Monitor metrics
watch -n 10 'curl http://metrics/canary_health'

# Check dashboards
# - Grafana: Model Performance Dashboard
# - DataDog: Error Rates & Latency
# - Custom: Fairness Metrics Dashboard
```

**Success Criteria:**
- Error rate < 1% for 1 full hour
- P95 latency < 2 seconds
- No crashes or OOM errors
- Fairness metrics stable
- Cost per request acceptable

**Actions:**
- ✅ **If healthy:** Proceed to Phase 3 after 1 hour
- ❌ **If unhealthy:** Execute rollback procedure immediately

---

### Phase 3: Increased Canary (10% Traffic)

**Traffic Update:**
```bash
# Increase to 10% traffic
kubectl apply -f k8s/traffic-split-10percent.yaml

# Verify updated split
kubectl describe virtualservice model-summarizer
```

**Monitoring (Next 3 Hours):**
- Continue monitoring all Phase 2 metrics
- Compare canary vs stable version performance
- Monitor for drift in fairness metrics
- Check cost trends

**Success Criteria:**
- All Phase 2 criteria met
- No degradation compared to stable version
- Maintained for 3 continuous hours

**Actions:**
- ✅ **If healthy:** Proceed to Phase 4 after 4 hours total
- ❌ **If unhealthy:** Execute rollback procedure

---

### Phase 4: Expanded Canary (25% Traffic)

**Traffic Update:**
```bash
# Increase to 25% traffic
kubectl apply -f k8s/traffic-split-25percent.yaml
```

**Extended Monitoring (20 Hours):**
- Full metrics dashboard review every 4 hours
- Compare day-over-day performance
- User feedback monitoring
- Cost analysis

**Success Criteria:**
- All previous criteria maintained
- User satisfaction metrics stable
- No anomalies detected over 20 hours

**Actions:**
- ✅ **If healthy:** Proceed to Phase 5 after 24 hours total
- ❌ **If issues:** Reduce traffic or rollback

---

### Phase 5: Major Canary (50% Traffic)

**Traffic Update:**
```bash
# Split traffic 50/50
kubectl apply -f k8s/traffic-split-50percent.yaml
```

**Monitoring (24 Hours):**
- A/B testing analysis
- Performance comparison reports
- Cost analysis
- User feedback analysis

**Success Criteria:**
- Canary performs equal or better than stable
- No degradation in any monitored metrics
- Maintained for 24 continuous hours

**Actions:**
- ✅ **If healthy:** Proceed to full rollout after 48 hours total
- ❌ **If issues:** Rollback to stable version

---

### Phase 6: Full Rollout (100% Traffic)

**Final Deployment:**
```bash
# Route 100% traffic to new version
kubectl apply -f k8s/traffic-split-100percent.yaml

# Remove old stable version after 24h soak time
kubectl delete deployment model-summarizer-v2.0.0
```

**Post-Deployment:**
- Monitor for 7 days with heightened alerting
- Conduct post-deployment review
- Update documentation
- Archive old version artifacts
- Celebrate success! 🎉

---

## 🚨 Rollback Procedures

### Automatic Rollback Triggers

Rollback automatically if:
- Error rate > 5% for 5 minutes
- P95 latency > 5 seconds for 5 minutes
- Critical errors detected
- Fairness metric drops below threshold
- Out of memory errors

### Manual Rollback Procedure

**Immediate Rollback (< 1 minute):**
```bash
# Instant rollback to stable version
kubectl apply -f k8s/traffic-split-0percent.yaml

# Verify traffic restored to stable
kubectl describe virtualservice model-summarizer

# Confirm error rates dropping
watch -n 5 'curl http://metrics/error_rate'
```

**Cleanup:**
```bash
# Remove canary deployment
kubectl delete -f k8s/canary-v2.1.0.yaml

# Document incident
# Create post-mortem ticket
# Update rollback logs
```

### Rollback Decision Matrix

| Issue Severity | Action | Timeline |
|----------------|--------|----------|
| **Critical** - Service down | Immediate rollback | < 30 seconds |
| **High** - Error rate &gt;5% | Rollback | < 2 minutes |
| **Medium** - Performance degradation | Reduce traffic or rollback | < 5 minutes |
| **Low** - Minor issues | Continue monitoring, prepare rollback | Monitor 30 min |

---

## 📊 Monitoring & Metrics

### Real-Time Dashboards

**Performance Dashboard:**
```
Model Performance - Canary vs Stable
├── Request Rate (req/s)
│   ├── Canary: XXX
│   └── Stable: XXX
├── Error Rate (%)
│   ├── Canary: X.XX%
│   └── Stable: X.XX%
├── Latency (P50/P95/P99)
│   ├── Canary: XXms / XXms / XXms
│   └── Stable: XXms / XXms / XXms
└── Success Rate (%)
    ├── Canary: XX.X%
    └── Stable: XX.X%
```

**Fairness Dashboard:**
```
Fairness Metrics - Canary vs Stable
├── Demographic Parity
│   ├── Canary: X.XX (threshold: &lt;0.1)
│   └── Stable: X.XX
├── Equal Opportunity
│   ├── Canary: X.XX (threshold: &lt;0.1)
│   └── Stable: X.XX
└── Disparate Impact
    ├── Canary: X.XX (threshold: &gt;0.8)
    └── Stable: X.XX
```

### Alert Configuration

```yaml
# alerts/canary-alerts.yaml
alerts:
  - name: "Canary Error Rate High"
    condition: "canary_error_rate > 0.05"
    duration: "5m"
    severity: "critical"
    action: "auto_rollback"
    
  - name: "Canary Latency High"
    condition: "canary_p95_latency > 5000"
    duration: "5m"
    severity: "high"
    action: "notify_on_call"
    
  - name: "Canary Fairness Violation"
    condition: "canary_fairness_metric < 0.8"
    duration: "10m"
    severity: "high"
    action: "notify_ml_team"
    
  - name: "Canary Cost Overrun"
    condition: "canary_cost_per_request > 1.5 * baseline"
    duration: "1h"
    severity: "medium"
    action: "notify_finops"
```

---

## 🔄 Deployment Automation

### Automated Canary Script

```python
#!/usr/bin/env python3
"""
Automated canary deployment script
"""
import time
from kubernetes import client, config
from prometheus_api_client import PrometheusConnect

def deploy_canary(version: str):
    """Deploy canary version with automated traffic progression"""
    
    traffic_stages = [
        {"percent": 5, "duration": 3600},      # 1 hour
        {"percent": 10, "duration": 10800},    # 3 hours
        {"percent": 25, "duration": 72000},    # 20 hours
        {"percent": 50, "duration": 86400},    # 24 hours
        {"percent": 100, "duration": 0},       # Full rollout
    ]
    
    for stage in traffic_stages:
        # Update traffic split
        update_traffic_split(version, stage["percent"])
        
        print(f"Traffic at {stage['percent']}% to canary {version}")
        
        # Monitor health for duration
        if not monitor_health(version, stage["duration"]):
            print(f"Health check failed at {stage['percent']}%")
            rollback(version)
            return False
        
        print(f"Stage {stage['percent']}% successful")
    
    print(f"Canary deployment {version} completed successfully!")
    cleanup_old_version()
    return True

def monitor_health(version: str, duration: int) -> bool:
    """Monitor canary health for specified duration"""
    prom = PrometheusConnect()
    
    start_time = time.time()
    while time.time() - start_time < duration:
        # Check error rate
        error_rate = get_error_rate(prom, version)
        if error_rate > 0.05:
            return False
        
        # Check latency
        p95_latency = get_p95_latency(prom, version)
        if p95_latency > 5000:
            return False
        
        # Check fairness metrics
        fairness = get_fairness_metrics(version)
        if not check_fairness_thresholds(fairness):
            return False
        
        time.sleep(60)  # Check every minute
    
    return True

def rollback(version: str):
    """Emergency rollback to stable version"""
    print(f"ROLLING BACK {version}")
    update_traffic_split(version, 0)
    send_alert("Canary rollback executed", severity="critical")
    create_incident_ticket(version)

if __name__ == "__main__":
    deploy_canary("v2.1.0")
```

---

## 📋 Deployment Checklist

### Pre-Deployment Review

- [ ] **Model Quality**
  - [ ] Model card completed
  - [ ] Performance benchmarks met
  - [ ] Fairness analysis passed
  - [ ] AIBOM generated

- [ ] **Security**
  - [ ] Vulnerability scan passed
  - [ ] No critical/high CVEs
  - [ ] Adversarial testing completed
  - [ ] Access controls verified

- [ ] **Infrastructure**
  - [ ] Container built and tested
  - [ ] Kubernetes manifests validated
  - [ ] Resource limits set appropriately
  - [ ] Auto-scaling configured

- [ ] **Monitoring**
  - [ ] Dashboards configured
  - [ ] Alerts defined
  - [ ] Logging enabled
  - [ ] Tracing configured

- [ ] **Rollback Readiness**
  - [ ] Rollback procedure tested
  - [ ] Stable version identified
  - [ ] Emergency contacts notified
  - [ ] Runbooks updated

### During Deployment

- [ ] Monitor error rates continuously
- [ ] Watch latency metrics
- [ ] Check fairness metrics
- [ ] Monitor resource utilization
- [ ] Track cost per request
- [ ] Review user feedback
- [ ] Document any issues

### Post-Deployment

- [ ] Conduct retrospective
- [ ] Update documentation
- [ ] Archive deployment logs
- [ ] Update model registry
- [ ] Notify stakeholders
- [ ] Remove old version (after soak period)

---

## 🔗 Related Documentation

- **[Drift Detection](../04-operations/drift-detection)** - Monitor for model drift
- **[Incident Response](../04-operations/incident-response/README)** - If issues arise
- **[SLA/SLO](../04-operations/sla-slo)** - Service level objectives
- **[Model Cards](model-cards/README)** - Pre-deployment documentation

---

## 📞 Support & Contacts

| Role | Contact | Responsibility |
|------|---------|----------------|
| **On-Call Engineer** | oncall@nuvanta-holding.com | 24/7 deployment support |
| **ML Lead** | ml-lead@nuvanta-holding.com | Model-specific decisions |
| **DevOps Lead** | devops@nuvanta-holding.com | Infrastructure issues |
| **Security Team** | security@nuvanta-holding.com | Security concerns |

---

## 📅 Review Schedule

- **Playbook Updates** - After each major deployment
- **Procedure Testing** - Quarterly rollback drills
- **Automation Review** - Semi-annual improvements

**Next Review:** 2026-03-11

---

**Last Updated:** 2025-12-11  
**Document Owner:** DevOps Lead  
**Status:** Active

---

[← Back to Volume III](index) | [Watermarking Standard →](watermarking-standard)
