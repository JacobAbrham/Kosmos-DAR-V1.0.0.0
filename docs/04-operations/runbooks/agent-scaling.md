# Agent Scaling Runbook

**Last Updated:** 2025-12-13

## Overview

Procedures for scaling KOSMOS agents based on load and performance metrics.

## Scaling Triggers

- CPU utilization > 70% for 5 minutes
- Memory utilization > 80%
- Request queue depth > 100
- Response latency > 2 seconds

## Manual Scaling

### Scale Up

```bash
# Increase replica count
kubectl scale deployment <agent-name> -n kosmos --replicas=5

# Verify scaling
kubectl get deployment <agent-name> -n kosmos
kubectl get pods -n kosmos -l app=<agent-name>
```

### Scale Down

```bash
# Decrease replica count
kubectl scale deployment <agent-name> -n kosmos --replicas=2

# Monitor graceful shutdown
kubectl get pods -n kosmos -l app=<agent-name> -w
```

## Auto-Scaling Configuration

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: agent-hpa
  namespace: kosmos
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: <agent-name>
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Monitoring

Check current scaling status:
```bash
kubectl get hpa -n kosmos
kubectl describe hpa agent-hpa -n kosmos
```

## Related Documentation

- [Agent Deployment](agent-deployment.md)
- [Performance Monitoring](../observability/dashboards.md)
