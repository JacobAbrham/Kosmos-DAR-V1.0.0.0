# Database Operations Runbook

**Document Type:** Operational Procedures  
**Owner:** Database Engineering / SRE  
**Reviewers:** Platform Engineering, Security Lead  
**Review Cadence:** Quarterly  
**Last Updated:** 2025-12-13  
**Status:** 🟢 Active

---

## Overview

This runbook covers operational procedures for KOSMOS database systems, including PostgreSQL (primary data store), Dragonfly (cache), and pgvector (embeddings). It provides step-by-step procedures for common operations, troubleshooting, and emergency responses.

---

## Database Inventory

| Database | Purpose | Version | Port | Namespace |
|----------|---------|---------|------|-----------|
| PostgreSQL | Primary data store | 16 | 5432 | kosmos-db |
| pgvector | Vector embeddings | 0.7.0 (extension) | 5432 | kosmos-db |
| Dragonfly | Cache (Redis-compatible) | 1.15 | 6379 | kosmos-db |
| NATS JetStream | Message persistence | 2.10 | 4222 | kosmos-db |

---

## PostgreSQL Operations

### Connection Information

```bash
# Production connection (from within cluster)
PGHOST=postgres-primary.kosmos-db.svc.cluster.local
PGPORT=5432
PGDATABASE=kosmos
PGUSER=kosmos

# Connect via kubectl
kubectl exec -it postgres-0 -n kosmos-db -- psql -U kosmos -d kosmos

# Port forward for local access (debugging only)
kubectl port-forward svc/postgres-primary 5432:5432 -n kosmos-db
```

### Health Checks

```bash
# Check PostgreSQL is accepting connections
kubectl exec postgres-0 -n kosmos-db -- pg_isready -U kosmos
# Expected: localhost:5432 - accepting connections

# Check replication status (if replicas configured)
kubectl exec postgres-0 -n kosmos-db -- psql -U kosmos -c "
SELECT 
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    sync_state
FROM pg_stat_replication;
"

# Check database size
kubectl exec postgres-0 -n kosmos-db -- psql -U kosmos -c "
SELECT 
    datname,
    pg_size_pretty(pg_database_size(datname)) as size
FROM pg_database 
ORDER BY pg_database_size(datname) DESC;
"

# Check active connections
kubectl exec postgres-0 -n kosmos-db -- psql -U kosmos -c "
SELECT 
    datname,
    usename,
    application_name,
    client_addr,
    state,
    query_start,
    state_change
FROM pg_stat_activity
WHERE datname = 'kosmos';
"
```

### Common Operations

#### Create Database Backup

```bash
#!/bin/bash
# backup-postgres.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="kosmos_backup_${TIMESTAMP}.dump"

echo "Creating backup: ${BACKUP_FILE}"

kubectl exec postgres-0 -n kosmos-db -- \
    pg_dump -Fc -U kosmos -d kosmos > "/tmp/${BACKUP_FILE}"

# Upload to object storage
aliyun oss cp "/tmp/${BACKUP_FILE}" \
    "oss://kosmos-backups/postgres/${BACKUP_FILE}"

# Verify backup
pg_restore --list "/tmp/${BACKUP_FILE}" | head -20

echo "Backup completed: ${BACKUP_FILE}"
```

#### Restore Database

```bash
#!/bin/bash
# restore-postgres.sh

BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup-file>"
    echo "Available backups:"
    aliyun oss ls oss://kosmos-backups/postgres/ | tail -10
    exit 1
fi

echo "WARNING: This will overwrite the current database!"
read -p "Type 'RESTORE' to confirm: " CONFIRM
if [ "$CONFIRM" != "RESTORE" ]; then
    echo "Cancelled"
    exit 1
fi

# Download backup
aliyun oss cp "oss://kosmos-backups/postgres/${BACKUP_FILE}" /tmp/

# Scale down applications
echo "Scaling down applications..."
kubectl scale deployment --all -n kosmos-core --replicas=0

# Wait for connections to close
sleep 10

# Restore
echo "Restoring database..."
kubectl exec -i postgres-0 -n kosmos-db -- \
    pg_restore -U kosmos -d kosmos -c < "/tmp/${BACKUP_FILE}"

# Scale up applications
echo "Scaling up applications..."
kubectl scale deployment zeus-orchestrator -n kosmos-core --replicas=3

echo "Restore completed"
```

#### Run Migrations

```bash
#!/bin/bash
# run-migrations.sh

# Check current migration status
kubectl exec -it postgres-0 -n kosmos-db -- psql -U kosmos -c "
SELECT * FROM schema_migrations ORDER BY version DESC LIMIT 10;
"

# Run migrations via application
kubectl run migrate --rm -it \
    --image=nuvanta/kosmos-migrations:latest \
    --restart=Never \
    --env="DATABASE_URL=postgresql://kosmos:***@postgres-primary:5432/kosmos" \
    -- alembic upgrade head

# Verify migration
kubectl exec -it postgres-0 -n kosmos-db -- psql -U kosmos -c "
SELECT * FROM schema_migrations ORDER BY version DESC LIMIT 5;
"
```

#### Vacuum and Analyze

```bash
# Run VACUUM ANALYZE on all tables
kubectl exec postgres-0 -n kosmos-db -- psql -U kosmos -c "
VACUUM ANALYZE;
"

# Check vacuum stats
kubectl exec postgres-0 -n kosmos-db -- psql -U kosmos -c "
SELECT 
    schemaname,
    relname,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    n_live_tup,
    n_dead_tup
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 10;
"
```

### Performance Tuning

#### Key Configuration Parameters

```ini
# postgresql.conf tuning for 8GB node
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
work_mem = 64MB
max_connections = 200
max_parallel_workers_per_gather = 2
max_parallel_workers = 4
max_wal_size = 4GB
min_wal_size = 1GB
checkpoint_completion_target = 0.9
random_page_cost = 1.1
effective_io_concurrency = 200
default_statistics_target = 100
```

#### Index Management

```sql
-- Find missing indexes
SELECT 
    schemaname,
    relname,
    seq_scan,
    idx_scan,
    seq_scan - idx_scan AS seq_vs_idx
FROM pg_stat_user_tables
WHERE seq_scan > idx_scan
ORDER BY seq_vs_idx DESC
LIMIT 10;

-- Find unused indexes
SELECT 
    schemaname,
    relname AS tablename,
    indexrelname AS indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
AND schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Create index concurrently (non-blocking)
CREATE INDEX CONCURRENTLY idx_conversations_tenant_created 
ON conversations(tenant_id, created_at DESC);
```

---

## pgvector Operations

### Vector Index Management

```sql
-- Check vector index status
SELECT 
    indexname,
    indexdef,
    pg_size_pretty(pg_relation_size(indexname::regclass)) as size
FROM pg_indexes
WHERE tablename = 'embeddings';

-- Create IVFFlat index for approximate search
CREATE INDEX CONCURRENTLY idx_embeddings_vector 
ON embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- For exact search (slower but more accurate)
CREATE INDEX CONCURRENTLY idx_embeddings_vector_exact
ON embeddings 
USING hnsw (embedding vector_cosine_ops);

-- Query with vector similarity
SELECT 
    id,
    content,
    1 - (embedding <=> '[0.1, 0.2, ...]'::vector) as similarity
FROM embeddings
WHERE tenant_id = 'tenant-uuid'
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 10;
```

### Reindex Vectors

```bash
#!/bin/bash
# reindex-vectors.sh

echo "Reindexing vector indexes..."

kubectl exec postgres-0 -n kosmos-db -- psql -U kosmos -c "
-- Drop old index
DROP INDEX IF EXISTS idx_embeddings_vector;

-- Recreate with updated parameters
CREATE INDEX CONCURRENTLY idx_embeddings_vector 
ON embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 200);  -- Increase lists for larger datasets
"

echo "Reindexing completed"
```

---

## Dragonfly (Cache) Operations

### Connection

```bash
# Connect to Dragonfly
kubectl exec -it dragonfly-0 -n kosmos-db -- redis-cli

# Or via port-forward
kubectl port-forward svc/dragonfly 6379:6379 -n kosmos-db
redis-cli -h localhost -p 6379
```

### Health Checks

```bash
# Ping
kubectl exec dragonfly-0 -n kosmos-db -- redis-cli ping
# Expected: PONG

# Info
kubectl exec dragonfly-0 -n kosmos-db -- redis-cli info

# Memory usage
kubectl exec dragonfly-0 -n kosmos-db -- redis-cli info memory

# Key count by database
kubectl exec dragonfly-0 -n kosmos-db -- redis-cli info keyspace
```

### Common Operations

```bash
# Flush specific pattern (careful!)
kubectl exec dragonfly-0 -n kosmos-db -- redis-cli --scan --pattern "session:*" | \
    xargs -L 100 kubectl exec dragonfly-0 -n kosmos-db -- redis-cli del

# Get slow log
kubectl exec dragonfly-0 -n kosmos-db -- redis-cli slowlog get 10

# Monitor real-time commands (debug only)
kubectl exec dragonfly-0 -n kosmos-db -- redis-cli monitor
```

### Cache Invalidation

```bash
#!/bin/bash
# invalidate-cache.sh

PATTERN="$1"

if [ -z "$PATTERN" ]; then
    echo "Usage: $0 <pattern>"
    echo "Examples:"
    echo "  $0 'user:*'           # All user caches"
    echo "  $0 'agent:zeus:*'     # Zeus agent caches"
    echo "  $0 'tenant:abc123:*'  # Specific tenant caches"
    exit 1
fi

echo "Invalidating cache pattern: ${PATTERN}"

COUNT=$(kubectl exec dragonfly-0 -n kosmos-db -- \
    redis-cli --scan --pattern "${PATTERN}" | wc -l)

echo "Found ${COUNT} keys to delete"
read -p "Continue? (y/n): " CONFIRM

if [ "$CONFIRM" = "y" ]; then
    kubectl exec dragonfly-0 -n kosmos-db -- \
        redis-cli --scan --pattern "${PATTERN}" | \
        xargs -L 100 kubectl exec dragonfly-0 -n kosmos-db -- redis-cli del
    echo "Cache invalidated"
else
    echo "Cancelled"
fi
```

---

## Troubleshooting

### High Connection Count

```sql
-- Find connection sources
SELECT 
    usename,
    application_name,
    client_addr,
    count(*) as connections
FROM pg_stat_activity
WHERE datname = 'kosmos'
GROUP BY usename, application_name, client_addr
ORDER BY connections DESC;

-- Terminate idle connections (> 10 min)
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'kosmos'
AND state = 'idle'
AND state_change < now() - interval '10 minutes';
```

### Long-Running Queries

```sql
-- Find long-running queries
SELECT 
    pid,
    now() - query_start as duration,
    state,
    query
FROM pg_stat_activity
WHERE state != 'idle'
AND now() - query_start > interval '1 minute'
ORDER BY duration DESC;

-- Cancel a query (graceful)
SELECT pg_cancel_backend(12345);

-- Terminate a query (force)
SELECT pg_terminate_backend(12345);
```

### Lock Contention

```sql
-- Find blocked queries
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity 
    ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks 
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity 
    ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

### Disk Space Issues

```bash
# Check disk usage
kubectl exec postgres-0 -n kosmos-db -- df -h /var/lib/postgresql/data

# Find largest tables
kubectl exec postgres-0 -n kosmos-db -- psql -U kosmos -c "
SELECT 
    relname as table,
    pg_size_pretty(pg_total_relation_size(relid)) as total_size,
    pg_size_pretty(pg_relation_size(relid)) as data_size,
    pg_size_pretty(pg_indexes_size(relid)) as index_size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 10;
"

# Find and remove old WAL files (if space critical)
kubectl exec postgres-0 -n kosmos-db -- \
    pg_archivecleanup /var/lib/postgresql/data/pg_wal <oldest_needed_wal>
```

---

## Monitoring Queries

### Key Metrics Dashboard Queries

```sql
-- Transaction rate
SELECT 
    sum(xact_commit + xact_rollback) as total_transactions,
    sum(xact_commit) as commits,
    sum(xact_rollback) as rollbacks
FROM pg_stat_database
WHERE datname = 'kosmos';

-- Cache hit ratio (should be > 99%)
SELECT 
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) * 100 
    as cache_hit_ratio
FROM pg_statio_user_tables;

-- Index hit ratio
SELECT 
    sum(idx_blks_hit) / (sum(idx_blks_hit) + sum(idx_blks_read)) * 100 
    as index_hit_ratio
FROM pg_statio_user_indexes;

-- Replication lag (seconds)
SELECT 
    EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) 
    as replication_lag_seconds;
```

---

## Emergency Procedures

### Database Failover

```bash
#!/bin/bash
# failover-postgres.sh
# Use when primary is unresponsive

echo "=== POSTGRES FAILOVER ==="
echo "WARNING: This will promote replica to primary"
read -p "Type 'FAILOVER' to confirm: " CONFIRM

if [ "$CONFIRM" != "FAILOVER" ]; then
    echo "Cancelled"
    exit 1
fi

# 1. Promote replica
kubectl exec postgres-replica-0 -n kosmos-db -- \
    pg_ctl promote -D /var/lib/postgresql/data

# 2. Update service to point to new primary
kubectl patch svc postgres-primary -n kosmos-db \
    -p '{"spec":{"selector":{"statefulset.kubernetes.io/pod-name":"postgres-replica-0"}}}'

# 3. Restart applications to reconnect
kubectl rollout restart deployment -n kosmos-core --all

# 4. Verify
kubectl exec -it postgres-replica-0 -n kosmos-db -- \
    psql -U kosmos -c "SELECT pg_is_in_recovery();"
# Should return 'f' (false) indicating it's now primary

echo "Failover completed"
```

---

## Related Documentation

- [Disaster Recovery Plan](disaster-recovery)
- [Kubernetes Architecture](kubernetes)
- [ADR-005: Data Storage Selection](../../02-architecture/adr/ADR-005-data-storage-selection)

---

**Document Owner:** dba@nuvanta-holding.com  
**Emergency Contact:** oncall@nuvanta-holding.com
