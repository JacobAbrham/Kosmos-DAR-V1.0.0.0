# Secrets Management

**Document Type:** Security Operations  
**Owner:** Security Lead  
**Reviewers:** Platform Engineering, SRE, CISO  
**Review Cadence:** Quarterly  
**Last Updated:** 2025-12-13  
**Status:** 🟢 Active  
**Classification:** Internal - Sensitive

---

## Overview

KOSMOS uses Infisical as the primary secrets management solution, with Kubernetes Secrets as the runtime delivery mechanism. This document covers secret lifecycle management, access controls, rotation procedures, and emergency protocols.

---

## Architecture

### Secrets Flow

```
┌───────────────────────────────────────────────────────────────────────┐
│                      Secrets Management Architecture                  │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   ┌─────────────────────────────────────────────────────────────┐    │
│   │                     Infisical Cloud                          │    │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │    │
│   │  │ Development │  │   Staging   │  │     Production      │ │    │
│   │  │ Environment │  │ Environment │  │    Environment      │ │    │
│   │  └─────────────┘  └─────────────┘  └─────────────────────┘ │    │
│   │         │                │                    │             │    │
│   │         └────────────────┼────────────────────┘             │    │
│   │                          │                                   │    │
│   │                    ┌─────▼─────┐                            │    │
│   │                    │   Audit   │                            │    │
│   │                    │    Log    │                            │    │
│   │                    └───────────┘                            │    │
│   └─────────────────────────────────────────────────────────────┘    │
│                              │                                        │
│                              │ Infisical Operator                     │
│                              │ (Kubernetes)                           │
│                              ▼                                        │
│   ┌─────────────────────────────────────────────────────────────┐    │
│   │                   Kubernetes Cluster                         │    │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │    │
│   │  │  K8s Secret │  │  K8s Secret │  │     K8s Secret      │ │    │
│   │  │  postgres   │  │   llm-keys  │  │   external-apis     │ │    │
│   │  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │    │
│   │         │                │                    │             │    │
│   │         └────────────────┼────────────────────┘             │    │
│   │                          │                                   │    │
│   │                          ▼                                   │    │
│   │                   ┌─────────────┐                           │    │
│   │                   │    Pods     │                           │    │
│   │                   │ (env vars)  │                           │    │
│   │                   └─────────────┘                           │    │
│   └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

---

## Secret Categories

### Category Classification

| Category | Examples | Rotation | Access Level |
|----------|----------|----------|--------------|
| **Infrastructure** | DB passwords, cache credentials | 90 days | Platform team |
| **API Keys** | LLM providers, external services | 90 days | Service accounts |
| **Encryption Keys** | JWT signing, data encryption | Annual | Security team |
| **Service Accounts** | Kubernetes SA, cloud IAM | Automatic | System |
| **User Credentials** | Admin accounts | 90 days | Restricted |

### Secret Inventory

```yaml
# Infisical project structure
project: kosmos
environments:
  - development
  - staging
  - production

folders:
  infrastructure:
    - POSTGRES_PASSWORD
    - POSTGRES_REPLICATION_PASSWORD
    - DRAGONFLY_PASSWORD
    - NATS_SYSTEM_PASSWORD
    - MINIO_ROOT_PASSWORD
    - MINIO_SECRET_KEY
  
  llm-providers:
    - HUGGINGFACE_API_KEY
    - OPENAI_API_KEY
    - ANTHROPIC_API_KEY
  
  authentication:
    - JWT_SIGNING_KEY
    - KEYCLOAK_ADMIN_PASSWORD
    - SESSION_SECRET
  
  external-services:
    - CLOUDFLARE_API_TOKEN
    - GITHUB_TOKEN
    - ALIBABA_ACCESS_KEY_SECRET
  
  observability:
    - LANGFUSE_SECRET_KEY
    - GRAFANA_ADMIN_PASSWORD
    - PAGERDUTY_INTEGRATION_KEY
```

---

## Infisical Configuration

### Kubernetes Operator Setup

```yaml
# infisical-operator.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: infisical-operator
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: infisical-operator
  namespace: infisical-operator
spec:
  replicas: 1
  selector:
    matchLabels:
      app: infisical-operator
  template:
    metadata:
      labels:
        app: infisical-operator
    spec:
      serviceAccountName: infisical-operator
      containers:
      - name: operator
        image: infisical/kubernetes-operator:v0.5.0
        env:
        - name: INFISICAL_TOKEN
          valueFrom:
            secretKeyRef:
              name: infisical-service-token
              key: token
        resources:
          limits:
            cpu: 100m
            memory: 128Mi
```

### InfisicalSecret Resources

```yaml
# Database credentials secret
apiVersion: secrets.infisical.com/v1alpha1
kind: InfisicalSecret
metadata:
  name: postgres-credentials
  namespace: kosmos-db
spec:
  hostAPI: https://app.infisical.com
  authentication:
    serviceToken:
      secretRef:
        name: infisical-service-token
        key: token
  managedSecretReference:
    secretName: postgres-credentials
    secretNamespace: kosmos-db
  secretsScope:
    projectSlug: kosmos
    envSlug: production
    secretsPath: /infrastructure
    recursive: false
---
# LLM provider keys
apiVersion: secrets.infisical.com/v1alpha1
kind: InfisicalSecret
metadata:
  name: llm-api-keys
  namespace: kosmos-core
spec:
  hostAPI: https://app.infisical.com
  authentication:
    serviceToken:
      secretRef:
        name: infisical-service-token
        key: token
  managedSecretReference:
    secretName: llm-api-keys
    secretNamespace: kosmos-core
  secretsScope:
    projectSlug: kosmos
    envSlug: production
    secretsPath: /llm-providers
```

---

## Secret Rotation

### Automated Rotation Schedule

| Secret Type | Frequency | Method | Notification |
|-------------|-----------|--------|--------------|
| Database passwords | 90 days | Automated | 7 days before |
| API keys | 90 days | Manual trigger | 14 days before |
| JWT signing keys | Annual | Blue-green | 30 days before |
| Service tokens | 30 days | Automated | None |

### Rotation Procedure: Database Password

```bash
#!/bin/bash
# rotate-postgres-password.sh

set -euo pipefail

# 1. Generate new password
NEW_PASSWORD=$(openssl rand -base64 32)

# 2. Update PostgreSQL
kubectl exec -it postgres-0 -n kosmos-db -- psql -c "
  ALTER USER kosmos PASSWORD '${NEW_PASSWORD}';
"

# 3. Update Infisical
infisical secrets set POSTGRES_PASSWORD="${NEW_PASSWORD}" \
  --env production \
  --path /infrastructure

# 4. Trigger Kubernetes secret sync
kubectl annotate infisicalsecret postgres-credentials \
  -n kosmos-db \
  secrets.infisical.com/force-sync=$(date +%s)

# 5. Rolling restart of dependent services
kubectl rollout restart deployment -n kosmos-core \
  zeus-orchestrator \
  athena-knowledge

# 6. Verify connectivity
kubectl exec -it zeus-orchestrator-xxx -n kosmos-core -- \
  python -c "from db import check_connection; check_connection()"

# 7. Audit log
echo "Password rotation completed at $(date)" >> /var/log/secret-rotation.log
```

### Rotation Procedure: JWT Signing Key

```bash
#!/bin/bash
# rotate-jwt-key.sh
# Blue-green deployment for zero-downtime key rotation

set -euo pipefail

# 1. Generate new key pair
openssl genrsa -out /tmp/jwt-new-private.pem 4096
openssl rsa -in /tmp/jwt-new-private.pem -pubout -out /tmp/jwt-new-public.pem

# 2. Add new key as secondary (both keys valid during transition)
NEW_PRIVATE=$(base64 -w 0 /tmp/jwt-new-private.pem)
NEW_PUBLIC=$(base64 -w 0 /tmp/jwt-new-public.pem)

infisical secrets set JWT_SIGNING_KEY_V2="${NEW_PRIVATE}" \
  --env production \
  --path /authentication

infisical secrets set JWT_PUBLIC_KEY_V2="${NEW_PUBLIC}" \
  --env production \
  --path /authentication

# 3. Deploy auth service with dual-key support
kubectl set env deployment/auth-service -n kosmos-core \
  JWT_SIGNING_KEY_NEW="\$(JWT_SIGNING_KEY_V2)"

# 4. Wait for all tokens signed with old key to expire (15 min default)
echo "Waiting for token expiry grace period..."
sleep 900

# 5. Promote new key to primary
infisical secrets set JWT_SIGNING_KEY="${NEW_PRIVATE}" \
  --env production \
  --path /authentication

infisical secrets delete JWT_SIGNING_KEY_V2 \
  --env production \
  --path /authentication

# 6. Remove old key from auth service
kubectl set env deployment/auth-service -n kosmos-core \
  JWT_SIGNING_KEY_NEW-

# 7. Cleanup
rm -f /tmp/jwt-*.pem

echo "JWT key rotation completed successfully"
```

---

## Access Control

### Role-Based Secret Access

```yaml
# Infisical access policies
policies:
  platform-engineers:
    description: "Full access to infrastructure secrets"
    environments: [development, staging, production]
    paths:
      - /infrastructure/*
      - /observability/*
    permissions: [read, write, delete]
  
  ml-engineers:
    description: "Access to LLM provider keys"
    environments: [development, staging]
    paths:
      - /llm-providers/*
    permissions: [read]
  
  security-team:
    description: "Full access to all secrets"
    environments: [development, staging, production]
    paths:
      - /*
    permissions: [read, write, delete, admin]
  
  ci-cd-pipeline:
    description: "Read-only for deployments"
    environments: [staging, production]
    paths:
      - /infrastructure/*
      - /llm-providers/*
      - /external-services/*
    permissions: [read]
```

### Service Token Scoping

```bash
# Create scoped service token for CI/CD
infisical service-token create \
  --name "github-actions-deploy" \
  --scope "kosmos:production:/infrastructure/*:read" \
  --scope "kosmos:production:/llm-providers/*:read" \
  --expires-in 30d

# Create scoped token for specific service
infisical service-token create \
  --name "zeus-orchestrator" \
  --scope "kosmos:production:/infrastructure/POSTGRES*:read" \
  --scope "kosmos:production:/llm-providers/*:read" \
  --expires-in 7d
```

---

## Emergency Procedures

### Secret Compromise Response

```
┌──────────────────────────────────────────────────────────────┐
│               SECRET COMPROMISE RESPONSE FLOW                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. DETECT                                                   │
│     ├── Alert triggered                                      │
│     ├── Manual report                                        │
│     └── Audit log anomaly                                    │
│            │                                                 │
│            ▼                                                 │
│  2. CONTAIN (< 15 minutes)                                   │
│     ├── Revoke compromised secret                           │
│     ├── Disable associated service accounts                  │
│     └── Block suspicious IP addresses                        │
│            │                                                 │
│            ▼                                                 │
│  3. ROTATE (< 1 hour)                                        │
│     ├── Generate new secrets                                 │
│     ├── Update all dependent services                        │
│     └── Verify service functionality                         │
│            │                                                 │
│            ▼                                                 │
│  4. INVESTIGATE                                              │
│     ├── Review audit logs                                    │
│     ├── Identify exposure scope                              │
│     └── Document findings                                    │
│            │                                                 │
│            ▼                                                 │
│  5. REMEDIATE                                                │
│     ├── Address root cause                                   │
│     ├── Update procedures if needed                          │
│     └── Conduct post-incident review                         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Emergency Rotation Script

```bash
#!/bin/bash
# emergency-rotate-all.sh
# USE ONLY IN CASE OF CONFIRMED COMPROMISE

set -euo pipefail

INCIDENT_ID="$1"
REASON="$2"

if [ -z "$INCIDENT_ID" ] || [ -z "$REASON" ]; then
    echo "Usage: $0 <incident-id> <reason>"
    exit 1
fi

log() {
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $1" | tee -a /var/log/emergency-rotation.log
}

log "=== EMERGENCY SECRET ROTATION INITIATED ==="
log "Incident: $INCIDENT_ID"
log "Reason: $REASON"
log "Initiated by: $(whoami)"

# Confirm with second operator
read -p "This will rotate ALL secrets. Type 'CONFIRM' to proceed: " CONFIRM
if [ "$CONFIRM" != "CONFIRM" ]; then
    log "Rotation cancelled"
    exit 1
fi

# 1. Database credentials
log "Rotating database credentials..."
NEW_PG_PASS=$(openssl rand -base64 32)
kubectl exec postgres-0 -n kosmos-db -- psql -c "ALTER USER kosmos PASSWORD '${NEW_PG_PASS}';"
infisical secrets set POSTGRES_PASSWORD="${NEW_PG_PASS}" --env production --path /infrastructure

# 2. Cache credentials
log "Rotating cache credentials..."
NEW_REDIS_PASS=$(openssl rand -base64 32)
infisical secrets set DRAGONFLY_PASSWORD="${NEW_REDIS_PASS}" --env production --path /infrastructure

# 3. JWT keys
log "Rotating JWT signing keys..."
openssl genrsa -out /tmp/jwt-emergency.pem 4096
NEW_JWT=$(base64 -w 0 /tmp/jwt-emergency.pem)
infisical secrets set JWT_SIGNING_KEY="${NEW_JWT}" --env production --path /authentication
rm /tmp/jwt-emergency.pem

# 4. Invalidate all service tokens
log "Revoking all service tokens..."
infisical service-token revoke-all --project kosmos --confirm

# 5. Force sync all Kubernetes secrets
log "Syncing Kubernetes secrets..."
kubectl get infisicalsecret -A -o name | xargs -I {} kubectl annotate {} \
    secrets.infisical.com/force-sync=$(date +%s) --overwrite

# 6. Rolling restart all services
log "Restarting all services..."
kubectl rollout restart deployment -n kosmos-core --all
kubectl rollout restart deployment -n kosmos-db --all

# 7. Wait for rollout
log "Waiting for rollouts to complete..."
kubectl rollout status deployment -n kosmos-core --timeout=600s
kubectl rollout status deployment -n kosmos-db --timeout=600s

# 8. Verify services
log "Verifying service health..."
sleep 30
curl -f https://api.kosmos.nuvanta-holding.com/health || {
    log "ERROR: Health check failed!"
    exit 1
}

log "=== EMERGENCY ROTATION COMPLETED ==="
log "All secrets rotated. Review audit logs and continue incident response."

# Send notification
./scripts/notify-security.sh "Emergency secret rotation completed for $INCIDENT_ID"
```

---

## Audit Logging

### Audit Events

```json
{
  "timestamp": "2025-12-13T10:30:00Z",
  "event_type": "secret_access",
  "action": "read",
  "user": {
    "id": "user-uuid",
    "email": "engineer@nuvanta-holding.com",
    "ip_address": "192.168.1.100"
  },
  "secret": {
    "path": "/infrastructure/POSTGRES_PASSWORD",
    "environment": "production"
  },
  "result": "success",
  "metadata": {
    "client": "infisical-cli/0.15.0",
    "request_id": "req-uuid"
  }
}
```

### Audit Queries

```bash
# View recent secret access
infisical audit-logs list \
  --project kosmos \
  --env production \
  --action read \
  --since "24h"

# View modifications
infisical audit-logs list \
  --project kosmos \
  --action write,delete \
  --since "7d"

# Export for analysis
infisical audit-logs export \
  --project kosmos \
  --format json \
  --since "30d" \
  > audit-logs-30d.json
```

---

## Development Workflow

### Local Development

```bash
# Pull secrets for local development
infisical run --env development -- docker-compose up

# Or export to .env file (gitignored)
infisical export --env development > .env

# Never commit secrets!
# .gitignore should include:
# .env
# .env.*
# *.pem
# secrets/
```

### CI/CD Integration

```yaml
# GitHub Actions example
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Infisical CLI
        run: |
          curl -1sLf 'https://dl.cloudsmith.io/public/infisical/infisical-cli/setup.deb.sh' | sudo -E bash
          sudo apt-get update && sudo apt-get install -y infisical
      
      - name: Deploy with secrets
        env:
          INFISICAL_TOKEN: ${{ secrets.INFISICAL_SERVICE_TOKEN }}
        run: |
          infisical run --env production -- ./deploy.sh
```

---

## Best Practices

### Do's

- ✅ Use environment-specific secrets
- ✅ Rotate secrets regularly
- ✅ Audit secret access
- ✅ Use service tokens with minimal scope
- ✅ Encrypt secrets at rest and in transit
- ✅ Use secret references, not values in configs

### Don'ts

- ❌ Commit secrets to version control
- ❌ Share secrets via Slack/email
- ❌ Use same secrets across environments
- ❌ Store secrets in environment variables long-term
- ❌ Disable audit logging
- ❌ Use overly permissive access policies

---

## Related Documentation

- [Identity and Access Management](iam)
- [Security Architecture](architecture)
- [Disaster Recovery](../04-operations/infrastructure/disaster-recovery)

---

**Document Owner:** security@nuvanta-holding.com  
**Emergency Contact:** security-emergency@nuvanta-holding.com
