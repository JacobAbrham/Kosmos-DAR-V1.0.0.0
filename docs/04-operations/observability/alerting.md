# Alerting Rules

**Document Type:** Operations Guide  
**Owner:** SRE Team  
**Last Updated:** 2025-12-13  
**Status:** 🟢 Active

---

## Overview

KOSMOS uses Prometheus AlertManager for alert management, routing, and notifications. This document defines all alerting rules, severity levels, and escalation procedures.

---

## Alert Severity Levels

| Severity | Response Time | Examples | Notification |
|----------|---------------|----------|--------------|
| **Critical (P1)** | 15 minutes | Complete outage, data loss | PagerDuty + Slack |
| **High (P2)** | 1 hour | Partial outage, SLO breach | PagerDuty + Slack |
| **Warning (P3)** | 4 hours | Degraded performance | Slack only |
| **Info (P4)** | Next business day | Capacity planning | Slack (low priority) |

---

## AlertManager Configuration

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/xxx/yyy/zzz'
  pagerduty_url: 'https://events.pagerduty.com/v2/enqueue'

route:
  receiver: 'slack-notifications'
  group_by: ['alertname', 'severity', 'agent']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    # Critical alerts - PagerDuty immediate
    - match:
        severity: critical
      receiver: 'pagerduty-critical'
      group_wait: 0s
      repeat_interval: 5m

    # High alerts - PagerDuty during business hours, Slack always
    - match:
        severity: high
      receiver: 'pagerduty-high'
      group_wait: 1m
      repeat_interval: 30m

    # Warning alerts - Slack only
    - match:
        severity: warning
      receiver: 'slack-warnings'
      repeat_interval: 4h

    # Info alerts - Low priority Slack
    - match:
        severity: info
      receiver: 'slack-info'
      repeat_interval: 24h

receivers:
  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: '$PAGERDUTY_CRITICAL_KEY'
        severity: critical
        description: '{{ .CommonAnnotations.summary }}'
        details:
          firing: '{{ template "pagerduty.default.instances" .Alerts.Firing }}'
    slack_configs:
      - channel: '#kosmos-alerts-critical'
        send_resolved: true
        title: '🚨 CRITICAL: {{ .CommonAnnotations.summary }}'
        text: '{{ .CommonAnnotations.description }}'

  - name: 'pagerduty-high'
    pagerduty_configs:
      - service_key: '$PAGERDUTY_HIGH_KEY'
        severity: error
    slack_configs:
      - channel: '#kosmos-alerts'
        send_resolved: true
        title: '⚠️ HIGH: {{ .CommonAnnotations.summary }}'
        text: '{{ .CommonAnnotations.description }}'

  - name: 'slack-warnings'
    slack_configs:
      - channel: '#kosmos-alerts'
        send_resolved: true
        title: '⚡ WARNING: {{ .CommonAnnotations.summary }}'
        text: '{{ .CommonAnnotations.description }}'

  - name: 'slack-info'
    slack_configs:
      - channel: '#kosmos-alerts-info'
        send_resolved: false
        title: 'ℹ️ INFO: {{ .CommonAnnotations.summary }}'

inhibit_rules:
  # Don't send warning if critical is firing
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'agent']

  # Don't send high if critical is firing
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'high'
    equal: ['alertname', 'agent']
```

---

## Alert Rules

### Agent Health Alerts

```yaml
# agent-alerts.yml
groups:
  - name: kosmos-agent-alerts
    rules:
      # Agent down
      - alert: AgentDown
        expr: up{job="kosmos-agents"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Agent {{ $labels.agent }} is down"
          description: "Agent {{ $labels.agent }} has been down for more than 2 minutes."
          runbook_url: "https://docs.kosmos.nuvanta-holding.com/04-operations/incident-response/"

      # High error rate
      - alert: AgentHighErrorRate
        expr: |
          100 * sum(rate(kosmos_agent_requests_total{status="error"}[5m])) by (agent)
          / sum(rate(kosmos_agent_requests_total[5m])) by (agent)
          > 5
        for: 5m
        labels:
          severity: high
        annotations:
          summary: "High error rate on {{ $labels.agent }}"
          description: "Agent {{ $labels.agent }} has error rate of {{ $value | printf \"%.2f\" }}%"
          runbook_url: "https://docs.kosmos.nuvanta-holding.com/04-operations/incident-response/"

      # Warning error rate
      - alert: AgentElevatedErrorRate
        expr: |
          100 * sum(rate(kosmos_agent_requests_total{status="error"}[5m])) by (agent)
          / sum(rate(kosmos_agent_requests_total[5m])) by (agent)
          > 1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Elevated error rate on {{ $labels.agent }}"
          description: "Agent {{ $labels.agent }} has error rate of {{ $value | printf \"%.2f\" }}%"

      # High latency (P99 > 500ms)
      - alert: AgentHighLatency
        expr: |
          histogram_quantile(0.99, sum(rate(kosmos_agent_request_duration_seconds_bucket[5m])) by (agent, le))
          > 0.5
        for: 10m
        labels:
          severity: high
        annotations:
          summary: "High latency on {{ $labels.agent }}"
          description: "Agent {{ $labels.agent }} P99 latency is {{ $value | printf \"%.2f\" }}s"

      # Very high latency (P99 > 2s)
      - alert: AgentCriticalLatency
        expr: |
          histogram_quantile(0.99, sum(rate(kosmos_agent_request_duration_seconds_bucket[5m])) by (agent, le))
          > 2
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Critical latency on {{ $labels.agent }}"
          description: "Agent {{ $labels.agent }} P99 latency is {{ $value | printf \"%.2f\" }}s"

      # Low request rate (potential issue)
      - alert: AgentLowTraffic
        expr: |
          sum(rate(kosmos_agent_requests_total[5m])) by (agent) < 0.1
          and
          sum(rate(kosmos_agent_requests_total[1h])) by (agent) > 1
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Unusually low traffic on {{ $labels.agent }}"
          description: "Agent {{ $labels.agent }} receiving very few requests"
```

### LLM Alerts

```yaml
# llm-alerts.yml
groups:
  - name: kosmos-llm-alerts
    rules:
      # High LLM latency
      - alert: LLMHighLatency
        expr: |
          histogram_quantile(0.99, sum(rate(kosmos_llm_latency_seconds_bucket[5m])) by (model, le))
          > 30
        for: 5m
        labels:
          severity: high
        annotations:
          summary: "LLM {{ $labels.model }} latency is high"
          description: "P99 latency is {{ $value | printf \"%.1f\" }}s"
          runbook_url: "https://docs.kosmos.nuvanta-holding.com/04-operations/incident-response/model-degradation/"

      # Rate limiting
      - alert: LLMRateLimited
        expr: |
          sum(rate(kosmos_llm_rate_limit_hits_total[5m])) by (provider) > 0.1
        for: 5m
        labels:
          severity: high
        annotations:
          summary: "LLM provider {{ $labels.provider }} rate limiting"
          description: "Rate limit hits detected on {{ $labels.provider }}"

      # Cost spike (hourly cost > 2x average)
      - alert: LLMCostSpike
        expr: |
          sum(rate(kosmos_llm_cost_dollars_total[1h])) * 3600
          > 2 * avg_over_time(sum(rate(kosmos_llm_cost_dollars_total[1h]))[24h:1h]) * 3600
        for: 30m
        labels:
          severity: high
        annotations:
          summary: "LLM cost spike detected"
          description: "Current hourly cost (${{ $value | printf \"%.2f\" }}) is more than 2x average"
          runbook_url: "https://docs.kosmos.nuvanta-holding.com/04-operations/incident-response/cost-spike/"

      # Daily cost threshold
      - alert: LLMDailyCostHigh
        expr: |
          sum(increase(kosmos_llm_cost_dollars_total[24h])) > 500
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "LLM daily cost is high"
          description: "24h cost is ${{ $value | printf \"%.2f\" }}"

      # Low cache hit ratio
      - alert: LLMCacheHitRateLow
        expr: |
          sum(rate(kosmos_llm_cache_hits_total[1h]))
          / (sum(rate(kosmos_llm_cache_hits_total[1h])) + sum(rate(kosmos_llm_cache_misses_total[1h])))
          < 0.2
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "LLM cache hit rate is low"
          description: "Cache hit rate is {{ $value | printf \"%.1f\" }}%"
```

### Infrastructure Alerts

```yaml
# infrastructure-alerts.yml
groups:
  - name: kosmos-infrastructure-alerts
    rules:
      # PostgreSQL connection pool exhaustion
      - alert: PostgresConnectionPoolExhausted
        expr: |
          kosmos_db_connections_active / (kosmos_db_connections_active + kosmos_db_connections_idle) > 0.9
        for: 5m
        labels:
          severity: high
        annotations:
          summary: "PostgreSQL connection pool near exhaustion"
          description: "Connection pool utilization is {{ $value | printf \"%.1f\" }}%"
          runbook_url: "https://docs.kosmos.nuvanta-holding.com/04-operations/infrastructure/database-ops/"

      # PostgreSQL down
      - alert: PostgresDown
        expr: pg_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL is down"
          description: "PostgreSQL database is not responding"

      # Slow queries
      - alert: PostgresSlowQueries
        expr: |
          histogram_quantile(0.99, sum(rate(kosmos_db_query_duration_seconds_bucket[5m])) by (le))
          > 1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL slow queries detected"
          description: "P99 query duration is {{ $value | printf \"%.2f\" }}s"

      # Dragonfly (cache) down
      - alert: DragonflyDown
        expr: up{job="dragonfly"} == 0
        for: 1m
        labels:
          severity: high
        annotations:
          summary: "Dragonfly cache is down"
          description: "Cache server is not responding"

      # Low cache hit ratio
      - alert: CacheHitRatioLow
        expr: kosmos_cache_hit_ratio < 0.8
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "Cache hit ratio is low"
          description: "Cache hit ratio is {{ $value | printf \"%.1f\" }}%"

      # High cache memory usage
      - alert: CacheMemoryHigh
        expr: |
          kosmos_cache_memory_bytes / (1024 * 1024 * 1024) > 6
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Cache memory usage is high"
          description: "Cache using {{ $value | printf \"%.1f\" }}GB"

      # NATS down
      - alert: NATSDown
        expr: up{job="nats"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "NATS messaging is down"
          description: "NATS server is not responding"

      # High queue depth
      - alert: QueueDepthHigh
        expr: kosmos_queue_depth > 1000
        for: 10m
        labels:
          severity: high
        annotations:
          summary: "Queue depth is high"
          description: "Queue {{ $labels.queue }} has {{ $value }} pending messages"

      # Consumer lag
      - alert: QueueConsumerLag
        expr: kosmos_queue_consumer_lag > 100
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Queue consumer lag detected"
          description: "Consumer {{ $labels.consumer }} is {{ $value }} messages behind"

      # Storage space
      - alert: StorageSpaceLow
        expr: |
          kosmos_storage_bytes_total / (1024 * 1024 * 1024 * 1024) > 0.8 * 1
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Storage space is running low"
          description: "MinIO storage at {{ $value | printf \"%.1f\" }}TB (80%+ capacity)"
```

### SLO Alerts

```yaml
# slo-alerts.yml
groups:
  - name: kosmos-slo-alerts
    rules:
      # Error budget burn rate - fast burn (2% in 1 hour)
      - alert: ErrorBudgetFastBurn
        expr: |
          sum(rate(kosmos_agent_requests_total{status="error"}[1h]))
          / sum(rate(kosmos_agent_requests_total[1h]))
          > 14.4 * 0.001
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Error budget burning fast"
          description: "At current rate, will exhaust 30-day error budget in 2 days"
          runbook_url: "https://docs.kosmos.nuvanta-holding.com/04-operations/sla-slo/"

      # Error budget burn rate - slow burn (5% in 6 hours)
      - alert: ErrorBudgetSlowBurn
        expr: |
          sum(rate(kosmos_agent_requests_total{status="error"}[6h]))
          / sum(rate(kosmos_agent_requests_total[6h]))
          > 6 * 0.001
        for: 1h
        labels:
          severity: high
        annotations:
          summary: "Error budget burning steadily"
          description: "At current rate, will exhaust 30-day error budget in 5 days"

      # Error budget nearly exhausted
      - alert: ErrorBudgetNearlyExhausted
        expr: |
          (1 - (
            sum(increase(kosmos_agent_requests_total{status="error"}[30d]))
            / sum(increase(kosmos_agent_requests_total[30d]))
          ) / 0.001) < 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Error budget nearly exhausted"
          description: "Only {{ $value | printf \"%.1f\" }}% of error budget remaining"

      # SLO breach
      - alert: SLOBreach
        expr: |
          avg_over_time(up{job="kosmos-agents"}[30d]) < 0.999
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "30-day SLO breached"
          description: "Availability is {{ $value | printf \"%.3f\" }}%, below 99.9% SLO"
```

### Kubernetes Alerts

```yaml
# kubernetes-alerts.yml
groups:
  - name: kosmos-kubernetes-alerts
    rules:
      # Pod not ready
      - alert: PodNotReady
        expr: |
          kube_pod_status_ready{namespace=~"kosmos-.*", condition="true"} == 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Pod {{ $labels.pod }} not ready"
          description: "Pod in namespace {{ $labels.namespace }} has been not ready for 5 minutes"

      # Pod crash looping
      - alert: PodCrashLooping
        expr: |
          rate(kube_pod_container_status_restarts_total{namespace=~"kosmos-.*"}[15m]) > 0
        for: 5m
        labels:
          severity: high
        annotations:
          summary: "Pod {{ $labels.pod }} is crash looping"
          description: "Pod has restarted {{ $value | printf \"%.0f\" }} times in last 15 minutes"

      # High CPU usage
      - alert: PodHighCPU
        expr: |
          sum(rate(container_cpu_usage_seconds_total{namespace=~"kosmos-.*"}[5m])) by (pod)
          / sum(kube_pod_container_resource_limits{resource="cpu", namespace=~"kosmos-.*"}) by (pod)
          > 0.9
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Pod {{ $labels.pod }} CPU usage high"
          description: "Pod using {{ $value | printf \"%.0f\" }}% of CPU limit"

      # High memory usage
      - alert: PodHighMemory
        expr: |
          sum(container_memory_usage_bytes{namespace=~"kosmos-.*"}) by (pod)
          / sum(kube_pod_container_resource_limits{resource="memory", namespace=~"kosmos-.*"}) by (pod)
          > 0.9
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Pod {{ $labels.pod }} memory usage high"
          description: "Pod using {{ $value | printf \"%.0f\" }}% of memory limit"

      # PVC nearly full
      - alert: PVCNearlyFull
        expr: |
          kubelet_volume_stats_used_bytes{namespace=~"kosmos-.*"}
          / kubelet_volume_stats_capacity_bytes{namespace=~"kosmos-.*"}
          > 0.85
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "PVC {{ $labels.persistentvolumeclaim }} nearly full"
          description: "PVC is {{ $value | printf \"%.0f\" }}% full"
```

---

## Silencing Alerts

### Creating a Silence

```bash
# Via AlertManager API
curl -X POST http://alertmanager:9093/api/v2/silences \
  -H "Content-Type: application/json" \
  -d '{
    "matchers": [
      {"name": "alertname", "value": "AgentHighLatency", "isRegex": false},
      {"name": "agent", "value": "zeus", "isRegex": false}
    ],
    "startsAt": "2025-12-13T00:00:00Z",
    "endsAt": "2025-12-13T02:00:00Z",
    "createdBy": "oncall@nuvanta-holding.com",
    "comment": "Planned maintenance window"
  }'
```

### Silence During Deployments

```yaml
# In deployment pipeline
- name: Silence alerts during deployment
  run: |
    SILENCE_ID=$(curl -s -X POST http://alertmanager:9093/api/v2/silences \
      -H "Content-Type: application/json" \
      -d '{
        "matchers": [
          {"name": "agent", "value": "'$AGENT_NAME'", "isRegex": false}
        ],
        "startsAt": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
        "endsAt": "'$(date -u -d "+30 minutes" +%Y-%m-%dT%H:%M:%SZ)'",
        "createdBy": "ci-cd",
        "comment": "Deployment in progress"
      }' | jq -r '.silenceID')
    echo "SILENCE_ID=$SILENCE_ID" >> $GITHUB_ENV

- name: Delete silence after deployment
  if: always()
  run: |
    curl -X DELETE http://alertmanager:9093/api/v2/silence/$SILENCE_ID
```

---

## Escalation Procedures

### Escalation Matrix

| Time Since Alert | Action |
|------------------|--------|
| 0 min | Alert fires, on-call notified |
| 15 min (P1) / 1 hour (P2) | Escalate to secondary on-call |
| 30 min (P1) / 2 hours (P2) | Escalate to team lead |
| 1 hour (P1) / 4 hours (P2) | Escalate to engineering manager |
| 2 hours (P1) | Escalate to CTO |

### On-Call Rotation

```yaml
# PagerDuty schedule
schedules:
  - name: KOSMOS Primary
    type: round_robin
    users:
      - user1@nuvanta-holding.com
      - user2@nuvanta-holding.com
    rotation_virtual_start: "2025-01-01T09:00:00Z"
    handoff_time: "09:00"
    handoff_day: monday

  - name: KOSMOS Secondary
    type: round_robin
    users:
      - user3@nuvanta-holding.com
      - user4@nuvanta-holding.com
```

---

## Related Documentation

- [Metrics & Prometheus](metrics.md)
- [Grafana Dashboards](dashboards.md)
- [Incident Response](../incident-response/README.md)
- [SLA/SLO Definitions](../sla-slo.md)

---

**Document Owner:** sre@nuvanta-holding.com  
**On-Call Escalation:** oncall@nuvanta-holding.com
