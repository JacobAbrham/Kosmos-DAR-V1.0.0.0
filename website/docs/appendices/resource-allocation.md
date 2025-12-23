# Resource Allocation

**Appendix A: KOSMOS Phase 1 Resource Summary**

:::info 32GB Target Environment
    This appendix details resource allocation for the CCX33 (32GB) staging environment and production cluster specifications.

---

## Staging Environment (Single Node - 32GB)

### System Reserved

| Component | CPU | Memory | Notes |
|-----------|-----|--------|-------|
| OS + System | 500m | 1 GB | Ubuntu 24.04 LTS |
| K3s Control Plane | 500m | 1 GB | API, scheduler, controller |
| kubelet + containerd | 500m | 512 MB | Container runtime |
| **Subtotal Reserved** | **1.5 cores** | **2.5 GB** | |

### Data Layer

| Service | CPU Req | CPU Limit | Mem Req | Mem Limit | Storage |
|---------|---------|-----------|---------|-----------|---------|
| PostgreSQL 16 | 500m | 2 | 2 GB | 4 GB | 100 GB |
| Dragonfly | 200m | 1 | 512 MB | 2 GB | 10 GB |
| NATS | 100m | 500m | 128 MB | 512 MB | 5 GB |
| MinIO | 200m | 1 | 512 MB | 2 GB | 200 GB |
| **Subtotal Data** | **1 core** | **4.5 cores** | **3.1 GB** | **8.5 GB** | **315 GB** |

### AI Services

| Service | CPU Req | CPU Limit | Mem Req | Mem Limit | Notes |
|---------|---------|-----------|---------|-----------|-------|
| Ollama (optional) | 500m | 2 | 2 GB | 4 GB | Mistral-7B |
| Langfuse | 200m | 1 | 512 MB | 1 GB | LLM observability |
| **Subtotal AI** | **700m** | **3 cores** | **2.5 GB** | **5 GB** | |

### Agent Workloads

| Agent | CPU Req | CPU Limit | Mem Req | Mem Limit | Replicas |
|-------|---------|-----------|---------|-----------|----------|
| Zeus | 200m | 500m | 256 MB | 512 MB | 1 |
| Hermes | 100m | 300m | 128 MB | 256 MB | 1 |
| AEGIS | 200m | 500m | 256 MB | 512 MB | 1 |
| Chronos | 100m | 300m | 128 MB | 256 MB | 1 |
| Athena | 200m | 500m | 256 MB | 512 MB | 1 |
| Hephaestus | 100m | 300m | 128 MB | 256 MB | 1 |
| Nur PROMETHEUS | 100m | 300m | 128 MB | 256 MB | 1 |
| Iris | 100m | 300m | 128 MB | 256 MB | 1 |
| MEMORIX | 200m | 500m | 256 MB | 512 MB | 1 |
| Hestia | 100m | 300m | 128 MB | 256 MB | 1 |
| Morpheus | 100m | 300m | 128 MB | 256 MB | 1 |
| **Subtotal Agents** | **1.5 cores** | **4.1 cores** | **1.9 GB** | **3.8 GB** | **11** |

### Observability

| Service | CPU Req | CPU Limit | Mem Req | Mem Limit | Storage |
|---------|---------|-----------|---------|-----------|---------|
| SigNoz (All-in-one) | 500m | 2 | 2 GB | 4 GB | 50 GB |
| **Subtotal Obs** | **500m** | **2 cores** | **2 GB** | **4 GB** | **50 GB** |

### Infrastructure

| Service | CPU Req | CPU Limit | Mem Req | Mem Limit |
|---------|---------|-----------|---------|-----------|
| Kong Ingress | 100m | 500m | 128 MB | 512 MB |
| Zitadel | 100m | 500m | 256 MB | 512 MB |
| Falco | 100m | 500m | 256 MB | 512 MB |
| Kyverno | 100m | 500m | 256 MB | 512 MB |
| **Subtotal Infra** | **400m** | **2 cores** | **896 MB** | **2 GB** |

---

## Total Staging Resources

```
┌─────────────────────────────────────────────────────────────┐
│              STAGING RESOURCE SUMMARY (32GB)                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  CPU ALLOCATION                                            │
│  ─────────────────────────────────────────────────────────│
│  Reserved (OS + K3s):     1.5 cores                        │
│  Data Layer:              1.0 cores (req) / 4.5 (limit)   │
│  AI Services:             0.7 cores (req) / 3.0 (limit)   │
│  Agents:                  1.5 cores (req) / 4.1 (limit)   │
│  Observability:           0.5 cores (req) / 2.0 (limit)   │
│  Infrastructure:          0.4 cores (req) / 2.0 (limit)   │
│  ─────────────────────────────────────────────────────────│
│  TOTAL REQUESTS:          5.6 cores                        │
│  TOTAL LIMITS:            17.1 cores (burstable)          │
│  AVAILABLE:               8 vCPU                          │
│                                                             │
│  MEMORY ALLOCATION                                         │
│  ─────────────────────────────────────────────────────────│
│  Reserved (OS + K3s):     2.5 GB                          │
│  Data Layer:              3.1 GB (req) / 8.5 GB (limit)   │
│  AI Services:             2.5 GB (req) / 5.0 GB (limit)   │
│  Agents:                  1.9 GB (req) / 3.8 GB (limit)   │
│  Observability:           2.0 GB (req) / 4.0 GB (limit)   │
│  Infrastructure:          0.9 GB (req) / 2.0 GB (limit)   │
│  ─────────────────────────────────────────────────────────│
│  TOTAL REQUESTS:          12.9 GB                          │
│  TOTAL LIMITS:            25.8 GB                          │
│  AVAILABLE:               32 GB                            │
│  HEADROOM:                6.2 GB (19%)                     │
│                                                             │
│  STORAGE ALLOCATION                                        │
│  ─────────────────────────────────────────────────────────│
│  PostgreSQL:              100 GB                           │
│  MinIO:                   200 GB                           │
│  SigNoz:                  50 GB                            │
│  Dragonfly + NATS:        15 GB                            │
│  System + Logs:           35 GB                            │
│  ─────────────────────────────────────────────────────────│
│  TOTAL:                   400 GB                           │
│  RECOMMENDED DISK:        500 GB NVMe                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Production Environment (3-Node Cluster)

### Per-Node Allocation

| Node | Role | CPU | Memory | Storage |
|------|------|-----|--------|---------|
| prod-01 | Control + Worker | 8 vCPU | 32 GB | 500 GB |
| prod-02 | Control + Worker | 8 vCPU | 32 GB | 500 GB |
| prod-03 | Control + Worker | 8 vCPU | 32 GB | 500 GB |
| **Total** | | **24 vCPU** | **96 GB** | **1.5 TB** |

### Workload Distribution

```
┌─────────────────────────────────────────────────────────────┐
│              PRODUCTION WORKLOAD DISTRIBUTION               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  prod-01                prod-02                prod-03     │
│  ────────────────────────────────────────────────────────  │
│  PostgreSQL (primary)   PostgreSQL (replica)   MinIO       │
│  Dragonfly              NATS                   SigNoz      │
│  Zeus                   Hermes                 AEGIS       │
│  Chronos                Athena                 Hephaestus  │
│  Zitadel                Langfuse               Kong        │
│  Falco                  Falco                  Falco       │
│  Kyverno                Kyverno                Kyverno     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Cloud Cost Estimate (Alibaba Cloud)

### Staging (me-central-1 Dubai)

| Resource | Spec | Monthly Cost |
|----------|------|--------------|
| ECS (CCX33 equiv) | 8 vCPU, 32 GB | ~$150 |
| Cloud Disk (NVMe) | 500 GB | ~$40 |
| Public IP | Elastic IP | ~$5 |
| Bandwidth | 100 Mbps | ~$30 |
| **Total Staging** | | **~$225/month** |

### Production (3-node)

| Resource | Spec | Monthly Cost |
|----------|------|--------------|
| ECS × 3 | 8 vCPU, 32 GB each | ~$450 |
| Cloud Disk × 3 | 500 GB each | ~$120 |
| SLB | Load Balancer | ~$20 |
| Public IP × 2 | Elastic IPs | ~$10 |
| Bandwidth | 200 Mbps | ~$60 |
| **Total Production** | | **~$660/month** |

---

## Scaling Considerations

### Vertical Scaling (Single Node)

| Config | RAM | Max Agents | Use Case |
|--------|-----|------------|----------|
| Minimal | 16 GB | 5 agents | Development |
| Standard | 32 GB | 11 agents | Staging |
| Enhanced | 64 GB | 11 agents + local LLM | Small production |

### Horizontal Scaling (Multi-Node)

| Config | Nodes | Total RAM | Use Case |
|--------|-------|-----------|----------|
| HA Minimal | 3 × 32 GB | 96 GB | Production |
| HA Standard | 3 × 64 GB | 192 GB | Enterprise |
| HA Large | 5 × 64 GB | 320 GB | Large enterprise |

---

## See Also

- [K3s Configuration](../04-operations/infrastructure/k3s-config)
- [Alibaba Cloud Setup](../04-operations/infrastructure/alibaba-cloud)
- [Cost Governance](../01-governance/cost-governance)

---

**Last Updated:** December 2025
