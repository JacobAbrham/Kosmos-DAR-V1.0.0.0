# Deployment Checklist

:::warning Pre-Deployment Verification
    Complete all checklist items before proceeding with KOSMOS deployment.

## Phase 1: Infrastructure Foundation

### Wave 0: Network & TLS

- [x] Alibaba Cloud account provisioned
- [x] VPC created in me-central-1 (Dubai)
- [x] K3s cluster initialized
- [x] cert-manager installed
- [x] Linkerd service mesh deployed
- [x] TLS certificates issued

### Wave 1: Database

- [x] PostgreSQL 16 deployed
- [x] PgBouncer configured
- [x] Extensions enabled:
  - [x] pgvector
  - [x] Apache AGE
  - [x] pg_trgm
- [x] Initial schemas created
- [x] Backup schedule configured

### Wave 2: Cache & Storage

- [x] Dragonfly deployed
- [x] MinIO deployed
- [x] Buckets created:
  - [x] kosmos-documents
  - [x] kosmos-media
  - [x] kosmos-backups
- [x] Retention policies set

### Wave 3: Messaging

- [x] NATS JetStream deployed
- [x] Streams configured:
  - [x] AGENT_EVENTS
  - [x] SYSTEM_EVENTS
  - [x] AUDIT_LOG
- [x] Consumer groups created

### Wave 4: Identity & Secrets

- [x] Zitadel deployed
- [x] Machine User created for Zeus
- [x] Infisical deployed
- [x] Initial secrets populated

### Wave 5: Observability

- [x] SigNoz deployed
- [x] Langfuse deployed
- [x] Dashboards imported
- [x] Alert rules configured

### Wave 6: Security

- [x] Kyverno policies applied
- [x] Falco rules deployed
- [x] Trivy scanner configured
- [x] Initial security scan passed

### Wave 7: AI Inference

- [x] Ollama deployed
- [x] Models pulled:
  - [x] llama3.2:3b
  - [x] nomic-embed-text
- [x] LiteLLM deployed
- [x] Model routing configured
- [x] HuggingFace endpoint verified

## Phase 2: Agent Deployment

### Core Agents

- [x] Zeus supervisor operational
- [x] Hermes orchestrator operational
- [x] AEGIS security agent operational

### Knowledge Agents

- [x] Athena knowledge agent operational
- [x] Chronos scheduler operational

### Operations Agents

- [x] Hephaestus operations agent operational
- [x] Nur PROMETHEUS analytics operational

### Support Agents

- [x] Iris communications operational
- [x] MEMORIX memory operational
- [x] Hestia personal operational
- [x] Morpheus learning operational

## Verification Checklist

### Health Checks

```bash
# Verify all pods running
kubectl get pods -n kosmos

# Check service endpoints
kubectl get svc -n kosmos

# Verify database connectivity
kubectl exec -it postgres-0 -- pg_isready

# Check NATS cluster
kubectl exec -it nats-0 -- nats server check
```

### Agent Communication

```bash
# Verify Zeus → NATS
curl http://zeus:8080/health

# Test agent routing
curl -X POST http://hermes:8080/route \
  -d '{"intent": "test", "message": "hello"}'
```

### Security Verification

- [ ] mTLS between all services
- [ ] Network policies enforced
- [ ] RBAC configured correctly
- [ ] Secrets not exposed in logs

## Post-Deployment

- [x] Smoke tests passed
- [x] Monitoring dashboards accessible
- [x] Audit logging verified
- [x] Backup tested with restore
- [x] Documentation updated

---

**Target Environment:** 32GB RAM Alibaba Cloud ECS  
**Last Updated:** December 2025
