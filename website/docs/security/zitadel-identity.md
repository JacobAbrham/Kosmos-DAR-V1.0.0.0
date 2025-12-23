# Zitadel Identity

**Enterprise Identity Management for KOSMOS**

:::info Identity Foundation
    Zitadel provides the identity layer for KOSMOS, handling authentication, authorization, and user management with OIDC/SAML support.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   ZITADEL ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    ZITADEL                           │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌────────┐ │   │
│  │  │  OIDC   │  │  SAML   │  │  Users  │  │  Orgs  │ │   │
│  │  │Provider │  │Provider │  │ Mgmt    │  │ Mgmt   │ │   │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬───┘ │   │
│  │       │            │            │            │      │   │
│  │       └────────────┼────────────┼────────────┘      │   │
│  │                    │            │                   │   │
│  │              ┌─────▼────────────▼─────┐            │   │
│  │              │     CockroachDB        │            │   │
│  │              │     (User Store)       │            │   │
│  │              └────────────────────────┘            │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                               │
│            ┌───────────────┼───────────────┐              │
│            ▼               ▼               ▼              │
│      ┌─────────┐     ┌─────────┐     ┌─────────┐        │
│      │  Kong   │     │ Agents  │     │ SigNoz  │        │
│      │ Gateway │     │  APIs   │     │   UI    │        │
│      └─────────┘     └─────────┘     └─────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation

### Helm Installation

```bash
# Add Zitadel Helm repo
helm repo add zitadel https://charts.zitadel.com
helm repo update

# Install with PostgreSQL (using existing KOSMOS PostgreSQL)
helm install zitadel zitadel/zitadel \
  --namespace kosmos-system \
  --values zitadel-values.yaml
```

### `zitadel-values.yaml`

```yaml
replicaCount: 1

zitadel:
  masterkeySecretName: zitadel-masterkey
  configmapConfig:
    ExternalDomain: auth.kosmos.nuvanta.local
    ExternalPort: 443
    ExternalSecure: true
    TLS:
      Enabled: false  # Terminated at ingress
    
    Database:
      postgres:
        Host: postgres.kosmos-data
        Port: 5432
        Database: zitadel
        User:
          Username: zitadel
          SSL:
            Mode: disable

resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi

ingress:
  enabled: true
  className: kong
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: auth.kosmos.nuvanta.local
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: zitadel-tls
      hosts:
        - auth.kosmos.nuvanta.local
```

---

## Configuration

### Organizations

```yaml
# KOSMOS organization structure
organizations:
  - name: Nuvanta Holding
    domain: nuvanta.local
    projects:
      - name: KOSMOS
        roles:
          - ADMIN
          - OPERATOR
          - USER
          - AGENT
```

### OIDC Application Setup

```bash
# Create KOSMOS application via CLI
zitadel apps create oidc \
  --name "KOSMOS Platform" \
  --redirect-uris "https://kosmos.nuvanta.local/callback" \
  --logout-uris "https://kosmos.nuvanta.local/logout" \
  --response-types "CODE" \
  --grant-types "AUTHORIZATION_CODE" "REFRESH_TOKEN" \
  --auth-method "CLIENT_SECRET_BASIC" \
  --output json
```

### Service Account for Agents

```yaml
# Machine user for agent authentication
apiVersion: v1
kind: Secret
metadata:
  name: zeus-service-account
  namespace: kosmos-agents
stringData:
  client_id: "zeus-agent@kosmos.nuvanta.local"
  client_secret: "${ZEUS_CLIENT_SECRET}"
```

---

## Agent Authentication

### Token Acquisition

```python
# agents/common/auth.py
import httpx
from datetime import datetime, timedelta

class ZitadelAuth:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = "https://auth.kosmos.nuvanta.local/oauth/v2/token"
        self._token = None
        self._expires_at = None
    
    async def get_token(self) -> str:
        if self._token and self._expires_at > datetime.utcnow():
            return self._token
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "grant_type": "client_credentials",
                    "scope": "openid profile urn:zitadel:iam:org:project:id:kosmos:aud"
                },
                auth=(self.client_id, self.client_secret)
            )
            response.raise_for_status()
            data = response.json()
            
            self._token = data["access_token"]
            self._expires_at = datetime.utcnow() + timedelta(seconds=data["expires_in"] - 60)
            
            return self._token

# Usage
auth = ZitadelAuth(
    client_id=os.getenv("ZITADEL_CLIENT_ID"),
    client_secret=os.getenv("ZITADEL_CLIENT_SECRET")
)

headers = {"Authorization": f"Bearer {await auth.get_token()}"}
```

### Token Validation

```python
# agents/common/auth_middleware.py
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWKClient

security = HTTPBearer()

class TokenValidator:
    def __init__(self):
        self.jwks_url = "https://auth.kosmos.nuvanta.local/.well-known/jwks.json"
        self.jwks_client = PyJWKClient(self.jwks_url)
        self.issuer = "https://auth.kosmos.nuvanta.local"
        self.audience = "kosmos"
    
    def validate(self, token: str) -> dict:
        signing_key = self.jwks_client.get_signing_key_from_jwt(token)
        
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=self.issuer,
            audience=self.audience
        )
        
        return payload

validator = TokenValidator()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    try:
        payload = validator.validate(credentials.credentials)
        return payload
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=str(e))
```

---

## Role-Based Access Control

### Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| `ADMIN` | Full system access | All operations |
| `OPERATOR` | Operations team | Monitor, restart, configure |
| `USER` | End user | Use agents, view own data |
| `AGENT` | Machine account | Inter-agent communication |

### Role Claims in JWT

```json
{
  "sub": "user-12345",
  "iss": "https://auth.kosmos.nuvanta.local",
  "aud": "kosmos",
  "urn:zitadel:iam:org:project:roles": {
    "OPERATOR": {
      "nuvanta.local": "nuvanta.local"
    }
  },
  "exp": 1702560000
}
```

### Role Enforcement

```python
# agents/common/rbac.py
from functools import wraps
from fastapi import HTTPException

def require_role(*required_roles):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user: dict = Depends(get_current_user), **kwargs):
            user_roles = user.get("urn:zitadel:iam:org:project:roles", {})
            
            if not any(role in user_roles for role in required_roles):
                raise HTTPException(
                    status_code=403,
                    detail=f"Required roles: {required_roles}"
                )
            
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator

# Usage
@app.post("/admin/config")
@require_role("ADMIN")
async def update_config(config: Config, user: dict = Depends(get_current_user)):
    ...
```

---

## Multi-Factor Authentication

### MFA Policy

```yaml
# Configure MFA for ADMIN role
mfa_policy:
  required_for_roles:
    - ADMIN
    - OPERATOR
  allowed_methods:
    - TOTP
    - U2F
  grace_period_days: 7
```

### TOTP Setup Flow

1. User logs in with password
2. System checks if MFA required (based on role)
3. User redirected to TOTP setup if not configured
4. QR code displayed for authenticator app
5. User enters verification code
6. MFA enabled for account

---

## API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/.well-known/openid-configuration` | OIDC discovery |
| `/.well-known/jwks.json` | Public keys for token verification |
| `/oauth/v2/authorize` | Authorization endpoint |
| `/oauth/v2/token` | Token endpoint |
| `/oauth/v2/userinfo` | User info endpoint |
| `/oauth/v2/introspect` | Token introspection |

---

## Integration with KOSMOS Services

### Kong Gateway

```yaml
# Kong OIDC plugin
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: oidc-auth
spec:
  plugin: oidc
  config:
    issuer: "https://auth.kosmos.nuvanta.local/"
    client_id: "${KONG_OIDC_CLIENT_ID}"
    client_secret: "${KONG_OIDC_CLIENT_SECRET}"
    redirect_uri: "https://kosmos.nuvanta.local/callback"
    scope: "openid profile email"
```

### SigNoz SSO

```yaml
# SigNoz OIDC configuration
signoz:
  auth:
    oidc:
      enabled: true
      issuer: "https://auth.kosmos.nuvanta.local"
      clientId: "${SIGNOZ_OIDC_CLIENT_ID}"
      clientSecret: "${SIGNOZ_OIDC_CLIENT_SECRET}"
      redirectUri: "https://signoz.kosmos.nuvanta.local/callback"
```

---

## Troubleshooting

```bash
# Check Zitadel health
curl https://auth.kosmos.nuvanta.local/healthz

# View Zitadel logs
kubectl logs -n kosmos-system -l app.kubernetes.io/name=zitadel -f

# Test token endpoint
curl -X POST https://auth.kosmos.nuvanta.local/oauth/v2/token \
  -d "grant_type=client_credentials" \
  -d "client_id=${CLIENT_ID}" \
  -d "client_secret=${CLIENT_SECRET}"

# Decode JWT
echo $TOKEN | cut -d'.' -f2 | base64 -d | jq
```

---

## See Also

- [Secrets Management](secrets-management)
- [Security Architecture](architecture)
- [ADR-024 Security Architecture](../02-architecture/adr/ADR-024-security-architecture)

---

**Last Updated:** December 2025
