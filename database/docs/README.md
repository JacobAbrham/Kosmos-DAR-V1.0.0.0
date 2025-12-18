# Database Documentation

This directory contains comprehensive database documentation.

## Contents

- Entity Relationship Diagrams (ERD)
- Data dictionary
- Migration guides
- Performance tuning notes
- Backup and recovery procedures

## Quick Links

- [Schema README](../schemas/README.md) - Schema definitions
- [Migration Guide](../migrations/README.md) - Alembic migrations
- Initial Schema: `../schemas/001_initial_schema.sql`

## Database Environments

### Development
- **Database:** `kosmos_dev`
- **Host:** localhost:5432
- **Purpose:** Local development and testing

### Staging
- **Database:** `kosmos_staging`
- **Host:** postgres-staging:5432
- **Purpose:** Pre-production testing

### Production
- **Database:** `kosmos_prod`
- **Host:** postgres-prod:5432
- **Purpose:** Production workloads

## Schema Overview

```
agents              - Agent definitions (11 agents)
├── conversations   - User conversation sessions
│   └── messages   - Individual messages
├── pentarchy_votes - Governance voting records
└── agent_executions - Task execution logs
```

## Maintenance

### Backups
```bash
# Development
pg_dump -U kosmos kosmos_dev > backup_dev_$(date +%Y%m%d).sql

# Production (use automated backups)
# Configured in infrastructure/kubernetes/
```

### Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "add_new_table"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1
```

## Performance Tuning

Key indexes are created for:
- Conversation lookups by user_id
- Message lookups by conversation_id
- Agent execution filtering by status
- Vote lookups by proposal_id

Monitor query performance with:
```sql
EXPLAIN ANALYZE SELECT ...;
```
