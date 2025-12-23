# Zeus Scaling Runbook

**Last Updated:** 2025-12-13

## Overview

Scaling procedures for Zeus Orchestrator to handle increased orchestration load.

## Scaling Strategy

Zeus uses a combination of:
- Horizontal pod scaling for request distribution
- Vertical scaling for complex orchestration tasks
- Message queue buffering for burst handling

## Horizontal Scaling

```bash
# Scale Zeus replicas
kubectl scale deployment zeus-orchestrator -n kosmos --replicas=5

# Configure auto-scaling
kubectl apply -f - <<EOF
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: zeus-hpa
  namespace: kosmos
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: zeus-orchestrator
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
  - type: Pods
    pods:
      metric:
        name: orchestration_queue_depth
      target:
        type: AverageValue
        averageValue: "50"
EOF
```

## Message Queue Scaling

```bash
# Scale Redis cluster
kubectl scale statefulset redis-cluster -n kosmos --replicas=5

# Monitor queue depth
kubectl exec -it redis-cluster-0 -n kosmos -- redis-cli INFO stats
```

## Performance Monitoring

Key metrics to watch:
- Routing decision latency
- Agent invocation success rate
- Message queue depth
- Memory usage per orchestration

## Related Documentation

- [Zeus Deployment](zeus-deployment)
- [Performance Tuning](../observability/dashboards)
