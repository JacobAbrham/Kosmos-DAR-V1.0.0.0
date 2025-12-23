# Demeter Data Agent (DEPRECATED)

:::warning Deprecated Agent
    This agent has been deprecated in KOSMOS V1.0.0. Its responsibilities have been distributed to:
    
    - **ATHENA** - Knowledge & RAG operations, document processing
    - **MEMORIX** - Data curation, cross-platform sync
    - **Hephaestus** - Infrastructure and pipeline operations
    - **n8n** - Workflow automation and ETL
    
    See the respective agent documentation for current implementations.

---

**Domain:** Data Management, ETL & Pipelines  
**Greek Deity:** Demeter - Goddess of Harvest  
**Status:** ~~Active~~ **DEPRECATED**  
**Version:** 1.0.0  
**Deprecated In:** V1.0.0

---

## Overview

Demeter is the **data management** agent, responsible for data operations, ETL pipelines, and data quality. Named after the goddess of harvest, Demeter cultivates and manages the data that nourishes KOSMOS.

### Key Capabilities

- **Data Queries** - Execute database queries
- **ETL Operations** - Transform and load data
- **Data Quality** - Validate data integrity
- **Pipeline Management** - Monitor data pipelines
- **Data Export** - Export data in various formats

### Supported Actions

| Action | Description | Required Params |
|--------|-------------|-----------------|
| `query_data` | Execute SQL query | `query`, `database` |
| `run_pipeline` | Trigger ETL pipeline | `pipeline_id` |
| `validate_data` | Run data quality checks | `dataset`, `rules` |
| `export_data` | Export to file | `query`, `format`, `destination` |
| `get_pipeline_status` | Check pipeline status | `pipeline_id` |

### MCP Connections

| MCP Server | Purpose |
|------------|---------|
| database-mcp | Database operations |
| storage-mcp | Object storage access |

---

## Deprecation Rationale

Demeter's functionality was too generic and overlapped with multiple specialized agents:

1. **Knowledge retrieval** → ATHENA (RAG, semantic search, pgvector)
2. **Data curation** → MEMORIX (content organization, deduplication)
3. **ETL pipelines** → n8n (workflow automation)
4. **Infrastructure ops** → Hephaestus (DevOps automation)

The V1.0.0 architecture consolidates data operations into purpose-specific agents with clearer responsibilities.

---

**Last Updated:** 2025-12-12  
**Archived:** 2025-12-13
