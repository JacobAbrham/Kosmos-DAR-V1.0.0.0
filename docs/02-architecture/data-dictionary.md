# Data Dictionary

**Document Type:** Data Governance  
**Owner:** Data Engineering Team  
**Reviewers:** DBA, Security, Compliance  
**Review Cadence:** Quarterly  
**Last Updated:** 2025-12-13  
**Status:** 🟢 Active

---

## Overview

This data dictionary provides comprehensive definitions for all data entities, tables, columns, and relationships within the KOSMOS platform. It serves as the authoritative reference for data structures, types, constraints, and business context.

---

## Database Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      KOSMOS Database Architecture                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    Primary Database (PostgreSQL)                 │   │
│   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐    │   │
│   │   │   kosmos    │  │  kosmos_    │  │    kosmos_audit     │    │   │
│   │   │   (core)    │  │  analytics  │  │    (audit logs)     │    │   │
│   │   └─────────────┘  └─────────────┘  └─────────────────────┘    │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    Vector Storage (pgvector)                     │   │
│   │   ┌─────────────────────────────────────────────────────────┐   │   │
│   │   │  embeddings (conversation, document, knowledge base)    │   │   │
│   │   └─────────────────────────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    Cache (Dragonfly/Redis)                       │   │
│   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐    │   │
│   │   │  Sessions   │  │   Cache     │  │    Rate Limits      │    │   │
│   │   └─────────────┘  └─────────────┘  └─────────────────────┘    │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Schema: kosmos (Core)

### Table: tenants

**Purpose:** Multi-tenant organization management

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR(50)` | NO | - | Primary key, format: `tenant_{uuid8}` |
| `name` | `VARCHAR(255)` | NO | - | Organization display name |
| `slug` | `VARCHAR(100)` | NO | - | URL-friendly identifier, unique |
| `plan` | `VARCHAR(20)` | NO | `'free'` | Subscription plan: free, pro, enterprise |
| `status` | `VARCHAR(20)` | NO | `'active'` | Account status: active, suspended, cancelled |
| `settings` | `JSONB` | YES | `'{}'` | Tenant-specific configuration |
| `limits` | `JSONB` | YES | - | Usage limits per plan |
| `created_at` | `TIMESTAMPTZ` | NO | `NOW()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `NOW()` | Last update timestamp |
| `deleted_at` | `TIMESTAMPTZ` | YES | - | Soft delete timestamp |

**Indexes:**
- `tenants_pkey` - PRIMARY KEY (`id`)
- `tenants_slug_key` - UNIQUE (`slug`)
- `tenants_status_idx` - INDEX (`status`)

**Constraints:**
- `tenants_plan_check` - CHECK (`plan` IN ('free', 'pro', 'enterprise'))
- `tenants_status_check` - CHECK (`status` IN ('active', 'suspended', 'cancelled'))

---

### Table: users

**Purpose:** User accounts and authentication

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR(50)` | NO | - | Primary key, format: `user_{uuid8}` |
| `tenant_id` | `VARCHAR(50)` | NO | - | Foreign key to tenants |
| `email` | `VARCHAR(255)` | NO | - | User email, unique per tenant |
| `email_hash` | `VARCHAR(64)` | YES | - | SHA-256 hash for privacy analytics |
| `name` | `VARCHAR(255)` | YES | - | Full name |
| `avatar_url` | `TEXT` | YES | - | Profile picture URL |
| `roles` | `VARCHAR(20)[]` | NO | `'{user}'` | Array of role names |
| `status` | `VARCHAR(20)` | NO | `'active'` | Account status |
| `preferences` | `JSONB` | YES | `'{}'` | User preferences (theme, language) |
| `last_login_at` | `TIMESTAMPTZ` | YES | - | Last login timestamp |
| `created_at` | `TIMESTAMPTZ` | NO | `NOW()` | Account creation |
| `updated_at` | `TIMESTAMPTZ` | NO | `NOW()` | Last update |
| `deleted_at` | `TIMESTAMPTZ` | YES | - | Soft delete (GDPR erasure) |

**Indexes:**
- `users_pkey` - PRIMARY KEY (`id`)
- `users_tenant_email_key` - UNIQUE (`tenant_id`, `email`)
- `users_email_hash_idx` - INDEX (`email_hash`)
- `users_tenant_status_idx` - INDEX (`tenant_id`, `status`)

**Foreign Keys:**
- `users_tenant_id_fkey` - REFERENCES `tenants(id)` ON DELETE CASCADE

**Constraints:**
- `users_status_check` - CHECK (`status` IN ('active', 'suspended', 'pending', 'deleted'))

**PII Fields:** `email`, `name`, `avatar_url`

---

### Table: conversations

**Purpose:** Chat conversation containers

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR(50)` | NO | - | Primary key, format: `conv_{uuid8}` |
| `user_id` | `VARCHAR(50)` | NO | - | Foreign key to users |
| `tenant_id` | `VARCHAR(50)` | NO | - | Foreign key to tenants (denormalized) |
| `title` | `VARCHAR(255)` | YES | - | Conversation title (auto-generated or user-set) |
| `summary` | `TEXT` | YES | - | AI-generated conversation summary |
| `status` | `VARCHAR(20)` | NO | `'active'` | Conversation status |
| `metadata` | `JSONB` | YES | `'{}'` | Additional metadata |
| `message_count` | `INTEGER` | NO | `0` | Cached message count |
| `token_count` | `INTEGER` | NO | `0` | Total tokens used |
| `last_message_at` | `TIMESTAMPTZ` | YES | - | Last message timestamp |
| `created_at` | `TIMESTAMPTZ` | NO | `NOW()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `NOW()` | Last update |
| `archived_at` | `TIMESTAMPTZ` | YES | - | Archive timestamp |

**Indexes:**
- `conversations_pkey` - PRIMARY KEY (`id`)
- `conversations_user_idx` - INDEX (`user_id`)
- `conversations_tenant_user_idx` - INDEX (`tenant_id`, `user_id`)
- `conversations_last_message_idx` - INDEX (`last_message_at` DESC)
- `conversations_status_idx` - INDEX (`status`) WHERE `status` = 'active'

**Foreign Keys:**
- `conversations_user_id_fkey` - REFERENCES `users(id)` ON DELETE CASCADE
- `conversations_tenant_id_fkey` - REFERENCES `tenants(id)` ON DELETE CASCADE

---

### Table: messages

**Purpose:** Individual chat messages

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR(50)` | NO | - | Primary key, format: `msg_{uuid8}` |
| `conversation_id` | `VARCHAR(50)` | NO | - | Foreign key to conversations |
| `role` | `VARCHAR(20)` | NO | - | Message role: user, assistant, system, tool |
| `content` | `TEXT` | NO | - | Message content (may contain PII) |
| `sanitized_content` | `TEXT` | YES | - | PII-redacted content for analytics |
| `content_type` | `VARCHAR(20)` | NO | `'text'` | Content type: text, image, file, tool_call |
| `tokens` | `INTEGER` | YES | - | Token count for this message |
| `model_used` | `VARCHAR(50)` | YES | - | LLM model used (for assistant messages) |
| `tool_calls` | `JSONB` | YES | - | Tool call details (for tool messages) |
| `metadata` | `JSONB` | YES | `'{}'` | Additional metadata |
| `parent_id` | `VARCHAR(50)` | YES | - | Parent message (for threading) |
| `created_at` | `TIMESTAMPTZ` | NO | `NOW()` | Message timestamp |

**Indexes:**
- `messages_pkey` - PRIMARY KEY (`id`)
- `messages_conversation_idx` - INDEX (`conversation_id`)
- `messages_conversation_created_idx` - INDEX (`conversation_id`, `created_at`)
- `messages_role_idx` - INDEX (`role`)
- `messages_parent_idx` - INDEX (`parent_id`) WHERE `parent_id` IS NOT NULL

**Foreign Keys:**
- `messages_conversation_id_fkey` - REFERENCES `conversations(id)` ON DELETE CASCADE
- `messages_parent_id_fkey` - REFERENCES `messages(id)` ON DELETE SET NULL

**PII Fields:** `content`

---

### Table: documents

**Purpose:** Knowledge base documents

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR(50)` | NO | - | Primary key, format: `doc_{uuid8}` |
| `tenant_id` | `VARCHAR(50)` | NO | - | Foreign key to tenants |
| `title` | `VARCHAR(500)` | NO | - | Document title |
| `content` | `TEXT` | YES | - | Full text content |
| `content_hash` | `VARCHAR(64)` | YES | - | SHA-256 hash for deduplication |
| `source` | `VARCHAR(50)` | NO | - | Source: upload, confluence, sharepoint, gdrive, web |
| `source_url` | `TEXT` | YES | - | Original document URL |
| `source_id` | `VARCHAR(255)` | YES | - | External source identifier |
| `mime_type` | `VARCHAR(100)` | YES | - | File MIME type |
| `file_size` | `BIGINT` | YES | - | File size in bytes |
| `chunk_count` | `INTEGER` | NO | `0` | Number of chunks |
| `status` | `VARCHAR(20)` | NO | `'processing'` | Processing status |
| `metadata` | `JSONB` | YES | `'{}'` | Document metadata |
| `indexed_at` | `TIMESTAMPTZ` | YES | - | When document was indexed |
| `created_at` | `TIMESTAMPTZ` | NO | `NOW()` | Upload timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `NOW()` | Last update |
| `deleted_at` | `TIMESTAMPTZ` | YES | - | Soft delete timestamp |

**Indexes:**
- `documents_pkey` - PRIMARY KEY (`id`)
- `documents_tenant_idx` - INDEX (`tenant_id`)
- `documents_content_hash_idx` - INDEX (`content_hash`)
- `documents_source_idx` - INDEX (`tenant_id`, `source`)
- `documents_status_idx` - INDEX (`status`)

**Foreign Keys:**
- `documents_tenant_id_fkey` - REFERENCES `tenants(id)` ON DELETE CASCADE

---

### Table: document_chunks

**Purpose:** Document chunks for RAG retrieval

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR(50)` | NO | - | Primary key, format: `chunk_{uuid8}` |
| `document_id` | `VARCHAR(50)` | NO | - | Foreign key to documents |
| `tenant_id` | `VARCHAR(50)` | NO | - | Foreign key to tenants (denormalized) |
| `chunk_index` | `INTEGER` | NO | - | Chunk sequence number |
| `content` | `TEXT` | NO | - | Chunk text content |
| `token_count` | `INTEGER` | YES | - | Token count |
| `embedding` | `vector(384)` | YES | - | Vector embedding (pgvector) |
| `metadata` | `JSONB` | YES | `'{}'` | Chunk metadata |
| `created_at` | `TIMESTAMPTZ` | NO | `NOW()` | Creation timestamp |

**Indexes:**
- `document_chunks_pkey` - PRIMARY KEY (`id`)
- `document_chunks_document_idx` - INDEX (`document_id`)
- `document_chunks_tenant_idx` - INDEX (`tenant_id`)
- `document_chunks_embedding_idx` - INDEX USING ivfflat (`embedding` vector_cosine_ops) WITH (lists = 100)

**Foreign Keys:**
- `document_chunks_document_id_fkey` - REFERENCES `documents(id)` ON DELETE CASCADE
- `document_chunks_tenant_id_fkey` - REFERENCES `tenants(id)` ON DELETE CASCADE

---

### Table: agent_sessions

**Purpose:** Agent execution sessions

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR(50)` | NO | - | Primary key, format: `sess_{uuid8}` |
| `conversation_id` | `VARCHAR(50)` | NO | - | Foreign key to conversations |
| `user_id` | `VARCHAR(50)` | NO | - | Foreign key to users |
| `tenant_id` | `VARCHAR(50)` | NO | - | Foreign key to tenants |
| `agent_name` | `VARCHAR(50)` | NO | - | Agent identifier: zeus, athena, hermes, etc. |
| `state` | `JSONB` | YES | `'{}'` | LangGraph state snapshot |
| `status` | `VARCHAR(20)` | NO | `'active'` | Session status |
| `input_tokens` | `INTEGER` | NO | `0` | Total input tokens |
| `output_tokens` | `INTEGER` | NO | `0` | Total output tokens |
| `total_cost` | `DECIMAL(10,6)` | NO | `0` | Estimated cost in USD |
| `started_at` | `TIMESTAMPTZ` | NO | `NOW()` | Session start |
| `ended_at` | `TIMESTAMPTZ` | YES | - | Session end |
| `duration_ms` | `INTEGER` | YES | - | Duration in milliseconds |

**Indexes:**
- `agent_sessions_pkey` - PRIMARY KEY (`id`)
- `agent_sessions_conversation_idx` - INDEX (`conversation_id`)
- `agent_sessions_tenant_agent_idx` - INDEX (`tenant_id`, `agent_name`)
- `agent_sessions_started_idx` - INDEX (`started_at` DESC)

**Foreign Keys:**
- `agent_sessions_conversation_id_fkey` - REFERENCES `conversations(id)` ON DELETE CASCADE
- `agent_sessions_user_id_fkey` - REFERENCES `users(id)` ON DELETE CASCADE
- `agent_sessions_tenant_id_fkey` - REFERENCES `tenants(id)` ON DELETE CASCADE

---

### Table: tool_executions

**Purpose:** MCP tool execution tracking

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `VARCHAR(50)` | NO | - | Primary key, format: `exec_{uuid8}` |
| `session_id` | `VARCHAR(50)` | NO | - | Foreign key to agent_sessions |
| `message_id` | `VARCHAR(50)` | YES | - | Foreign key to messages |
| `tool_name` | `VARCHAR(100)` | NO | - | MCP tool name |
| `server_name` | `VARCHAR(100)` | NO | - | MCP server name |
| `input` | `JSONB` | YES | - | Tool input parameters |
| `output` | `JSONB` | YES | - | Tool output result |
| `status` | `VARCHAR(20)` | NO | - | Execution status: success, error, timeout |
| `error_message` | `TEXT` | YES | - | Error details if failed |
| `duration_ms` | `INTEGER` | YES | - | Execution duration |
| `created_at` | `TIMESTAMPTZ` | NO | `NOW()` | Execution timestamp |

**Indexes:**
- `tool_executions_pkey` - PRIMARY KEY (`id`)
- `tool_executions_session_idx` - INDEX (`session_id`)
- `tool_executions_tool_idx` - INDEX (`tool_name`)
- `tool_executions_status_idx` - INDEX (`status`)

**Foreign Keys:**
- `tool_executions_session_id_fkey` - REFERENCES `agent_sessions(id)` ON DELETE CASCADE
- `tool_executions_message_id_fkey` - REFERENCES `messages(id)` ON DELETE SET NULL

---

## Schema: kosmos_analytics

### Table: usage_metrics

**Purpose:** Aggregated usage statistics

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `BIGSERIAL` | NO | - | Primary key |
| `tenant_id` | `VARCHAR(50)` | NO | - | Foreign key to tenants |
| `period_start` | `TIMESTAMPTZ` | NO | - | Aggregation period start |
| `period_end` | `TIMESTAMPTZ` | NO | - | Aggregation period end |
| `period_type` | `VARCHAR(10)` | NO | - | Period type: hourly, daily, monthly |
| `active_users` | `INTEGER` | NO | `0` | Unique active users |
| `conversations` | `INTEGER` | NO | `0` | Total conversations |
| `messages` | `INTEGER` | NO | `0` | Total messages |
| `input_tokens` | `BIGINT` | NO | `0` | Total input tokens |
| `output_tokens` | `BIGINT` | NO | `0` | Total output tokens |
| `estimated_cost` | `DECIMAL(12,4)` | NO | `0` | Estimated cost USD |
| `avg_response_time_ms` | `DECIMAL(10,2)` | YES | - | Average response latency |
| `error_count` | `INTEGER` | NO | `0` | Error count |
| `created_at` | `TIMESTAMPTZ` | NO | `NOW()` | Record creation |

**Indexes:**
- `usage_metrics_pkey` - PRIMARY KEY (`id`)
- `usage_metrics_tenant_period_idx` - UNIQUE (`tenant_id`, `period_type`, `period_start`)
- `usage_metrics_period_idx` - INDEX (`period_start` DESC)

**Partitioning:** Range partitioned by `period_start` (monthly)

---

### Table: model_metrics

**Purpose:** Per-model usage and performance metrics

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `BIGSERIAL` | NO | - | Primary key |
| `tenant_id` | `VARCHAR(50)` | NO | - | Foreign key to tenants |
| `model_name` | `VARCHAR(100)` | NO | - | LLM model identifier |
| `period_start` | `TIMESTAMPTZ` | NO | - | Aggregation period start |
| `period_type` | `VARCHAR(10)` | NO | - | Period type: hourly, daily |
| `request_count` | `INTEGER` | NO | `0` | Total requests |
| `input_tokens` | `BIGINT` | NO | `0` | Input tokens used |
| `output_tokens` | `BIGINT` | NO | `0` | Output tokens generated |
| `estimated_cost` | `DECIMAL(12,6)` | NO | `0` | Estimated cost USD |
| `avg_latency_ms` | `DECIMAL(10,2)` | YES | - | Average latency |
| `p99_latency_ms` | `DECIMAL(10,2)` | YES | - | P99 latency |
| `error_count` | `INTEGER` | NO | `0` | Error count |
| `cache_hits` | `INTEGER` | NO | `0` | Semantic cache hits |
| `created_at` | `TIMESTAMPTZ` | NO | `NOW()` | Record creation |

**Indexes:**
- `model_metrics_pkey` - PRIMARY KEY (`id`)
- `model_metrics_tenant_model_period_idx` - UNIQUE (`tenant_id`, `model_name`, `period_type`, `period_start`)

---

## Schema: kosmos_audit

### Table: audit_logs

**Purpose:** Compliance audit trail

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `BIGSERIAL` | NO | - | Primary key |
| `tenant_id` | `VARCHAR(50)` | NO | - | Foreign key to tenants |
| `user_id` | `VARCHAR(50)` | YES | - | Acting user (null for system) |
| `action` | `VARCHAR(100)` | NO | - | Action performed |
| `resource_type` | `VARCHAR(50)` | NO | - | Resource type affected |
| `resource_id` | `VARCHAR(50)` | YES | - | Resource identifier |
| `old_value` | `JSONB` | YES | - | Previous state (redacted) |
| `new_value` | `JSONB` | YES | - | New state (redacted) |
| `ip_address` | `INET` | YES | - | Client IP address |
| `user_agent` | `TEXT` | YES | - | Client user agent |
| `trace_id` | `VARCHAR(50)` | YES | - | Distributed trace ID |
| `created_at` | `TIMESTAMPTZ` | NO | `NOW()` | Event timestamp |

**Indexes:**
- `audit_logs_pkey` - PRIMARY KEY (`id`)
- `audit_logs_tenant_idx` - INDEX (`tenant_id`)
- `audit_logs_user_idx` - INDEX (`user_id`)
- `audit_logs_action_idx` - INDEX (`action`)
- `audit_logs_resource_idx` - INDEX (`resource_type`, `resource_id`)
- `audit_logs_created_idx` - INDEX (`created_at` DESC)

**Partitioning:** Range partitioned by `created_at` (monthly)

**Retention:** 3 years (compliance requirement)

---

### Table: data_access_logs

**Purpose:** GDPR Article 30 data access tracking

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `BIGSERIAL` | NO | - | Primary key |
| `tenant_id` | `VARCHAR(50)` | NO | - | Foreign key to tenants |
| `user_id` | `VARCHAR(50)` | YES | - | User accessing data |
| `data_subject_id` | `VARCHAR(50)` | YES | - | Data subject (whose data) |
| `data_category` | `VARCHAR(50)` | NO | - | Category: pii, conversation, document |
| `access_type` | `VARCHAR(20)` | NO | - | Access type: read, write, delete, export |
| `purpose` | `VARCHAR(100)` | NO | - | Purpose of access |
| `legal_basis` | `VARCHAR(50)` | NO | - | GDPR legal basis |
| `ip_address` | `INET` | YES | - | Client IP |
| `created_at` | `TIMESTAMPTZ` | NO | `NOW()` | Access timestamp |

**Indexes:**
- `data_access_logs_pkey` - PRIMARY KEY (`id`)
- `data_access_logs_subject_idx` - INDEX (`data_subject_id`)
- `data_access_logs_category_idx` - INDEX (`data_category`)
- `data_access_logs_created_idx` - INDEX (`created_at` DESC)

**Retention:** 3 years (GDPR Article 30)

---

## Cache Keys (Dragonfly)

### Session Cache

| Key Pattern | Type | TTL | Description |
|-------------|------|-----|-------------|
| `session:{session_id}` | Hash | 24h | User session data |
| `session:{session_id}:tokens` | String | 24h | Session token count |

### Rate Limiting

| Key Pattern | Type | TTL | Description |
|-------------|------|-----|-------------|
| `ratelimit:{tenant_id}:{window}` | String | 60s | Tenant rate limit counter |
| `ratelimit:{user_id}:{window}` | String | 60s | User rate limit counter |
| `ratelimit:llm:{provider}:{window}` | String | 60s | LLM provider rate limit |

### Semantic Cache

| Key Pattern | Type | TTL | Description |
|-------------|------|-----|-------------|
| `llm:cache:{hash}` | String | 1h | Cached LLM response |
| `embedding:cache:{hash}` | String | 24h | Cached embedding |

### Context Cache

| Key Pattern | Type | TTL | Description |
|-------------|------|-----|-------------|
| `context:{conversation_id}` | List | 1h | Recent context window |
| `rag:{query_hash}` | String | 1h | RAG retrieval cache |

---

## Data Types Reference

### Custom ENUM Types

```sql
-- User roles
CREATE TYPE user_role AS ENUM ('admin', 'user', 'viewer', 'api_client');

-- Conversation status
CREATE TYPE conversation_status AS ENUM ('active', 'archived', 'deleted');

-- Message role
CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system', 'tool');

-- Document source
CREATE TYPE document_source AS ENUM ('upload', 'confluence', 'sharepoint', 'gdrive', 'web', 'api');

-- Agent names
CREATE TYPE agent_name AS ENUM (
    'zeus', 'athena', 'hermes', 'chronos', 'hephaestus',
    'apollo', 'prometheus', 'dionysus', 'ares', 'demeter', 'iris'
);
```

### JSON Schema: User Preferences

```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "theme": {
            "type": "string",
            "enum": ["light", "dark", "system"]
        },
        "language": {
            "type": "string",
            "pattern": "^[a-z]{2}(-[A-Z]{2})?$"
        },
        "notifications": {
            "type": "object",
            "properties": {
                "email": { "type": "boolean" },
                "push": { "type": "boolean" }
            }
        },
        "default_model": {
            "type": "string"
        }
    }
}
```

### JSON Schema: Tenant Settings

```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "allowed_models": {
            "type": "array",
            "items": { "type": "string" }
        },
        "default_model": {
            "type": "string"
        },
        "max_tokens_per_request": {
            "type": "integer",
            "minimum": 100,
            "maximum": 32000
        },
        "enabled_agents": {
            "type": "array",
            "items": { "type": "string" }
        },
        "custom_branding": {
            "type": "object",
            "properties": {
                "logo_url": { "type": "string", "format": "uri" },
                "primary_color": { "type": "string", "pattern": "^#[0-9a-fA-F]{6}$" }
            }
        }
    }
}
```

---

## Data Retention Policies

| Data Category | Table | Retention | Legal Basis |
|---------------|-------|-----------|-------------|
| User accounts | `users` | Active + 90 days after deletion request | GDPR Article 17 |
| Conversations | `conversations` | 90 days after last activity | Business policy |
| Messages | `messages` | 90 days (follows conversation) | Business policy |
| Documents | `documents` | Until deletion or tenant cancellation | User consent |
| Audit logs | `audit_logs` | 3 years | SOC 2, ISO 27001 |
| Data access logs | `data_access_logs` | 3 years | GDPR Article 30 |
| Usage metrics | `usage_metrics` | 2 years | Business analytics |
| Session cache | Dragonfly | 24 hours | Performance |

---

## Related Documentation

- [Data Lineage](data-lineage.md)
- [Database Operations](../04-operations/infrastructure/database-ops.md)
- [Security Architecture](../security/architecture.md)

---

**Document Owner:** data-engineering@nuvanta-holding.com  
**Schema Questions:** dba@nuvanta-holding.com
