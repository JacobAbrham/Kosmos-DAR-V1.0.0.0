# Zeus Deployment Runbook

**Last Updated:** 2025-12-13

## Overview

Deployment procedures specific to Zeus Orchestrator agent.

## Prerequisites

- [ ] All specialized agents deployed
- [ ] MCP servers operational
- [ ] LangGraph runtime configured
- [ ] Message broker (Redis/RabbitMQ) available

## Deployment

### 1. Deploy Dependencies

```bash
# Deploy message broker
kubectl apply -f k8s/infrastructure/redis-cluster.yaml

# Deploy MCP servers
kubectl apply -f k8s/mcp/
```

### 2. Deploy Zeus

```bash
# Apply Zeus configuration
kubectl apply -f k8s/agents/zeus/configmap.yaml

# Deploy Zeus orchestrator
kubectl apply -f k8s/agents/zeus/deployment.yaml

# Verify deployment
kubectl rollout status deployment/zeus-orchestrator -n kosmos
```

### 3. Configure Routing

```bash
# Apply routing rules
kubectl apply -f k8s/agents/zeus/routing-config.yaml

# Test routing
curl -X POST https://api.kosmos.internal/zeus/route \
  -H "Content-Type: application/json" \
  -d '{"query": "test routing", "context": {}}'
```

## Health Checks

```bash
# Check Zeus pod health
kubectl get pods -n kosmos -l app=zeus-orchestrator

# View orchestration metrics
kubectl exec -it deployment/zeus-orchestrator -n kosmos -- \
  curl localhost:9090/metrics | grep zeus_routing
```

## Related Documentation

- [Zeus Orchestrator Architecture](../../02-architecture/agents/zeus-orchestrator)
- [Zeus Scaling](zeus-scaling)
