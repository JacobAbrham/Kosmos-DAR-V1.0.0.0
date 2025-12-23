# K3s Configuration

**Lightweight Kubernetes for KOSMOS Deployment**

:::info Why K3s
    K3s provides production-grade Kubernetes with reduced resource footprint, ideal for the 32GB CCX33 target environment.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    K3s CLUSTER TOPOLOGY                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  STAGING (Single Node - 32GB)                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  k3s-staging-01 (control-plane + worker)            │   │
│  │  • API Server, Scheduler, Controller                │   │
│  │  • All workloads                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  PRODUCTION (3 Nodes - 32GB each)                          │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐    │
│  │ k3s-prod-01   │ │ k3s-prod-02   │ │ k3s-prod-03   │    │
│  │ control-plane │ │ control-plane │ │ control-plane │    │
│  │ + worker      │ │ + worker      │ │ + worker      │    │
│  └───────────────┘ └───────────────┘ └───────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequisites

| Requirement | Staging | Production |
|-------------|---------|------------|
| OS | Ubuntu 24.04 LTS | Ubuntu 24.04 LTS |
| CPU | 8 vCPU | 8 vCPU × 3 |
| RAM | 32 GB | 32 GB × 3 |
| Disk | 500 GB NVMe | 500 GB NVMe × 3 |
| Network | Private VLAN | Private VLAN |

### Staging Installation

```bash
# Install K3s on single node
curl -sfL https://get.k3s.io | sh -s - \
  --disable traefik \
  --disable servicelb \
  --write-kubeconfig-mode 644 \
  --node-name k3s-staging-01 \
  --cluster-init

# Verify installation
kubectl get nodes
kubectl get pods -A
```

### Production Installation

```bash
# First control-plane node
curl -sfL https://get.k3s.io | sh -s - \
  --disable traefik \
  --disable servicelb \
  --write-kubeconfig-mode 644 \
  --node-name k3s-prod-01 \
  --cluster-init \
  --tls-san k3s.kosmos.nuvanta.local

# Get token for joining
cat /var/lib/rancher/k3s/server/node-token

# Additional control-plane nodes
curl -sfL https://get.k3s.io | sh -s - \
  --server https://k3s-prod-01:6443 \
  --token <NODE_TOKEN> \
  --node-name k3s-prod-02
```

---

## Configuration Files

### `/etc/rancher/k3s/config.yaml`

```yaml
# K3s server configuration
write-kubeconfig-mode: "0644"
tls-san:
  - "k3s.kosmos.nuvanta.local"
  - "10.0.1.10"

# Disable default components (we use alternatives)
disable:
  - traefik        # Using Kong instead
  - servicelb      # Using MetalLB instead

# Kubelet configuration
kubelet-arg:
  - "max-pods=110"
  - "eviction-hard=memory.available&lt;500Mi,nodefs.available&lt;10%"
  - "system-reserved=cpu=500m,memory=1Gi"
  - "kube-reserved=cpu=500m,memory=1Gi"

# etcd configuration (embedded)
etcd-expose-metrics: true

# Networking
flannel-backend: vxlan
cluster-cidr: "10.42.0.0/16"
service-cidr: "10.43.0.0/16"
cluster-dns: "10.43.0.10"
```

---

## Resource Allocation

### Namespace Quotas

```yaml
# namespaces/kosmos-agents-quota.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: agent-quota
  namespace: kosmos-agents
spec:
  hard:
    requests.cpu: "8"
    requests.memory: "16Gi"
    limits.cpu: "12"
    limits.memory: "24Gi"
    pods: "50"
```

### Limit Ranges

```yaml
# namespaces/kosmos-agents-limits.yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: agent-limits
  namespace: kosmos-agents
spec:
  limits:
    - default:
        cpu: "500m"
        memory: "512Mi"
      defaultRequest:
        cpu: "100m"
        memory: "128Mi"
      type: Container
```

---

## Namespaces

| Namespace | Purpose | Resource Limit |
|-----------|---------|----------------|
| `kosmos-system` | Core infrastructure | 4Gi |
| `kosmos-agents` | Agent deployments | 16Gi |
| `kosmos-data` | PostgreSQL, Dragonfly | 8Gi |
| `kosmos-observability` | SigNoz, Langfuse | 4Gi |

```bash
# Create namespaces
kubectl create namespace kosmos-system
kubectl create namespace kosmos-agents
kubectl create namespace kosmos-data
kubectl create namespace kosmos-observability

# Apply labels
kubectl label namespace kosmos-agents app.kubernetes.io/part-of=kosmos
```

---

## Storage Configuration

### Local Path Provisioner

K3s includes local-path-provisioner by default:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-data
  namespace: kosmos-data
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: local-path
  resources:
    requests:
      storage: 100Gi
```

### Storage Classes

```yaml
# storage/fast-storage.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-local
provisioner: rancher.io/local-path
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer
parameters:
  nodePath: /mnt/fast-storage
```

---

## Networking

### MetalLB Configuration

```yaml
# metallb/config.yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: kosmos-pool
  namespace: metallb-system
spec:
  addresses:
    - 10.0.1.100-10.0.1.110

---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: kosmos-l2
  namespace: metallb-system
spec:
  ipAddressPools:
    - kosmos-pool
```

### Kong Ingress

```yaml
# kong/values.yaml (Helm)
ingressController:
  enabled: true
  installCRDs: false

proxy:
  type: LoadBalancer
  loadBalancerIP: 10.0.1.100

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

---

## Maintenance Commands

```bash
# Node operations
kubectl drain k3s-prod-01 --ignore-daemonsets --delete-emptydir-data
kubectl uncordon k3s-prod-01

# Backup etcd (critical!)
k3s etcd-snapshot save --name pre-upgrade-backup

# Restore from snapshot
k3s server --cluster-reset --cluster-reset-restore-path=/path/to/snapshot

# Upgrade K3s
curl -sfL https://get.k3s.io | INSTALL_K3S_CHANNEL=stable sh -

# Check cluster health
kubectl get nodes -o wide
kubectl top nodes
kubectl get componentstatuses
```

---

## Monitoring Integration

### Metrics Server

```bash
# Already included in K3s, verify:
kubectl top nodes
kubectl top pods -A
```

### SigNoz Integration

```yaml
# Expose K3s metrics to SigNoz
apiVersion: v1
kind: Service
metadata:
  name: k3s-metrics
  namespace: kube-system
  labels:
    app: k3s-metrics
spec:
  ports:
    - name: metrics
      port: 10250
      targetPort: 10250
  selector:
    node-role.kubernetes.io/master: "true"
```

---

## Troubleshooting

### Common Issues

| Issue | Diagnosis | Resolution |
|-------|-----------|------------|
| Node NotReady | `kubectl describe node` | Check kubelet logs |
| Pod Pending | `kubectl describe pod` | Check resource limits |
| DNS issues | `kubectl run test --image=busybox -it -- nslookup kubernetes` | Restart coredns |
| etcd slow | Check disk I/O | Use NVMe storage |

### Log Locations

```bash
# K3s server logs
journalctl -u k3s -f

# Kubelet logs
journalctl -u k3s -f | grep kubelet

# Container logs
kubectl logs -n kosmos-agents deployment/zeus -f
```

---

## See Also

- [Alibaba Cloud Setup](alibaba-cloud)
- [Boot Sequence](boot-sequence)
- [Disaster Recovery](../../security/disaster-recovery)

---

**Last Updated:** December 2025
