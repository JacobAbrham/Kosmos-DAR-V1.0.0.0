# Unified Data Fabric (Layer 2)

!!! abstract "The Memory & Knowledge Base"
    Layer 2 acts as the "memory" and "knowledge base" for all KOSMOS agents, eliminating data silos through a consolidated PostgreSQL-centric architecture.

## Overview

The Unified Data Fabric consolidates what would traditionally be 5+ separate databases into a single PostgreSQL instance enhanced with specialized extensions.

```
┌─────────────────────────────────────────────────────────────────┐
│                    PostgreSQL (Swiss Army Knife)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Relational  │  │   pgvector   │  │     AGE      │          │
│  │    Tables    │  │   Vectors    │  │    Graph     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │   pg_trgm    │  │   tsvector   │   ← Full-Text Search       │
│  │   (Fuzzy)    │  │    (FTS)     │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
       ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
       │  PgBouncer  │ │  Dragonfly  │ │    MinIO    │
       │  (Pooling)  │ │ (Hot Cache) │ │  (Objects)  │
       └─────────────┘ └─────────────┘ └─────────────┘
```

## Database Consolidation

### What We Replaced

| Traditional Component | Replaced By | Savings |
|----------------------|-------------|---------|
| PostgreSQL (relational) | PostgreSQL 16 | Base |
| Qdrant/Pinecone (vectors) | pgvector | ~2 GB RAM |
| Neo4j (graph) | Apache AGE | ~4 GB RAM |
| Meilisearch (search) | pg_trgm + tsvector | ~1 GB RAM |
| Redis (cache) | Dragonfly | Compatible |
| **Total Savings** | | **~7 GB RAM** |

### PostgreSQL Extensions

| Extension | Purpose | Status |
|-----------|---------|--------|
| `pgvector` | Vector similarity search for RAG | ✅ Required |
| `age` | Graph database (Apache AGE) | ✅ Required |
| `pg_trgm` | Trigram fuzzy text matching | ✅ Required |
| `unaccent` | Accent-insensitive search | ✅ Required |
| `btree_gin` | GIN index for multiple types | ✅ Required |
| `uuid-ossp` | UUID generation | ✅ Required |

## Component Specifications

### PostgreSQL 16

**Role:** Primary data store for structured, vector, and graph data

```yaml
# postgresql-config.yaml
version: "16"
resources:
  requests:
    memory: "4Gi"
    cpu: "2000m"
storage:
  class: alicloud-essd-pl1
  size: 100Gi
  iops: 3000

parameters:
  shared_buffers: "1GB"
  effective_cache_size: "3GB"
  work_mem: "64MB"
  max_connections: 200
```

### Dragonfly

**Role:** High-performance Redis-compatible cache

```yaml
# dragonfly-config.yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
storage:
  size: 5Gi

config:
  maxmemory: "900mb"
  maxmemory-policy: "allkeys-lru"
  appendonly: "yes"
```

### MinIO

**Role:** S3-compatible object storage

```yaml
# minio-config.yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
storage:
  size: 200Gi

buckets:
  - name: kosmos-docs
    versioning: true
  - name: kosmos-backups
    lifecycle:
      transition_to_archive: 90d
  - name: kosmos-media
    versioning: true
```

## Schema Design

### Vector Storage (pgvector)

```sql
-- Document embeddings for RAG
CREATE TABLE document_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1536),  -- OpenAI ada-002 dimension
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- IVFFlat index for approximate nearest neighbor
CREATE INDEX idx_embeddings_vector ON document_embeddings 
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
```

### Graph Storage (Apache AGE)

```sql
-- Initialize graph
SELECT create_graph('kosmos_graph');

-- Graph traversal query
SELECT * FROM cypher('kosmos_graph', $$
    MATCH path = (start:Entity)-[:RELATES_TO*1..3]-(end:Entity)
    WHERE start.id = $entity_id
    RETURN path
$$) AS (path agtype);
```

## Backup Strategy

### GCP (Global Consistency Point)

```yaml
# backup-config.yaml
schedule: "0 2 * * *"  # Daily at 2 AM
retention:
  daily: 7
  weekly: 4
  monthly: 12

procedure:
  1. Zeus broadcasts system.pause via NATS
  2. LangGraph drains current operations
  3. Inject snapshot_id into PostgreSQL WAL
  4. Trigger Alibaba Cloud disk snapshot
  5. Velero backup to MinIO
  6. Zeus broadcasts system.resume
```

## Monitoring

### Key Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `pg_connections_active` | Active connections | > 150 |
| `pg_replication_lag` | Replication delay | > 10s |
| `pgbouncer_pool_available` | Available pool slots | < 10 |
| `dragonfly_memory_used` | Cache memory usage | > 85% |
| `minio_bucket_size` | Bucket storage used | > 90% |

---

## See Also

- [Memory Architecture](adr/ADR-018-memory-architecture.md) — Memory design
- [Cloud Inference](cloud-inference.md) — LLM architecture

---

**Last Updated:** December 2025
