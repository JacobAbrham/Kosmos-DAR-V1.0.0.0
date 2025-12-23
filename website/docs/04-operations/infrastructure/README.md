# Infrastructure Documentation

**Document Type:** Index  
**Owner:** Platform Engineering  
**Last Updated:** 2025-12-13  
**Status:** 🟢 Active

---

## Overview

This section provides comprehensive infrastructure documentation for deploying and operating the KOSMOS AI Operating System across various environments and cloud providers.

---

## Documentation Index

### Core Infrastructure

| Document | Description | Status |
|----------|-------------|--------|
| [Kubernetes Architecture](kubernetes) | K3s cluster topology, networking, RBAC | ✅ Complete |
| [Deployment Architecture](deployment) | CI/CD pipelines, release strategies, canary | ✅ Complete |
| [Disaster Recovery](disaster-recovery) | DR procedures, RTO/RPO, backup strategies | ✅ Complete |
| [Database Operations](database-ops) | PostgreSQL, Dragonfly, pgvector runbooks | ✅ Complete |

### Cloud Providers

| Document | Description | Priority |
|----------|-------------|----------|
| [Alibaba Cloud](alibaba-cloud) | Primary deployment (Asia-Pacific) | Primary |
| [Google Cloud Platform](gcp) | Secondary deployment | Secondary |
| [Amazon Web Services](aws) | Tertiary deployment | Tertiary |

---

## Deployment Environments

| Environment | Infrastructure | Purpose | Documentation |
|-------------|---------------|---------|---------------|
| Development | Docker Compose | Local development | [Dev Guide](../../developer-guide/codespaces) |
| Staging | K3s Single Node | Integration testing | [Kubernetes](kubernetes) |
| Production | K3s HA (3 nodes) | Production workloads | [Kubernetes](kubernetes) |

---

## Quick Links

- **Emergency**: [Disaster Recovery](disaster-recovery)
- **Database Issues**: [Database Operations](database-ops)
- **Kubernetes**: [K8s Architecture](kubernetes)
- **Cost Management**: [FinOps Metrics](../finops-metrics)

---

**Document Owner:** platform-engineering@nuvanta-holding.com
