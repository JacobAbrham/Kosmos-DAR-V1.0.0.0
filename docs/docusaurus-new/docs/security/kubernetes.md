# Kubernetes Security

**Last Updated:** 2025-12-13  
**Status:** Active

## Overview

Kubernetes security controls and best practices for KOSMOS infrastructure.

## Pod Security Standards

### Baseline Policy
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: kosmos
  labels:
    pod-security.kubernetes.io/enforce: baseline
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### Restricted Policy (Production)
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-agent
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: agent
    image: kosmos/agent:latest
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop:
        - ALL
      readOnlyRootFilesystem: true
```

## Network Policies

### Default Deny All
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: kosmos
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

### Agent-to-Agent Communication
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: agent-communication
  namespace: kosmos
spec:
  podSelector:
    matchLabels:
      component: agent
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          component: agent
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          component: agent
    ports:
    - protocol: TCP
      port: 8080
```

## RBAC Configuration

### ServiceAccount
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: agent-sa
  namespace: kosmos
```

### Role
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: agent-role
  namespace: kosmos
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list"]
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]
  resourceNames: ["agent-credentials"]
```

### RoleBinding
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: agent-rolebinding
  namespace: kosmos
subjects:
- kind: ServiceAccount
  name: agent-sa
  namespace: kosmos
roleRef:
  kind: Role
  name: agent-role
  apiGroup: rbac.authorization.k8s.io
```

## Resource Quotas

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: kosmos-quota
  namespace: kosmos
spec:
  hard:
    requests.cpu: "100"
    requests.memory: "200Gi"
    limits.cpu: "200"
    limits.memory: "400Gi"
    persistentvolumeclaims: "20"
    pods: "100"
```

## Admission Controllers

### OPA Gatekeeper Policies

**Require Labels:**
```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          properties:
            labels:
              type: array
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        
        violation[{"msg": msg, "details": {"missing_labels": missing}}] {
          provided := {label | input.review.object.metadata.labels[label]}
          required := {label | label := input.parameters.labels[_]}
          missing := required - provided
          count(missing) > 0
          msg := sprintf("Required labels missing: %v", [missing])
        }
```

## Image Security

### Image Pull Policy
- Always pull from trusted registries
- Use image digests (SHA256) not tags
- Scan images before deployment

### Container Registry Security
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: registry-credentials
  namespace: kosmos
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: <base64-encoded-credentials>
```

## Secrets Management

### Sealed Secrets
```bash
# Encrypt secret
kubeseal --format=yaml < secret.yaml > sealed-secret.yaml

# Apply sealed secret
kubectl apply -f sealed-secret.yaml
```

### External Secrets Operator
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: agent-secrets
  namespace: kosmos
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: agent-credentials
  data:
  - secretKey: api-key
    remoteRef:
      key: kosmos/agents/api-key
```

## Runtime Security

### Falco Rules
```yaml
- rule: Unexpected Network Connection
  desc: Detect unexpected outbound network connections from agents
  condition: >
    spawned_process and container and
    not allowed_k8s_namespaces and
    outbound and
    not allowed_outbound_destinations
  output: >
    Unexpected network connection
    (user=%user.name command=%proc.cmdline connection=%fd.name)
  priority: WARNING
```

## Audit Logging

Enable Kubernetes audit logging:
```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata
  resources:
  - group: ""
    resources: ["secrets", "configmaps"]
- level: RequestResponse
  resources:
  - group: ""
    resources: ["pods"]
  verbs: ["create", "delete", "patch"]
```

## Compliance

- **CIS Kubernetes Benchmark:** Automated compliance checks
- **NSA/CISA Hardening Guide:** Implementation guidelines
- **Pod Security Standards:** Enforced via admission controllers

## Related Documentation

- [IAM](iam)
- [Security Architecture](architecture)
- [Threat Model](threat-model)
