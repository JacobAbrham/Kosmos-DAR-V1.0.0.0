# ADR-012: Multi-Tenancy Strategy

**Status:** Accepted  
**Date:** 2025-12-13  
**Decision Makers:** Architecture Team, Security Team  

---

## Context

KOSMOS serves multiple enterprise customers who require strict data isolation, independent configuration, and separate billing. We need a multi-tenancy architecture that balances operational efficiency with security requirements.

### Requirements

1. **Data Isolation:** Complete separation of tenant data
2. **Performance Isolation:** Fair resource allocation, no noisy neighbor effects
3. **Configuration Isolation:** Tenant-specific settings without affecting others
4. **Cost Attribution:** Accurate per-tenant cost tracking
5. **Scalability:** Support 1000+ tenants without architectural changes

### Options Considered

#### Option A: Database-per-Tenant

Each tenant gets a dedicated database instance.

**Pros:**
- Complete physical isolation
- Easy backup/restore per tenant
- Simple compliance for data residency

**Cons:**
- High operational overhead (1000+ databases)
- Expensive infrastructure costs
- Complex schema migrations
- Slow tenant onboarding

#### Option B: Schema-per-Tenant

Shared database with tenant-specific schemas.

**Pros:**
- Good isolation within single database
- Moderate operational overhead
- Easier migrations than Option A

**Cons:**
- Connection pooling complexity
- Still scales linearly with tenants
- Cross-tenant queries difficult

#### Option C: Shared Schema with Tenant ID (Selected)

Single schema with `tenant_id` column on all tenant-scoped tables.

**Pros:**
- Lowest operational overhead
- Efficient resource utilization
- Simple tenant onboarding (insert row)
- Easy cross-tenant analytics (with proper authorization)
- Connection pooling works naturally

**Cons:**
- Requires rigorous tenant filtering in all queries
- Risk of data leakage if filtering missed
- Index design must include tenant_id

---

## Decision

We adopt **Option C: Shared Schema with Tenant ID** with the following safeguards:

### 1. Row-Level Security (RLS)

```sql
-- Enable RLS on all tenant-scoped tables
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

-- Create tenant isolation policy
CREATE POLICY tenant_isolation ON conversations
    USING (tenant_id = current_setting('app.current_tenant')::text);

-- Set tenant context at connection start
SET app.current_tenant = 'tenant_abc123';
```

### 2. Application-Level Enforcement

```python
class TenantMiddleware:
    async def __call__(self, request, call_next):
        tenant_id = extract_tenant_from_token(request)
        
        # Set tenant context for database RLS
        async with get_db() as db:
            await db.execute(
                "SET app.current_tenant = :tenant_id",
                {"tenant_id": tenant_id}
            )
        
        # Add to request state for application code
        request.state.tenant_id = tenant_id
        return await call_next(request)
```

### 3. Query Builder Pattern

```python
class TenantScopedRepository:
    def __init__(self, tenant_id: str, session: AsyncSession):
        self.tenant_id = tenant_id
        self.session = session
    
    async def get_conversations(self, user_id: str) -> list[Conversation]:
        # tenant_id automatically included
        query = select(Conversation).where(
            Conversation.tenant_id == self.tenant_id,
            Conversation.user_id == user_id
        )
        return await self.session.scalars(query)
```

### 4. Tenant-Aware Caching

```python
def cache_key(tenant_id: str, resource: str, id: str) -> str:
    """Generate tenant-scoped cache key"""
    return f"tenant:{tenant_id}:{resource}:{id}"

# Example usage
await cache.set(
    cache_key(tenant_id, "conversation", conv_id),
    conversation_data,
    ttl=3600
)
```

---

## Consequences

### Positive

- Single database simplifies operations
- Efficient resource utilization
- Fast tenant provisioning (&lt;1 second)
- Natural connection pooling
- Easy cross-tenant analytics with proper controls

### Negative

- Requires discipline in all database access
- Must test tenant isolation thoroughly
- Complex index design (all indexes include tenant_id)
- Single point of failure for database

### Mitigations

1. **Automated testing** for tenant isolation in CI/CD
2. **Code review checklist** for tenant_id inclusion
3. **Database audit logging** for cross-tenant access attempts
4. **Index design standard** requiring tenant_id prefix

---

## Compliance

| Requirement | Implementation |
|-------------|----------------|
| SOC 2 CC6.1 | Logical access controls via RLS |
| GDPR Article 32 | Data isolation via tenant filtering |
| ISO 27001 A.9 | Access control policies enforced |

---

## Related

- [IAM Documentation](../../security/iam)
- [Database Operations](../../04-operations/infrastructure/database-ops)
- [ADR-004: Authentication Strategy](ADR-004-authentication-strategy)
