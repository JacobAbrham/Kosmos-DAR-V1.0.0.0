# Zeus Routing Troubleshooting

**Last Updated:** 2025-12-13

## Overview

Troubleshooting guide for Zeus Orchestrator routing issues.

## Common Routing Issues

### 1. Incorrect Agent Selection

**Symptoms:**
- Wrong agent handling request
- Routing to default fallback agent

**Diagnosis:**
```bash
# View routing decisions
kubectl logs -n kosmos deployment/zeus-orchestrator | grep "ROUTING_DECISION"

# Check routing configuration
kubectl get configmap zeus-routing-config -n kosmos -o yaml
```

**Resolution:**
- Review routing rules
- Update agent capability definitions
- Retrain routing classifier if using ML-based routing

### 2. Routing Timeout

**Symptoms:**
- Routing decision takes > 2 seconds
- Gateway timeout errors

**Diagnosis:**
```bash
# Check routing latency metrics
kubectl exec -it deployment/zeus-orchestrator -n kosmos -- \
  curl localhost:9090/metrics | grep routing_duration

# View slow routing queries
kubectl logs -n kosmos deployment/zeus-orchestrator | grep "SLOW_ROUTING"
```

**Resolution:**
- Optimize routing rules
- Add routing cache
- Scale Zeus replicas
- Review agent availability checks

### 3. Circular Routing

**Symptoms:**
- Agents calling each other in loop
- Orchestration never completes

**Diagnosis:**
```bash
# Trace routing path
kubectl logs -n kosmos deployment/zeus-orchestrator | grep "conversation:${CONV_ID}"

# Check for routing cycles
python scripts/analyze_routing.py --conversation ${CONV_ID}
```

**Resolution:**
- Add max routing depth limit
- Implement routing loop detection
- Review agent delegation rules

### 4. Agent Unavailable

**Symptoms:**
- Routing to offline agent
- "Agent not found" errors

**Diagnosis:**
```bash
# Check agent registry
curl https://api.kosmos.internal/zeus/agents/status

# View agent health
kubectl get pods -n kosmos -l component=agent
```

**Resolution:**
- Update agent registry
- Implement agent health checks in routing
- Configure fallback agents

## Routing Configuration

### Update Routing Rules

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: zeus-routing-config
  namespace: kosmos
data:
  routing-rules.yaml: |
    rules:
      - pattern: ".*question about.*"
        agent: athena-knowledge
        confidence: 0.95
      
      - pattern: ".*summarize.*|.*tldr.*"
        agent: prometheus-code
        confidence: 0.90
      
      - pattern: ".*"
        agent: default-assistant
        confidence: 0.50
```

### Test Routing

```bash
# Test routing decision
curl -X POST https://api.kosmos.internal/zeus/test-routing \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Can you explain quantum computing?",
    "context": {}
  }'
```

## Monitoring

Enable routing metrics:
```bash
kubectl set env deployment/zeus-orchestrator -n kosmos \
  ENABLE_ROUTING_METRICS=true
```

View routing statistics:
```bash
# Routing success rate
kubectl exec -it deployment/zeus-orchestrator -n kosmos -- \
  curl localhost:9090/metrics | grep routing_success_rate

# Agent usage distribution
kubectl exec -it deployment/zeus-orchestrator -n kosmos -- \
  curl localhost:9090/metrics | grep agent_invocation_count
```

## Related Documentation

- [Zeus Architecture](../../02-architecture/agents/zeus-orchestrator.md)
- [Inter-Agent Communication](../../02-architecture/agents/inter-agent-communication.md)
- [Zeus Deployment](zeus-deployment.md)
