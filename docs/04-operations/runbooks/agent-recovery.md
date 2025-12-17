# Agent Recovery Runbook

**Last Updated:** 2025-12-13

## Overview

Procedures for recovering failed or degraded KOSMOS agents.

## Common Failure Scenarios

### 1. Pod CrashLoopBackOff

**Symptoms:**
- Pod repeatedly crashing
- Status: CrashLoopBackOff

**Diagnosis:**
```bash
kubectl describe pod <pod-name> -n kosmos
kubectl logs <pod-name> -n kosmos --previous
```

**Resolution:**
- Check configuration errors
- Verify environment variables
- Review resource limits
- Check dependencies availability

### 2. Out of Memory (OOM)

**Symptoms:**
- Pod killed by OOM killer
- Exit code 137

**Resolution:**
```bash
# Increase memory limits
kubectl set resources deployment <agent-name> -n kosmos \
  --limits=memory=2Gi --requests=memory=1Gi

# Restart deployment
kubectl rollout restart deployment <agent-name> -n kosmos
```

### 3. Unresponsive Agent

**Symptoms:**
- Health checks failing
- No response to requests

**Diagnosis:**
```bash
# Check liveness probe
kubectl get pods -n kosmos -l app=<agent-name>

# Exec into pod
kubectl exec -it <pod-name> -n kosmos -- /bin/sh
```

**Resolution:**
- Restart pod
- Check for deadlocks
- Review recent code changes

## State Recovery

### Restore from Backup

```bash
# List available backups
kubectl get volumesnapshots -n kosmos

# Restore from snapshot
kubectl apply -f restore-pvc.yaml
```

### Conversation State Recovery

```bash
# Export conversation state
kubectl exec -it <pod-name> -n kosmos -- \
  python -m kosmos.tools.export_state --output /tmp/state.json

# Import conversation state
kubectl cp state.json <pod-name>:/tmp/ -n kosmos
kubectl exec -it <pod-name> -n kosmos -- \
  python -m kosmos.tools.import_state --input /tmp/state.json
```

## Emergency Procedures

### Complete Agent Reset

```bash
# Delete all pods
kubectl delete pods -n kosmos -l app=<agent-name>

# Clear persistent state (if needed)
kubectl delete pvc <agent-pvc> -n kosmos

# Redeploy
kubectl apply -f k8s/agents/<agent-name>/
```

## Post-Recovery

- [ ] Verify agent functionality
- [ ] Check metrics and logs
- [ ] Document root cause
- [ ] Update runbook if needed
- [ ] Conduct post-mortem

## Related Documentation

- [Agent Deployment](agent-deployment.md)
- [MCP Troubleshooting](mcp-troubleshooting.md)
