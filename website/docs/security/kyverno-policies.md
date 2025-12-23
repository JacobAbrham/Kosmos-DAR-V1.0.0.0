# Kyverno Policies

**Kubernetes-Native Policy Enforcement**

:::info Policy as Code
    Kyverno provides Kubernetes-native policy management, enforcing security standards and best practices through admission control and background scanning.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   KYVERNO ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Kubernetes API Server                   │   │
│  │                                                      │   │
│  │  CREATE/UPDATE ──► Admission Webhook ──► Kyverno    │   │
│  │                         │                            │   │
│  └─────────────────────────┼────────────────────────────┘   │
│                            │                               │
│                            ▼                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Kyverno Engine                      │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌────────┐ │   │
│  │  │Validate │  │ Mutate  │  │Generate │  │ Verify │ │   │
│  │  │ Rules   │  │ Rules   │  │ Rules   │  │ Images │ │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                               │
│                            ▼                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Policy Reports (CRDs)                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation

```bash
# Install Kyverno
helm repo add kyverno https://kyverno.github.io/kyverno/
helm repo update

helm install kyverno kyverno/kyverno \
  --namespace kyverno \
  --create-namespace \
  --set replicaCount=1 \
  --set resources.requests.cpu=100m \
  --set resources.requests.memory=256Mi
```

---

## KOSMOS Policies

### Pod Security Policies

```yaml
# policies/require-non-root.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-non-root-kosmos
  annotations:
    policies.kyverno.io/title: Require Non-Root for KOSMOS
    policies.kyverno.io/category: Pod Security
    policies.kyverno.io/severity: high
spec:
  validationFailureAction: Enforce
  background: true
  rules:
    - name: check-runAsNonRoot
      match:
        any:
          - resources:
              kinds:
                - Pod
              namespaces:
                - kosmos-agents
                - kosmos-system
      validate:
        message: "KOSMOS pods must run as non-root"
        pattern:
          spec:
            securityContext:
              runAsNonRoot: true
            containers:
              - securityContext:
                  runAsNonRoot: true
                  allowPrivilegeEscalation: false
```

### Resource Limits

```yaml
# policies/require-resource-limits.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-resource-limits-kosmos
spec:
  validationFailureAction: Enforce
  rules:
    - name: check-resource-limits
      match:
        any:
          - resources:
              kinds:
                - Pod
              namespaces:
                - kosmos-agents
      validate:
        message: "All KOSMOS agent containers must have resource limits"
        pattern:
          spec:
            containers:
              - resources:
                  limits:
                    memory: "?*"
                    cpu: "?*"
                  requests:
                    memory: "?*"
                    cpu: "?*"
```

### Image Policies

```yaml
# policies/restrict-image-registries.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: restrict-image-registries
spec:
  validationFailureAction: Enforce
  rules:
    - name: validate-registries
      match:
        any:
          - resources:
              kinds:
                - Pod
              namespaces:
                - kosmos-*
      validate:
        message: "Images must come from approved registries"
        pattern:
          spec:
            containers:
              - image: "ghcr.io/nuvanta-holding/* | registry.kosmos.nuvanta.local/*"
            initContainers:
              - image: "ghcr.io/nuvanta-holding/* | registry.kosmos.nuvanta.local/*"
```

### Network Policies Generation

```yaml
# policies/generate-network-policy.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: generate-default-network-policy
spec:
  rules:
    - name: generate-networkpolicy
      match:
        any:
          - resources:
              kinds:
                - Namespace
              selector:
                matchLabels:
                  app.kubernetes.io/part-of: kosmos
      generate:
        apiVersion: networking.k8s.io/v1
        kind: NetworkPolicy
        name: default-deny-ingress
        namespace: "{{request.object.metadata.name}}"
        data:
          spec:
            podSelector: {}
            policyTypes:
              - Ingress
            ingress:
              - from:
                  - namespaceSelector:
                      matchLabels:
                        app.kubernetes.io/part-of: kosmos
```

### Label Requirements

```yaml
# policies/require-labels.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-kosmos-labels
spec:
  validationFailureAction: Enforce
  rules:
    - name: check-labels
      match:
        any:
          - resources:
              kinds:
                - Deployment
                - StatefulSet
              namespaces:
                - kosmos-*
      validate:
        message: "KOSMOS workloads must have required labels"
        pattern:
          metadata:
            labels:
              app.kubernetes.io/name: "?*"
              app.kubernetes.io/component: "?*"
              app.kubernetes.io/part-of: kosmos
              kosmos.nuvanta.local/agent: "?*"
```

### Secrets Encryption

```yaml
# policies/require-sealed-secrets.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-infisical-secrets
spec:
  validationFailureAction: Audit  # Start with audit, move to enforce
  rules:
    - name: check-secret-source
      match:
        any:
          - resources:
              kinds:
                - Secret
              namespaces:
                - kosmos-*
      validate:
        message: "Secrets must be managed by Infisical"
        pattern:
          metadata:
            annotations:
              infisical.com/managed: "true"
```

---

## Agent-Specific Policies

### Zeus Orchestrator

```yaml
# policies/zeus-policy.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: zeus-orchestrator-policy
spec:
  validationFailureAction: Enforce
  rules:
    - name: zeus-service-account
      match:
        any:
          - resources:
              kinds:
                - Pod
              selector:
                matchLabels:
                  kosmos.nuvanta.local/agent: zeus
      validate:
        message: "Zeus must use dedicated service account"
        pattern:
          spec:
            serviceAccountName: zeus-orchestrator
    
    - name: zeus-network-access
      match:
        any:
          - resources:
              kinds:
                - Pod
              selector:
                matchLabels:
                  kosmos.nuvanta.local/agent: zeus
      validate:
        message: "Zeus pods must have network policy annotation"
        pattern:
          metadata:
            annotations:
              kosmos.nuvanta.local/network-profile: orchestrator
```

### AEGIS Security Agent

```yaml
# policies/aegis-policy.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: aegis-security-policy
spec:
  validationFailureAction: Enforce
  rules:
    - name: aegis-privileged
      match:
        any:
          - resources:
              kinds:
                - Pod
              selector:
                matchLabels:
                  kosmos.nuvanta.local/agent: aegis
      validate:
        message: "AEGIS may run with elevated privileges for security monitoring"
        pattern:
          spec:
            containers:
              - securityContext:
                  capabilities:
                    add:
                      - SYS_PTRACE
                      - NET_ADMIN
```

---

## Policy Reports

### View Policy Results

```bash
# List policy reports
kubectl get policyreports -A

# View violations
kubectl get policyreports -n kosmos-agents -o yaml

# Cluster-wide report
kubectl get clusterpolicyreports
```

### Sample Report

```yaml
apiVersion: wgpolicyk8s.io/v1alpha2
kind: PolicyReport
metadata:
  name: polr-ns-kosmos-agents
  namespace: kosmos-agents
results:
  - category: Pod Security
    message: "validation rule 'check-runAsNonRoot' passed"
    policy: require-non-root-kosmos
    resources:
      - apiVersion: v1
        kind: Pod
        name: zeus-orchestrator-abc123
    result: pass
    rule: check-runAsNonRoot
    scored: true
    timestamp:
      nanos: 0
      seconds: 1702560000
```

---

## Exceptions

### Policy Exceptions (Kyverno 1.9+)

```yaml
# exceptions/infra-exception.yaml
apiVersion: kyverno.io/v2alpha1
kind: PolicyException
metadata:
  name: allow-infra-privileged
  namespace: kyverno
spec:
  exceptions:
    - policyName: require-non-root-kosmos
      ruleNames:
        - check-runAsNonRoot
  match:
    any:
      - resources:
          kinds:
            - Pod
          namespaces:
            - kube-system
            - kosmos-observability
          names:
            - falco-*
            - signoz-*
```

---

## Troubleshooting

```bash
# Check Kyverno logs
kubectl logs -n kyverno -l app.kubernetes.io/name=kyverno -f

# Test policy against resource
kubectl apply -f test-pod.yaml --dry-run=server

# View admission events
kubectl get events --field-selector reason=PolicyViolation

# Debug specific policy
kubectl describe cpol require-non-root-kosmos
```

---

## See Also

- [Falco Runtime](falco-runtime)
- [AEGIS Security Agent](../02-architecture/agents/aegis-security)
- [ADR-024 Security Architecture](../02-architecture/adr/ADR-024-security-architecture)

---

**Last Updated:** December 2025
