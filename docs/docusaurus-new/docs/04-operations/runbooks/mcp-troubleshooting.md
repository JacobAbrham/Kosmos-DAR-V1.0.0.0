# MCP Server Troubleshooting

**Last Updated:** 2025-12-13

## Overview

Troubleshooting guide for Model Context Protocol (MCP) server issues in KOSMOS.

## Common Issues

### 1. MCP Server Not Starting

**Symptoms:**
- Server fails to initialize
- Connection refused errors

**Diagnosis:**
```bash
# Check server logs
kubectl logs -n kosmos -l app=mcp-server

# Verify configuration
kubectl get configmap mcp-config -n kosmos -o yaml
```

**Resolution:**
- Verify MCP server configuration
- Check network connectivity
- Ensure required environment variables are set
- Validate authentication credentials

### 2. Connection Timeouts

**Symptoms:**
- Clients cannot connect to MCP server
- Timeout errors in logs

**Diagnosis:**
```bash
# Test connectivity
kubectl exec -it <client-pod> -n kosmos -- \
  curl -v http://mcp-server:8080/health

# Check service endpoints
kubectl get endpoints mcp-server -n kosmos
```

**Resolution:**
- Verify service configuration
- Check network policies
- Review firewall rules
- Validate DNS resolution

### 3. Memory Server Issues

**Symptoms:**
- Memory operations failing
- State not persisting

**Diagnosis:**
```bash
# Check memory server status
npx -y @modelcontextprotocol/server-memory --check

# Verify storage backend
kubectl get pvc -n kosmos | grep memory
```

**Resolution:**
- Check storage availability
- Verify persistence configuration
- Review memory limits
- Clear corrupted state if necessary

### 4. Sequential Thinking Server Errors

**Symptoms:**
- Reasoning chains incomplete
- Step execution failures

**Diagnosis:**
```bash
# View sequential thinking logs
kubectl logs -n kosmos -l app=mcp-sequential-thinking

# Test server directly
npx -y @modelcontextprotocol/server-sequential-thinking --debug
```

**Resolution:**
- Verify model access
- Check token limits
- Review reasoning configuration
- Validate input formatting

## Performance Issues

### High Latency

**Check:**
- Network latency between client and server
- Model inference time
- Database query performance
- Cache hit rates

### High Resource Usage

**Monitor:**
```bash
# CPU and memory usage
kubectl top pods -n kosmos -l component=mcp

# Active connections
kubectl exec -it <mcp-pod> -n kosmos -- \
  netstat -an | grep ESTABLISHED | wc -l
```

## MCP Configuration Validation

```bash
# Validate MCP settings
python validate_mcp_config.py

# Test MCP connection
curl -X POST http://mcp-server:8080/api/v1/health \
  -H "Content-Type: application/json"
```

## Debugging Tips

1. **Enable Debug Logging:**
   ```bash
   kubectl set env deployment/mcp-server -n kosmos MCP_LOG_LEVEL=debug
   ```

2. **Trace MCP Calls:**
   ```bash
   kubectl logs -f -n kosmos deployment/mcp-server | grep "MCP:"
   ```

3. **Check MCP Protocol Version:**
   ```bash
   curl http://mcp-server:8080/api/version
   ```

## Emergency Recovery

### Restart MCP Servers

```bash
# Restart all MCP servers
kubectl rollout restart deployment -n kosmos -l component=mcp

# Verify restart
kubectl rollout status deployment/mcp-server -n kosmos
```

### Clear MCP Cache

```bash
# Clear cache volume
kubectl exec -it <mcp-pod> -n kosmos -- rm -rf /var/cache/mcp/*

# Restart to rebuild cache
kubectl delete pod -n kosmos -l app=mcp-server
```

## Related Documentation

- [MCP Integration Guide](../../developer-guide/mcp-integration/README)
- [Memory Server Setup](../../developer-guide/MCP_MEMORY_SERVER_SETUP)
- [Sequential Thinking Setup](../../developer-guide/MCP_SEQUENTIAL_THINKING_SETUP)
- [Agent Deployment](agent-deployment)
