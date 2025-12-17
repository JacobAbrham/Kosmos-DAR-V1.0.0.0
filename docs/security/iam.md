# Identity and Access Management

**Document Type:** Security Architecture  
**Owner:** Security Lead  
**Reviewers:** CISO, Platform Engineering, Architecture Review Board  
**Review Cadence:** Quarterly  
**Last Updated:** 2025-12-13  
**Status:** 🟢 Active

---

## Overview

This document defines the Identity and Access Management (IAM) architecture for KOSMOS, covering authentication, authorization, role definitions, and access control policies across all system components.

---

## Authentication Architecture

### Authentication Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     KOSMOS Authentication Flow                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────┐ │
│   │  User   │────▶│  Frontend   │────▶│ Auth Service│────▶│  Zitadel│ │
│   │         │     │  (Next.js)  │     │  (Gateway)  │     │   IdP    │ │
│   └─────────┘     └─────────────┘     └─────────────┘     └─────────┘ │
│        │                                     │                   │      │
│        │                                     │                   │      │
│        │         ┌─────────────┐            │                   │      │
│        │         │   JWT       │◀───────────┘                   │      │
│        │         │   Token     │                                │      │
│        │         └──────┬──────┘                                │      │
│        │                │                                       │      │
│        ▼                ▼                                       │      │
│   ┌─────────────────────────────┐                              │      │
│   │       API Gateway           │                              │      │
│   │  (Token Validation)         │                              │      │
│   └─────────────┬───────────────┘                              │      │
│                 │                                               │      │
│                 ▼                                               │      │
│   ┌─────────────────────────────┐     ┌─────────────────────┐ │      │
│   │    Zeus Orchestrator        │────▶│  Policy Engine      │ │      │
│   │    (Authorization)          │     │  (OPA/Casbin)       │ │      │
│   └─────────────────────────────┘     └─────────────────────┘ │      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Authentication Methods

| Method | Use Case | Implementation |
|--------|----------|----------------|
| **OAuth 2.0 + OIDC** | User authentication | Zitadel |
| **API Keys** | Service-to-service | Custom + rate limiting |
| **JWT Tokens** | Session management | RS256 signed |
| **mTLS** | Internal services | Cert-manager |

### OAuth 2.0 Configuration

```yaml
# Zitadel organization configuration
organization: kosmos
enabled: true
sslRequired: external
registrationAllowed: false
loginWithEmailAllowed: true
duplicateEmailsAllowed: false

clients:
  - clientId: kosmos-web
    enabled: true
    publicClient: true
    redirectUris:
      - "https://kosmos.nuvanta-holding.com/*"
      - "http://localhost:3000/*"
    webOrigins:
      - "https://kosmos.nuvanta-holding.com"
      - "http://localhost:3000"
    standardFlowEnabled: true
    directAccessGrantsEnabled: false
    
  - clientId: kosmos-api
    enabled: true
    publicClient: false
    secret: "${KOSMOS_API_SECRET}"
    serviceAccountsEnabled: true
    standardFlowEnabled: false
    directAccessGrantsEnabled: true
```

### JWT Token Structure

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "kosmos-signing-key-v1"
  },
  "payload": {
    "iss": "https://auth.nuvanta-holding.com/realms/kosmos",
    "sub": "user-uuid-here",
    "aud": "kosmos-api",
    "exp": 1702500000,
    "iat": 1702496400,
    "auth_time": 1702496400,
    "session_state": "session-uuid",
    "acr": "1",
    "realm_access": {
      "roles": ["user", "agent-operator"]
    },
    "resource_access": {
      "kosmos-api": {
        "roles": ["read", "write", "admin"]
      }
    },
    "scope": "openid profile email",
    "email_verified": true,
    "name": "John Doe",
    "preferred_username": "jdoe",
    "email": "jdoe@nuvanta-holding.com",
    "tenant_id": "tenant-uuid",
    "department": "engineering"
  }
}
```

---

## Authorization Model

### Role-Based Access Control (RBAC)

```
┌───────────────────────────────────────────────────────────────┐
│                    KOSMOS RBAC Hierarchy                      │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│                    ┌─────────────────┐                       │
│                    │  Super Admin    │                       │
│                    │  (Platform)     │                       │
│                    └────────┬────────┘                       │
│                             │                                 │
│            ┌────────────────┼────────────────┐               │
│            │                │                │               │
│   ┌────────▼───────┐ ┌─────▼─────┐ ┌───────▼───────┐       │
│   │  Tenant Admin  │ │ Security  │ │   Platform    │       │
│   │                │ │   Admin   │ │   Engineer    │       │
│   └────────┬───────┘ └───────────┘ └───────────────┘       │
│            │                                                 │
│   ┌────────┼────────────────┐                               │
│   │        │                │                               │
│   ▼        ▼                ▼                               │
│ ┌─────┐ ┌─────────┐ ┌────────────┐                         │
│ │User │ │Operator │ │ Developer  │                         │
│ └─────┘ └─────────┘ └────────────┘                         │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Role Definitions

#### Platform-Level Roles

| Role | Description | Scope |
|------|-------------|-------|
| `super-admin` | Full platform access | Global |
| `platform-engineer` | Infrastructure management | Global |
| `security-admin` | Security configuration | Global |

#### Tenant-Level Roles

| Role | Description | Scope |
|------|-------------|-------|
| `tenant-admin` | Full tenant access | Tenant |
| `operator` | Agent operations, monitoring | Tenant |
| `developer` | API access, testing | Tenant |
| `user` | Basic API access | Tenant |
| `viewer` | Read-only access | Tenant |

### Permission Matrix

```yaml
# permissions.yaml
roles:
  super-admin:
    description: "Full platform administration"
    permissions:
      - "platform:*"
      - "tenant:*"
      - "user:*"
      - "agent:*"
      - "config:*"
      - "audit:*"
  
  tenant-admin:
    description: "Full tenant administration"
    permissions:
      - "tenant:read"
      - "tenant:update"
      - "user:create"
      - "user:read"
      - "user:update"
      - "user:delete"
      - "agent:*"
      - "config:read"
      - "config:update"
      - "audit:read"
  
  operator:
    description: "Agent operations and monitoring"
    permissions:
      - "agent:invoke"
      - "agent:read"
      - "conversation:create"
      - "conversation:read"
      - "metrics:read"
      - "logs:read"
  
  developer:
    description: "API development and testing"
    permissions:
      - "agent:invoke"
      - "agent:read"
      - "api:test"
      - "conversation:create"
      - "conversation:read"
      - "conversation:delete:own"
  
  user:
    description: "Basic API consumer"
    permissions:
      - "agent:invoke"
      - "conversation:create"
      - "conversation:read:own"
  
  viewer:
    description: "Read-only access"
    permissions:
      - "agent:read"
      - "conversation:read:own"
      - "metrics:read"
```

### Resource-Based Policies

```python
# Example OPA policy for agent access
package kosmos.authz

default allow = false

# Allow if user has explicit permission
allow {
    user_has_permission[input.action]
}

# Allow if user is tenant admin of the resource's tenant
allow {
    input.user.roles[_] == "tenant-admin"
    input.user.tenant_id == input.resource.tenant_id
}

# Permission lookup
user_has_permission[permission] {
    role := input.user.roles[_]
    permission := data.roles[role].permissions[_]
    glob.match(permission, [], input.action)
}

# Agent invocation requires specific permission
allow {
    input.action == "agent:invoke"
    input.user.permissions[_] == "agent:invoke"
    agent_access_allowed
}

agent_access_allowed {
    # User's tenant matches agent's tenant
    input.user.tenant_id == input.resource.tenant_id
}

agent_access_allowed {
    # Agent is public
    input.resource.visibility == "public"
}
```

---

## Multi-Tenancy

### Tenant Isolation

```
┌──────────────────────────────────────────────────────────────┐
│                     Multi-Tenant Architecture                 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                  Shared Infrastructure               │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │    │
│  │  │ API Gateway │  │ Auth Service│  │ Observability│ │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘ │    │
│  └─────────────────────────────────────────────────────┘    │
│                            │                                 │
│         ┌──────────────────┼──────────────────┐             │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐        │
│  │  Tenant A  │    │  Tenant B  │    │  Tenant C  │        │
│  │            │    │            │    │            │        │
│  │ ┌────────┐ │    │ ┌────────┐ │    │ ┌────────┐ │        │
│  │ │ Schema │ │    │ │ Schema │ │    │ │ Schema │ │        │
│  │ │tenant_a│ │    │ │tenant_b│ │    │ │tenant_c│ │        │
│  │ └────────┘ │    │ └────────┘ │    │ └────────┘ │        │
│  │            │    │            │    │            │        │
│  │ ┌────────┐ │    │ ┌────────┐ │    │ ┌────────┐ │        │
│  │ │ Vector │ │    │ │ Vector │ │    │ │ Vector │ │        │
│  │ │Namespace│ │    │ │Namespace│ │    │ │Namespace│ │        │
│  │ └────────┘ │    │ └────────┘ │    │ └────────┘ │        │
│  └────────────┘    └────────────┘    └────────────┘        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Tenant Context Propagation

```python
# Middleware for tenant context
class TenantContextMiddleware:
    async def __call__(self, request: Request, call_next):
        # Extract tenant from JWT
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        claims = verify_jwt(token)
        tenant_id = claims.get("tenant_id")
        
        if not tenant_id:
            raise HTTPException(401, "Missing tenant context")
        
        # Set tenant context for request
        request.state.tenant_id = tenant_id
        request.state.tenant = await get_tenant(tenant_id)
        
        # Set PostgreSQL search path
        async with get_db_connection() as conn:
            await conn.execute(f"SET search_path TO tenant_{tenant_id}, public")
        
        response = await call_next(request)
        return response
```

### Row-Level Security

```sql
-- PostgreSQL Row-Level Security for multi-tenancy

-- Enable RLS on conversations table
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their tenant's data
CREATE POLICY tenant_isolation ON conversations
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

-- Policy: Users can only insert into their tenant
CREATE POLICY tenant_insert ON conversations
    FOR INSERT
    WITH CHECK (tenant_id = current_setting('app.current_tenant')::uuid);

-- Function to set tenant context
CREATE OR REPLACE FUNCTION set_tenant_context(p_tenant_id uuid)
RETURNS void AS $$
BEGIN
    PERFORM set_config('app.current_tenant', p_tenant_id::text, true);
END;
$$ LANGUAGE plpgsql;
```

---

## Service Account Management

### Service Account Types

| Account Type | Purpose | Authentication | Rotation |
|--------------|---------|----------------|----------|
| **Agent Service** | Inter-agent communication | mTLS | Annual |
| **External API** | Third-party integrations | API Key | 90 days |
| **System Service** | Infrastructure components | Kubernetes SA | Automatic |
| **CI/CD Pipeline** | Deployment automation | OIDC | Per-job |

### Kubernetes Service Accounts

```yaml
# Service account for agents
apiVersion: v1
kind: ServiceAccount
metadata:
  name: kosmos-agent-sa
  namespace: kosmos-core
  annotations:
    # Workload identity for cloud provider access
    iam.gke.io/gcp-service-account: kosmos-agent@project.iam.gserviceaccount.com
---
# Role binding for agent permissions
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: kosmos-agent-binding
  namespace: kosmos-core
subjects:
- kind: ServiceAccount
  name: kosmos-agent-sa
  namespace: kosmos-core
roleRef:
  kind: Role
  name: kosmos-agent-role
  apiGroup: rbac.authorization.k8s.io
```

### API Key Management

```python
# API Key generation and validation
import secrets
import hashlib
from datetime import datetime, timedelta

class APIKeyManager:
    def create_api_key(
        self,
        tenant_id: str,
        name: str,
        permissions: list[str],
        expires_days: int = 90
    ) -> tuple[str, str]:
        """Create new API key. Returns (key_id, secret)."""
        
        key_id = f"kosmos_{secrets.token_hex(8)}"
        secret = secrets.token_urlsafe(32)
        secret_hash = hashlib.sha256(secret.encode()).hexdigest()
        
        # Store in database
        self.db.execute("""
            INSERT INTO api_keys 
            (key_id, secret_hash, tenant_id, name, permissions, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            key_id,
            secret_hash,
            tenant_id,
            name,
            permissions,
            datetime.utcnow() + timedelta(days=expires_days)
        ))
        
        # Return full key only once
        return key_id, f"{key_id}.{secret}"
    
    def validate_api_key(self, api_key: str) -> dict | None:
        """Validate API key and return claims."""
        
        if "." not in api_key:
            return None
        
        key_id, secret = api_key.split(".", 1)
        secret_hash = hashlib.sha256(secret.encode()).hexdigest()
        
        result = self.db.execute("""
            SELECT tenant_id, permissions, expires_at
            FROM api_keys
            WHERE key_id = %s 
              AND secret_hash = %s
              AND expires_at > NOW()
              AND revoked = false
        """, (key_id, secret_hash))
        
        if not result:
            return None
        
        return {
            "key_id": key_id,
            "tenant_id": result["tenant_id"],
            "permissions": result["permissions"]
        }
```

---

## Token Lifecycle

### Token Refresh Flow

```
┌─────────┐                                    ┌─────────────┐
│  Client │                                    │   Zitadel   │
└────┬────┘                                    └──────┬──────┘
     │                                                │
     │  1. Request with expired access token          │
     │ ──────────────────────────────────────────────▶│
     │                                                │
     │  2. 401 Unauthorized                           │
     │ ◀──────────────────────────────────────────────│
     │                                                │
     │  3. POST /token (refresh_token grant)          │
     │ ──────────────────────────────────────────────▶│
     │                                                │
     │  4. New access_token + refresh_token           │
     │ ◀──────────────────────────────────────────────│
     │                                                │
     │  5. Retry original request                     │
     │ ──────────────────────────────────────────────▶│
     │                                                │
```

### Token Configuration

| Token Type | Lifetime | Refresh | Storage |
|------------|----------|---------|---------|
| Access Token | 15 minutes | No | Memory only |
| Refresh Token | 24 hours | Yes (rotating) | Secure cookie |
| ID Token | 15 minutes | No | Memory only |
| API Key | 90 days | Manual rotation | Server-side |

---

## Audit Logging

### Authentication Events

```json
{
  "timestamp": "2025-12-13T10:30:00Z",
  "event_type": "authentication",
  "event_name": "user_login",
  "user_id": "user-uuid",
  "tenant_id": "tenant-uuid",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "auth_method": "oauth2",
  "success": true,
  "session_id": "session-uuid",
  "metadata": {
    "idp": "zitadel",
    "mfa_used": true
  }
}
```

### Authorization Events

```json
{
  "timestamp": "2025-12-13T10:30:05Z",
  "event_type": "authorization",
  "event_name": "permission_check",
  "user_id": "user-uuid",
  "tenant_id": "tenant-uuid",
  "resource": "agent:zeus",
  "action": "invoke",
  "decision": "allow",
  "policy": "tenant_agent_access",
  "metadata": {
    "request_id": "req-uuid",
    "roles": ["operator"]
  }
}
```

---

## Emergency Access

### Break Glass Procedure

```bash
# Emergency admin access - requires approval from 2 authorized personnel

# 1. Generate emergency token (requires HSM access)
./scripts/generate-emergency-token.sh \
  --reason "Production incident INC-2025-001" \
  --approver1 "cto@nuvanta-holding.com" \
  --approver2 "security@nuvanta-holding.com" \
  --duration 2h

# 2. Token is logged and audited
# 3. All actions during emergency session are recorded
# 4. Token auto-expires after duration

# 5. Post-incident: Review emergency access log
./scripts/audit-emergency-access.sh --incident INC-2025-001
```

---

## Related Documentation

- [Security Architecture](architecture.md)
- [Secrets Management](secrets-management.md)
- [Threat Model](threat-model.md)
- [ADR-004: Authentication Strategy](../02-architecture/adr/ADR-004-authentication-strategy.md)

---

**Document Owner:** security@nuvanta-holding.com  
**Emergency Contact:** security-emergency@nuvanta-holding.com
