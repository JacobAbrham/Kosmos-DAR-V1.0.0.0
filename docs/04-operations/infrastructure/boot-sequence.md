# Boot Sequence (7-Wave Initialization)

!!! info "Infrastructure Startup Order"
    KOSMOS follows a strict 7-wave boot sequence to ensure dependencies are satisfied and services start in the correct order.

## Wave Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    7-WAVE BOOT SEQUENCE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Wave 0 ────► Wave 1 ────► Wave 2 ────► Wave 3                 │
│  Network      Database     Cache        Messaging               │
│  & TLS        & Identity                                        │
│                                                                 │
│  Wave 4 ────► Wave 5 ────► Wave 6 ────► Wave 7                 │
│  Observ-      Security     AI &         Agents                  │
│  ability                   Knowledge                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Wave Details

### Wave 0: Network & TLS (1 GB)

| Component | Resource | Health Check |
|-----------|----------|--------------|
| cert-manager | 128 MB | `/healthz` |
| Linkerd | 512 MB | `/ready` |
| K3s system | 384 MB | API server |

### Wave 1: Database & Identity (5 GB)

| Component | Resource | Health Check |
|-----------|----------|--------------|
| PostgreSQL | 4 GB | pg_isready |
| PgBouncer | 256 MB | TCP 6432 |
| Zitadel | 512 MB | `/healthz` |
| Infisical | 256 MB | `/api/status` |

### Wave 2: Cache & Object Storage (2 GB)

| Component | Resource | Health Check |
|-----------|----------|--------------|
| Dragonfly | 1.5 GB | `PING` |
| MinIO | 512 MB | `/minio/health/live` |

### Wave 3: Messaging (512 MB)

| Component | Resource | Health Check |
|-----------|----------|--------------|
| NATS JetStream | 512 MB | `/healthz` |

### Wave 4: Observability (2.5 GB)

| Component | Resource | Health Check |
|-----------|----------|--------------|
| SigNoz | 2 GB | `/api/v1/health` |
| Langfuse | 512 MB | `/api/public/health` |

### Wave 5: Security (1 GB)

| Component | Resource | Health Check |
|-----------|----------|--------------|
| Kyverno | 384 MB | `/health` |
| Falco | 384 MB | `/healthz` |
| Trivy | 256 MB | TCP 4954 |

### Wave 6: AI & Knowledge (7 GB)

| Component | Resource | Health Check |
|-----------|----------|--------------|
| Ollama | 4 GB | `/api/tags` |
| LiteLLM | 256 MB | `/health` |
| Haystack | 2 GB | `/health` |
| pgvector | (PostgreSQL) | Query test |

### Wave 7: Agents (3.5 GB)

| Agent | Resource | Dependencies |
|-------|----------|--------------|
| Zeus | 512 MB | Wave 1, 3 |
| Hermes | 384 MB | Wave 3, 6 |
| AEGIS | 384 MB | Wave 5 |
| Chronos | 256 MB | Wave 1 |
| Athena | 512 MB | Wave 6 |
| Hephaestus | 384 MB | Wave 1, 3 |
| Nur PROMETHEUS | 256 MB | Wave 4 |
| Iris | 192 MB | Wave 3 |
| MEMORIX | 256 MB | Wave 1, 2 |
| Hestia | 192 MB | Wave 1, 2 |
| Morpheus | 192 MB | Wave 4 |

## Boot Script

```bash
#!/bin/bash
# kosmos-boot.sh - Execute 7-wave boot sequence

set -e

NAMESPACE="kosmos"
TIMEOUT=300

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

wait_for_ready() {
    local deployment=$1
    local timeout=$2
    log "Waiting for $deployment..."
    kubectl rollout status deployment/$deployment -n $NAMESPACE --timeout=${timeout}s
}

# Wave 0: Network & TLS
log "=== WAVE 0: Network & TLS ==="
kubectl apply -f manifests/wave-0/
wait_for_ready cert-manager $TIMEOUT

# Wave 1: Database & Identity
log "=== WAVE 1: Database & Identity ==="
kubectl apply -f manifests/wave-1/
wait_for_ready postgresql $TIMEOUT
wait_for_ready zitadel $TIMEOUT

# Wave 2-7: Continue sequence...
log "=== BOOT SEQUENCE COMPLETE ==="
kosmos status
```

## Total Resource Summary

| Wave | RAM Allocation |
|------|---------------|
| Wave 0 | 1 GB |
| Wave 1 | 5 GB |
| Wave 2 | 2 GB |
| Wave 3 | 512 MB |
| Wave 4 | 2.5 GB |
| Wave 5 | 1 GB |
| Wave 6 | 7 GB |
| Wave 7 | 3.5 GB |
| **Total** | **~22.5 GB** |

---

## See Also

- [Deployment Checklist](../deployment-checklist.md) — Full deployment procedure
- [Resource Allocation](../../appendices/resource-allocation.md) — Memory/CPU breakdown

---

**Last Updated:** December 2025
