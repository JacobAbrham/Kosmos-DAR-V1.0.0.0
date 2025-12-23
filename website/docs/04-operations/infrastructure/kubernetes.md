# Kubernetes Architecture

**Document Type:** Infrastructure Architecture  
**Owner:** Platform Engineering  
**Reviewers:** Infrastructure Architect, Security Lead, SRE Lead  
**Review Cadence:** Quarterly  
**Last Updated:** 2025-12-13  
**Status:** 🟢 Active

---

## Executive Summary

KOSMOS runs on Kubernetes (K3s) with a phased deployment architecture: local development uses Docker Compose, staging uses single-node K3s on Alibaba Cloud, and production runs a 3-node K3s cluster. This document details cluster topology, namespace organization, networking, storage, and operational procedures.

---

## Deployment Environments

| Environment | Infrastructure | Nodes | Purpose |
|-------------|---------------|-------|---------|
| Development | Docker Compose | N/A | Local development |
| Staging | K3s Single Node | 1 | Integration testing |
| Production | K3s HA Cluster | 3 | Production workloads |

---

## Cluster Topology

### Production Cluster Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        KOSMOS Production Cluster                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     Control Plane (HA)                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │   Node 1    │  │   Node 2    │  │   Node 3    │              │   │
│  │  │ k3s-server  │  │ k3s-server  │  │ k3s-server  │              │   │
│  │  │  + etcd     │  │  + etcd     │  │  + etcd     │              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                │                                        │
│                         ┌──────┴──────┐                                │
│                         │   Traefik   │                                │
│                         │   Ingress   │                                │
│                         └──────┬──────┘                                │
│                                │                                        │
│  ┌─────────────────────────────┼─────────────────────────────────┐    │
│  │                    Worker Workloads                            │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │    │
│  │  │ kosmos-core │  │ kosmos-db   │  │ kosmos-obs  │            │    │
│  │  │ namespace   │  │ namespace   │  │ namespace   │            │    │
│  │  │             │  │             │  │             │            │    │
│  │  │ - Zeus      │  │ - PostgreSQL│  │ - Prometheus│            │    │
│  │  │ - Athena    │  │ - Dragonfly │  │ - Grafana   │            │    │
│  │  │ - Hermes    │  │ - NATS      │  │ - Loki      │            │    │
│  │  │ - Chronos   │  │ - MinIO     │  │ - Jaeger    │            │    │
│  │  │ - etc.      │  │             │  │ - Langfuse  │            │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘            │    │
│  └───────────────────────────────────────────────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Node Specifications

| Node Role | vCPU | Memory | Storage | Count |
|-----------|------|--------|---------|-------|
| Server (Control + Worker) | 4 | 8 GB | 100 GB SSD | 3 |
| **Total Cluster** | 12 | 24 GB | 300 GB | 3 |

---

## Namespace Organization

### Namespace Inventory

```yaml
# Namespace definitions
apiVersion: v1
kind: Namespace
metadata:
  name: kosmos-core
  labels:
    app.kubernetes.io/part-of: kosmos
    environment: production
---
apiVersion: v1
kind: Namespace
metadata:
  name: kosmos-db
  labels:
    app.kubernetes.io/part-of: kosmos
    tier: data
---
apiVersion: v1
kind: Namespace
metadata:
  name: kosmos-observability
  labels:
    app.kubernetes.io/part-of: kosmos
    tier: monitoring
---
apiVersion: v1
kind: Namespace
metadata:
  name: kosmos-ingress
  labels:
    app.kubernetes.io/part-of: kosmos
    tier: edge
```

### Namespace Purpose Matrix

| Namespace | Purpose | Resource Quota | Network Policy |
|-----------|---------|----------------|----------------|
| `kosmos-core` | Agent services, API | 8 CPU, 16 Gi | Restricted |
| `kosmos-db` | Databases, caches, queues | 4 CPU, 12 Gi | Isolated |
| `kosmos-observability` | Monitoring stack | 2 CPU, 4 Gi | Allow from all |
| `kosmos-ingress` | Ingress controllers | 1 CPU, 2 Gi | External access |
| `kube-system` | K3s system components | Default | System |

---

## Resource Quotas

### kosmos-core Namespace

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: kosmos-core-quota
  namespace: kosmos-core
spec:
  hard:
    requests.cpu: "6"
    requests.memory: 12Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "50"
    services: "20"
    persistentvolumeclaims: "10"
```

### Default Limit Ranges

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: kosmos-default-limits
  namespace: kosmos-core
spec:
  limits:
  - default:
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:
      cpu: "100m"
      memory: "128Mi"
    type: Container
  - max:
      cpu: "2"
      memory: "4Gi"
    min:
      cpu: "50m"
      memory: "64Mi"
    type: Container
```

---

## Network Configuration

### Network Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    External Traffic                          │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│              Cloudflare (CDN + WAF + DDoS)                   │
└─────────────────────────┬────────────────────────────────────┘
                          │ HTTPS (443)
                          ▼
┌──────────────────────────────────────────────────────────────┐
│              Traefik Ingress Controller                      │
│              (kosmos-ingress namespace)                      │
└─────────────────────────┬────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ kosmos-  │   │ kosmos-  │   │ kosmos-  │
    │ core     │   │ db       │   │ obs      │
    │ :8000    │   │ :5432    │   │ :9090    │
    └──────────┘   └──────────┘   └──────────┘
```

### Service CIDR Configuration

```yaml
# K3s server configuration
# /etc/rancher/k3s/config.yaml
cluster-cidr: "10.42.0.0/16"
service-cidr: "10.43.0.0/16"
cluster-dns: "10.43.0.10"
```

### Network Policies

**Isolate Database Namespace:**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-isolation
  namespace: kosmos-db
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          app.kubernetes.io/part-of: kosmos
    - podSelector:
        matchLabels:
          db-access: "true"
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53
```

**Allow Prometheus Scraping:**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-prometheus-scrape
  namespace: kosmos-core
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: kosmos-observability
      podSelector:
        matchLabels:
          app: prometheus
    ports:
    - protocol: TCP
      port: 8000
```

---

## Storage Configuration

### Storage Classes

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-path
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: rancher.io/local-path
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Delete
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-path-retain
provisioner: rancher.io/local-path
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Retain
```

### Persistent Volume Claims

**PostgreSQL Storage:**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-data
  namespace: kosmos-db
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: local-path-retain
  resources:
    requests:
      storage: 50Gi
```

**MinIO Storage:**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: minio-data
  namespace: kosmos-db
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: local-path-retain
  resources:
    requests:
      storage: 100Gi
```

---

## Ingress Configuration

### Traefik IngressRoute

```yaml
apiVersion: traefik.containo.us/v1alpha1
kind: IngressRoute
metadata:
  name: kosmos-api
  namespace: kosmos-ingress
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`api.kosmos.nuvanta-holding.com`)
      kind: Rule
      services:
        - name: zeus-orchestrator
          namespace: kosmos-core
          port: 8000
      middlewares:
        - name: rate-limit
        - name: cors-headers
  tls:
    certResolver: letsencrypt
---
apiVersion: traefik.containo.us/v1alpha1
kind: Middleware
metadata:
  name: rate-limit
  namespace: kosmos-ingress
spec:
  rateLimit:
    average: 100
    burst: 200
---
apiVersion: traefik.containo.us/v1alpha1
kind: Middleware
metadata:
  name: cors-headers
  namespace: kosmos-ingress
spec:
  headers:
    accessControlAllowMethods:
      - GET
      - POST
      - PUT
      - DELETE
      - OPTIONS
    accessControlAllowOriginList:
      - "https://kosmos.nuvanta-holding.com"
    accessControlMaxAge: 100
    addVaryHeader: true
```

---

## RBAC Configuration

### Service Accounts

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: kosmos-agent
  namespace: kosmos-core
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: kosmos-agent-role
  namespace: kosmos-core
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: kosmos-agent-binding
  namespace: kosmos-core
subjects:
- kind: ServiceAccount
  name: kosmos-agent
  namespace: kosmos-core
roleRef:
  kind: Role
  name: kosmos-agent-role
  apiGroup: rbac.authorization.k8s.io
```

---

## Deployment Strategies

### Rolling Update (Default)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zeus-orchestrator
  namespace: kosmos-core
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: zeus-orchestrator
  template:
    metadata:
      labels:
        app: zeus-orchestrator
    spec:
      serviceAccountName: kosmos-agent
      containers:
      - name: zeus
        image: nuvanta/kosmos-zeus:v2.0.0
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: "200m"
            memory: "512Mi"
          limits:
            cpu: "1"
            memory: "2Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        env:
        - name: POSTGRES_HOST
          valueFrom:
            secretKeyRef:
              name: kosmos-db-credentials
              key: host
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: kosmos-db-credentials
              key: password
```

### Canary Deployment with Argo Rollouts

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: zeus-orchestrator
  namespace: kosmos-core
spec:
  replicas: 3
  strategy:
    canary:
      steps:
      - setWeight: 10
      - pause: {duration: 5m}
      - setWeight: 30
      - pause: {duration: 5m}
      - setWeight: 50
      - pause: {duration: 10m}
      - setWeight: 100
      canaryService: zeus-canary
      stableService: zeus-stable
      trafficRouting:
        traefik:
          weightedTrafficRouting:
            stableService: zeus-stable
            canaryService: zeus-canary
  selector:
    matchLabels:
      app: zeus-orchestrator
  template:
    # ... same as deployment template
```

---

## Health Checks

### Liveness and Readiness Probes

| Service | Liveness Path | Readiness Path | Initial Delay |
|---------|---------------|----------------|---------------|
| Zeus Orchestrator | `/health` | `/ready` | 30s |
| Athena Knowledge | `/health` | `/ready` | 45s |
| PostgreSQL | TCP 5432 | TCP 5432 | 30s |
| Dragonfly | TCP 6379 | TCP 6379 | 10s |
| NATS | `/healthz` | `/healthz` | 10s |

### Startup Probes for Slow Starts

```yaml
startupProbe:
  httpGet:
    path: /health
    port: 8000
  failureThreshold: 30
  periodSeconds: 10
```

---

## Scaling Configuration

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: zeus-hpa
  namespace: kosmos-core
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: zeus-orchestrator
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
```

---

## Cluster Operations

### Installation (K3s HA)

```bash
# Node 1 - Initialize cluster
curl -sfL https://get.k3s.io | sh -s - server \
  --cluster-init \
  --tls-san kosmos-api.nuvanta-holding.com \
  --disable traefik \  # We'll install Traefik manually for more control
  --write-kubeconfig-mode 644

# Get token for joining nodes
sudo cat /var/lib/rancher/k3s/server/node-token

# Node 2 & 3 - Join cluster
curl -sfL https://get.k3s.io | sh -s - server \
  --server https://<node1-ip>:6443 \
  --token <node-token> \
  --tls-san kosmos-api.nuvanta-holding.com
```

### Upgrade Procedure

```bash
# 1. Cordon node
kubectl cordon node-1

# 2. Drain workloads
kubectl drain node-1 --ignore-daemonsets --delete-emptydir-data

# 3. Upgrade K3s
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.29.0+k3s1 sh -

# 4. Verify node status
kubectl get nodes

# 5. Uncordon node
kubectl uncordon node-1

# 6. Repeat for remaining nodes
```

### Backup etcd

```bash
# Create snapshot
k3s etcd-snapshot save --name kosmos-backup-$(date +%Y%m%d)

# List snapshots
k3s etcd-snapshot ls

# Restore from snapshot (disaster recovery)
k3s server \
  --cluster-reset \
  --cluster-reset-restore-path=/var/lib/rancher/k3s/server/db/snapshots/<snapshot-name>
```

---

## Monitoring Integration

### Prometheus ServiceMonitor

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: kosmos-agents
  namespace: kosmos-observability
spec:
  selector:
    matchLabels:
      app.kubernetes.io/part-of: kosmos
  namespaceSelector:
    matchNames:
    - kosmos-core
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

### Key Metrics to Monitor

| Metric | Alert Threshold | Severity |
|--------|-----------------|----------|
| `kube_pod_status_phase{phase="Failed"}` | > 0 for 5m | Critical |
| `kube_deployment_status_replicas_unavailable` | > 0 for 10m | Warning |
| `node_memory_MemAvailable_bytes` | < 1Gi | Critical |
| `node_filesystem_avail_bytes` | < 10Gi | Warning |
| `kube_pod_container_status_restarts_total` | > 5 in 1h | Warning |

---

## Troubleshooting

### Common Issues

**Pod stuck in Pending:**
```bash
kubectl describe pod <pod-name> -n <namespace>
# Check Events section for:
# - Insufficient resources
# - PVC not bound
# - Node selector mismatch
```

**Service not reachable:**
```bash
# Check endpoints
kubectl get endpoints <service-name> -n <namespace>

# Test from within cluster
kubectl run debug --rm -it --image=busybox -- wget -qO- http://<service>:<port>/health
```

**Node NotReady:**
```bash
# Check node conditions
kubectl describe node <node-name>

# Check kubelet logs
journalctl -u k3s -f

# Check system resources
df -h
free -m
```

---

## Related Documentation

- [Disaster Recovery Plan](disaster-recovery)
- [Deployment Architecture](deployment)
- [Security Architecture](../../security/architecture)
- [SLA/SLO Definitions](../sla-slo)

---

**Document Owner:** platform-engineering@nuvanta-holding.com  
**Emergency Contact:** oncall@nuvanta-holding.com
