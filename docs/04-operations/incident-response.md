# Incident Response

**KOSMOS Incident Management Framework**

!!! warning "On-Call Reference"
    This document serves as the index for incident response procedures. Bookmark for quick access during incidents.

---

## Incident Classification

| Severity | Impact | Response Time | Examples |
|----------|--------|---------------|----------|
| **P1 - Critical** | System down | 15 min | All agents offline, data loss |
| **P2 - High** | Major degradation | 30 min | Core agent failure, auth down |
| **P3 - Medium** | Partial impact | 2 hours | Single agent degraded |
| **P4 - Low** | Minor issue | 24 hours | Non-critical feature broken |

---

## Incident Playbooks

### Agent Issues

| Playbook | Trigger | Link |
|----------|---------|------|
| Loop Detection | Agent stuck in infinite loop | [loop-detection.md](incident-response/loop-detection.md) |
| Model Degradation | LLM quality decline | [model-degradation.md](incident-response/model-degradation.md) |
| Prompt Injection | Detected attack attempt | [prompt-injection.md](incident-response/prompt-injection.md) |

### Infrastructure Issues

| Playbook | Trigger | Link |
|----------|---------|------|
| Data Pipeline Failure | ETL/sync broken | [data-pipeline-failure.md](incident-response/data-pipeline-failure.md) |
| Third-Party API Outage | External service down | [third-party-api-outage.md](incident-response/third-party-api-outage.md) |
| Cost Spike | Unexpected billing increase | [cost-spike.md](incident-response/cost-spike.md) |

---

## Response Procedure

### 1. Detection
```
Alert received → Acknowledge in SigNoz → Assess severity
```

### 2. Triage
```
P1/P2: Page on-call immediately
P3/P4: Create ticket, schedule response
```

### 3. Containment
```
Isolate affected components
Enable circuit breakers if needed
Consider kill switch for P1
```

### 4. Resolution
```
Apply fix or rollback
Verify system health
Clear alerts
```

### 5. Post-Incident
```
Create post-mortem (P1/P2 required)
Update runbooks
Schedule preventive work
```

---

## Escalation Path

```
┌─────────────────────────────────────────────────────────────┐
│                   ESCALATION MATRIX                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  L1: On-Call Engineer                                      │
│      ↓ (15 min no progress)                                │
│  L2: Team Lead                                             │
│      ↓ (30 min no progress)                                │
│  L3: Architecture Team                                     │
│      ↓ (P1 only, 1 hour)                                   │
│  L4: Executive Notification                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Communication Templates

### Status Update (Slack)

```
🔴 INCIDENT: [Brief description]
Severity: P[1-4]
Status: [Investigating|Identified|Monitoring|Resolved]
Impact: [What's affected]
ETA: [Expected resolution time]
Lead: @[name]
```

### Post-Incident Summary

```
Incident: [Title]
Duration: [Start] - [End] ([Duration])
Severity: P[X]
Impact: [Users/systems affected]
Root Cause: [Brief explanation]
Resolution: [What fixed it]
Follow-up: [Ticket links]
```

---

## Quick Actions

### Kill Switch (P1 Only)

```bash
# Requires AEGIS authorization
kubectl exec -n kosmos-agents aegis-xxxxx -- \
  /app/kill-switch --level=soft --reason="incident response"
```

### Circuit Breaker

```bash
# Disable specific agent
kubectl scale -n kosmos-agents deployment/[agent] --replicas=0
```

### Rollback

```bash
# Rollback to previous deployment
kubectl rollout undo -n kosmos-agents deployment/[agent]
```

---

## See Also

- [SigNoz Observability](observability/signoz.md)
- [Kill Switch Protocol](../01-governance/kill-switch-protocol.md)
- [Backup & Recovery](backup-recovery.md)

---

**Last Updated:** December 2025
