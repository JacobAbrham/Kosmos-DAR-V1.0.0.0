# High Error Rate Response

**Runbook for High Error Rate Incidents**

---

## 🚨 Severity Classification

| Severity | Error Rate | Response Time |
|----------|------------|---------------|
| P0 (Critical) | >gt;10% error rate | 5 minutes |
| P1 (High) | 5-10% error rate | 15 minutes |
| P2 (Medium) | 1-5% error rate | 1 hour |
| P3 (Low) | &lt;1% error rate | 24 hours |

---

## 📊 Detection Triggers

### Automated Alerts

```yaml
alerts:
  - name: CriticalErrorRate
    condition: error_rate > 0.10
    severity: P0

  - name: HighErrorRate
    condition: error_rate > 0.05
    severity: P1

  - name: ElevatedErrorRate
    condition: error_rate > 0.01
    severity: P2
```

---

## 🔧 Response Procedures

### Phase 1: Immediate Assessment (0-5 minutes)

1. **Confirm alert is valid**
   ```bash
   # Check current error metrics
   curl -s https://api.kosmos.nuvanta-holding.com/metrics/errors | jq '.error_rate'
   ```

   ```bash
   # Check recent error logs
   kubectl logs -l app=agent --tail=100 | grep ERROR
   ```

2. **Assess scope of impact**
   - Which agent(s) affected?
   - Which endpoints/features impacted?
   - How many users affected?

3. **Notify stakeholders**
   ```bash
   # Slack notification
   /incident start "High error rate detected on {agent_id}"
   ```

### Phase 2: Triage (5-15 minutes)

1. **Identify error patterns**

   | Error Type | Indicators | Likely Cause |
   |------------|------------|--------------|
   | 4xx Client | Input validation failures | Bad requests, API misuse |
   | 5xx Server | Internal errors | Code bugs, resource issues |
   | Timeout | Slow responses | Performance degradation |
   | External | Provider errors | LLM provider issues |

2. **Check recent changes**
   ```bash
   # Recent deployments
   kubectl rollout history deployment/{agent-deployment}

   # Recent config changes
   git log --oneline -10
   ```

3. **Determine if rollback needed**
   - If recent deployment caused errors → rollback
   - If external service issue → activate circuit breaker

### Phase 3: Mitigation

#### Option A: Rollback to Previous Version

```bash
# Rollback deployment
kubectl rollout undo deployment/{agent-deployment}

# Verify rollback
kubectl rollout status deployment/{agent-deployment}
```

#### Option B: Enable Circuit Breaker

```bash
# Enable circuit breaker for failing endpoints
kubectl patch configmap agent-config -p '{"data":{"circuit_breaker":"enabled"}}'

# Restart pods to pick up config
kubectl rollout restart deployment/{agent-deployment}
```

#### Option C: Scale Resources

```bash
# Scale up if resource constrained
kubectl scale deployment {agent-deployment} --replicas=10

# Check resource usage
kubectl top pods
```

### Phase 4: Investigation

1. **Analyze error logs**
   ```bash
   # Get detailed error logs
   kubectl logs -l app=agent --since=1h | grep ERROR | head -50
   ```

2. **Check dependencies**
   ```bash
   # Database connectivity
   kubectl exec -it {db-pod} -- mysqladmin ping

   # Cache connectivity
   kubectl exec -it {cache-pod} -- redis-cli ping

   # External API status
   curl -I https://api.openai.com/v1/models
   ```

3. **Review code for bugs**
   - Check recent commits for error-prone changes
   - Review error handling in affected code paths

### Phase 5: Recovery

1. **Verify error rate reduction**
   ```bash
   # Monitor error rate for 15 minutes
   watch -n 60 'curl -s https://api.kosmos.nuvanta-holding.com/metrics/errors | jq ".error_rate"'
   ```

2. **Gradual traffic restoration**
   ```bash
   # If circuit breaker was enabled, gradually restore traffic
   kubectl patch configmap agent-config -p '{"data":{"circuit_breaker_threshold":"0.8"}}'
   ```

3. **Update monitoring**
   - Add additional alerts if needed
   - Update error rate baselines

---

## 📋 Communication Template

### Internal Notification
```
🚨 INCIDENT: High Error Rate on {agent_id}

Status: Investigating
Impact: {X}% error rate, affecting {Y} users
ETA: {time}

Next update: {time}
```

### Customer Communication (if needed)
```
We're experiencing elevated error rates on some requests.
Our team is actively investigating and implementing fixes.
Service should be restored within {time}.

Status: https://status.kosmos.nuvanta-holding.com
```

---

## 🎯 Prevention

- Implement comprehensive error handling
- Add circuit breakers for external dependencies
- Regular load testing
- Monitor error rate trends
- Automated rollback capabilities

---

## 📝 Post-Mortem Questions

- What caused the error rate spike?
- How quickly did we detect it?
- Was the response effective?
- What can we do to prevent recurrence?
- Should we update our alerting thresholds?