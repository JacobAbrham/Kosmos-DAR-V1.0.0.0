# Database Schemas

This directory contains SQL schema definitions for the KOSMOS database.

## Files

- `001_initial_schema.sql` - Initial database schema with core tables
  - agents
  - conversations
  - messages
  - pentarchy_votes
  - agent_executions

## Usage

### Development
```bash
psql -U kosmos -d kosmos_dev -f database/schemas/001_initial_schema.sql
```

### Staging
```bash
psql -U kosmos -d kosmos_staging -f database/schemas/001_initial_schema.sql
```

### Production
```bash
psql -U kosmos -d kosmos_prod -f database/schemas/001_initial_schema.sql
```

## Schema Management

Schemas are versioned with numeric prefixes (001, 002, etc.) to maintain order.

For migrations, use Alembic:
```bash
cd database
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Database Structure

### Core Tables

**agents** - Agent definitions and metadata
- Stores all 11 agent configurations
- Tracks agent status and capabilities

**conversations** - User conversation sessions
- Links to messages
- Stores conversation metadata

**messages** - Individual messages
- Belongs to conversation
- Tracks agent responses

**pentarchy_votes** - Governance voting records
- Stores Pentarchy voting decisions
- Links to agents and proposals

**agent_executions** - Execution logs
- Tracks agent task performance
- Stores execution metrics

## Extensions

The schema requires these PostgreSQL extensions:
- `uuid-ossp` - UUID generation
- `pgvector` - Vector embeddings for RAG
