# Agent Deployment Runbook

**Last Updated:** 2025-12-13

## Overview

Standard operating procedure for deploying KOSMOS agents to production infrastructure.

## Prerequisites

- [ ] Agent code reviewed and approved
- [ ] Integration tests passed
- [ ] Security scan completed
- [ ] Infrastructure capacity verified
- [ ] Deployment window scheduled

## Deployment Steps

### 1. Pre-Deployment Checks

```bash
# Verify agent configuration
kubectl get configmap agent-config -n kosmos -o yaml

# Check resource availability
kubectl top nodes
kubectl describe nodes | grep -A 5 "Allocated resources"
```

### 2. Deploy Agent

```bash
# Apply agent manifests
kubectl apply -f k8s/agents/deployment.yaml

# Verify deployment
kubectl rollout status deployment/<agent-name> -n kosmos
```

### 3. Health Checks

```bash
# Check pod status
kubectl get pods -n kosmos -l app=<agent-name>

# View logs
kubectl logs -f deployment/<agent-name> -n kosmos

# Test agent endpoint
curl -X POST https://api.kosmos.internal/agents/<agent-name>/health
```

### 4. Monitoring Setup

- Configure Prometheus alerts
- Set up Grafana dashboard
- Enable distributed tracing
- Configure log aggregation

## Rollback Procedure

```bash
# Rollback to previous version
kubectl rollout undo deployment/<agent-name> -n kosmos

# Verify rollback
kubectl rollout status deployment/<agent-name> -n kosmos
```

## Post-Deployment

- [ ] Verify metrics collection
- [ ] Test agent functionality
- [ ] Update documentation
- [ ] Notify stakeholders

## Troubleshooting

### Agent Not Starting

Check pod events:
```bash
kubectl describe pod <pod-name> -n kosmos
```

### High Memory Usage

Review resource limits and requests in deployment manifest.

### Connection Issues

Verify network policies and service mesh configuration.

## Related Documentation

- [Agent Scaling](agent-scaling.md)
- [Agent Recovery](agent-recovery.md)
- [MCP Server Troubleshooting](mcp-troubleshooting.md)
