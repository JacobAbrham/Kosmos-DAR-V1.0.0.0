# ADR-024: Security Architecture

## Status

**Accepted** — December 2025

## Context

KOSMOS requires a comprehensive security architecture that addresses:

1. **Identity and Access Management** — Authentication and authorization for users and agents
2. **Runtime Security** — Detection of anomalous behavior in containers
3. **Policy Enforcement** — Kubernetes-native security policies
4. **Secrets Management** — Secure storage and rotation of credentials
5. **Network Security** — Zero-trust communication between services
6. **Compliance** — ISO 42001, UAE PDPL, GDPR alignment

The architecture must:
- Support AI-specific security concerns (prompt injection, model theft)
- Operate within 32GB memory constraints
- Provide defense-in-depth without excessive complexity
- Enable the AEGIS agent to orchestrate security operations

## Decision

Implement a **defense-in-depth security stack** with four primary layers:

### 1. Identity Layer: Zitadel

Selected over Keycloak for:
- Lower memory footprint (~256MB vs ~1GB)
- Native Go implementation (no JVM)
- Built-in multi-tenancy
- Modern OIDC/SAML implementation

```yaml
zitadel_config:
  authentication:
    methods:
      - oidc
      - saml
      - api_keys (for agents)
    mfa:
      required_roles: [ADMIN, OPERATOR]
      methods: [totp, webauthn]
  
  authorization:
    model: rbac
    roles:
      - ADMIN
      - OPERATOR
      - USER
      - AGENT
    
  agent_auth:
    type: client_credentials
    token_lifetime: 3600
    refresh_enabled: true
```

### 2. Runtime Security Layer: Falco

Real-time syscall monitoring for threat detection:

```yaml
falco_config:
  driver: ebpf  # Lower overhead than kernel module
  
  custom_rules:
    - kosmos_agent_shell_spawn
    - kosmos_mcp_unauthorized_access
    - kosmos_kill_switch_detection
    - kosmos_sensitive_file_access
  
  outputs:
    - signoz (logs)
    - slack (alerts)
    - aegis_webhook (response orchestration)
  
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
```

### 3. Policy Layer: Kyverno

Kubernetes-native policy enforcement:

```yaml
kyverno_policies:
  security:
    - require_non_root
    - require_resource_limits
    - restrict_image_registries
    - require_security_context
  
  kosmos_specific:
    - agent_service_accounts
    - mcp_network_policies
    - secrets_infisical_managed
  
  enforcement:
    validating: Enforce
    mutating: Audit → Enforce
```

### 4. Secrets Layer: Infisical

Secrets management with automatic rotation:

```yaml
infisical_config:
  storage: encrypted_postgres
  
  rotation:
    database_passwords: 30d
    api_keys: 90d
    jwt_signing_keys: 7d
  
  injection:
    method: kubernetes_operator
    sync_interval: 60s
  
  audit:
    access_logging: true
    retention: 365d
```

### 5. Network Security: Linkerd mTLS

Zero-trust service mesh:

```yaml
linkerd_config:
  mtls:
    enabled: true
    mode: strict  # No plaintext allowed
  
  traffic_policy:
    default: deny
    allow:
      - zeus → all_agents
      - agents → mcp_servers
      - all → zitadel
      - all → signoz
```

### 6. AEGIS Agent Integration

The AEGIS agent orchestrates security operations:

```python
class AEGISAgent:
    """Security orchestration agent."""
    
    async def handle_falco_alert(self, alert: FalcoAlert):
        if alert.priority in ["critical", "emergency"]:
            await self.evaluate_kill_switch(alert)
        
        if "unauthorized" in alert.rule.lower():
            await self.quarantine_container(alert.container)
        
        await self.audit_log.record(alert)
    
    async def evaluate_kill_switch(self, trigger: SecurityEvent):
        """Pentarchy-governed kill switch evaluation."""
        votes = await self.request_pentarchy_vote(
            trigger=trigger,
            timeout_seconds=30
        )
        
        if votes.unanimous_halt:
            await self.execute_kill_switch(level="hard")
        elif votes.majority_halt:
            await self.execute_kill_switch(level="soft")
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    IDENTITY                          │   │
│  │                    Zitadel                           │   │
│  │           OIDC │ SAML │ API Keys │ MFA              │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    NETWORK                           │   │
│  │                 Linkerd mTLS                         │   │
│  │           Zero-Trust Service Mesh                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                 │
│  ┌───────────────┬───────┴───────┬───────────────┐        │
│  │    POLICY     │    RUNTIME    │    SECRETS    │        │
│  │   Kyverno     │    Falco      │   Infisical   │        │
│  │               │               │               │        │
│  │ • Admission   │ • eBPF probe  │ • Encrypted   │        │
│  │ • Mutation    │ • Syscalls    │ • Rotation    │        │
│  │ • Audit       │ • K8s audit   │ • Injection   │        │
│  └───────────────┴───────────────┴───────────────┘        │
│                          │                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                AEGIS ORCHESTRATION                   │   │
│  │         Alert Processing │ Kill Switch │ Audit       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Consequences

### Positive

- **Defense in depth** — Multiple security layers prevent single points of failure
- **AI-aware security** — Custom Falco rules for agent-specific threats
- **Low overhead** — Stack fits within 32GB memory constraints (~1.5GB total)
- **Kubernetes-native** — All components integrate naturally with K3s
- **Compliance-ready** — Architecture supports ISO 42001, GDPR, UAE PDPL

### Negative

- **Operational complexity** — Four security components to maintain
- **Learning curve** — Team needs familiarity with each tool
- **Alert fatigue risk** — Multiple sources of security alerts

### Mitigations

| Concern | Mitigation |
|---------|------------|
| Complexity | AEGIS agent abstracts security operations |
| Learning curve | Documented runbooks and training |
| Alert fatigue | SigNoz consolidation, severity filtering |

## Resource Requirements

| Component | CPU Request | Memory Request | Memory Limit |
|-----------|-------------|----------------|--------------|
| Zitadel | 100m | 256Mi | 512Mi |
| Falco | 100m | 256Mi | 512Mi |
| Kyverno | 100m | 256Mi | 512Mi |
| Infisical | 100m | 128Mi | 256Mi |
| **Total** | **400m** | **896Mi** | **1.8Gi** |

## Alternatives Considered

### 1. Keycloak for Identity

**Rejected because:**
- JVM-based, requires 1GB+ memory
- More complex configuration
- Overkill for single-tenant deployment

### 2. OPA/Gatekeeper for Policy

**Rejected because:**
- Kyverno is more Kubernetes-native
- Rego language has steeper learning curve
- Kyverno policies are more readable YAML

### 3. HashiCorp Vault for Secrets

**Rejected because:**
- Significantly higher resource requirements
- More complex operational model
- Infisical provides sufficient features

### 4. Istio for Service Mesh

**Rejected because:**
- 4-5GB memory footprint
- Incompatible with 32GB constraint
- Linkerd provides sufficient mTLS

## Compliance Mapping

| Requirement | Implementation |
|-------------|----------------|
| ISO 42001 AI Governance | AEGIS oversight, kill switch |
| ISO 27001 Access Control | Zitadel RBAC |
| GDPR Data Protection | Infisical encryption, audit logs |
| UAE PDPL | Data residency (Dubai region), consent tracking |
| NIST AI RMF | Falco monitoring, Kyverno policies |

## References

- [Zitadel Documentation](https://zitadel.com/docs)
- [Falco Documentation](https://falco.org/docs/)
- [Kyverno Documentation](https://kyverno.io/docs/)
- [Infisical Documentation](https://infisical.com/docs)
- [AEGIS Agent Specification](../agents/aegis-security.md)
- [Kill Switch Protocol](../../01-governance/kill-switch-protocol.md)

---

**Authors:** Architecture Team, Security Team  
**Reviewers:** AEGIS Agent Lead, Compliance Officer  
**Last Updated:** December 2025
