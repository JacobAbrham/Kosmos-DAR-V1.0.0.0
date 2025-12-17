# MEMORIX Memory & Curation Agent

**Domain:** Memory Management, Data Curation & Synchronization  
**Symbol:** 🧠 (Brain)  
**Status:** Active  
**Version:** 1.0.0

---

## Overview

MEMORIX is the **Lexicon Memory & Curation Agent**, responsible for long-term memory management, context preservation, memory consolidation, relationship mapping, user preferences, personal data curation, content categorization, and cross-platform synchronization. MEMORIX maintains a rich, organized, and private digital archive of user data and preferences, feeding into both personal and enterprise contexts.

## Core Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **Long-term Memory** | Persistent storage of conversations and decisions |
| **Context Preservation** | Maintaining relevant context across sessions |
| **Memory Consolidation** | Summarizing and organizing historical data |
| **Relationship Mapping** | Graph-based entity relationships (Apache AGE) |
| **Data Curation** | Content organization, deduplication, quality |
| **Cross-Platform Sync** | Multi-device data consistency |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       MEMORIX AGENT                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Memory Module  │  │ Curation Module │  │   Sync Module   │ │
│  │                 │  │                 │  │                 │ │
│  │ • Store/recall  │  │ • Categorize    │  │ • Conflict res  │ │
│  │ • Consolidate   │  │ • Deduplicate   │  │ • Bandwidth opt │ │
│  │ • Summarize     │  │ • Quality check │  │ • Consistency   │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           │                    │                    │          │
│           └────────────────────┼────────────────────┘          │
│                                │                               │
│                    ┌───────────▼───────────┐                   │
│                    │   Relationship Graph  │                   │
│                    │    (Apache AGE)       │                   │
│                    └───────────────────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
    ┌──────────┐         ┌──────────┐         ┌──────────┐
    │PostgreSQL│         │  MinIO   │         │   Zep    │
    │  + AGE   │         │ (Objects)│         │ (Memory) │
    └──────────┘         └──────────┘         └──────────┘
```

## Supported Actions

| Action | Description | Required Params | Approval |
|--------|-------------|-----------------|----------|
| `store_memory` | Save to long-term memory | `content`, `context`, `tags` | Auto |
| `recall_memory` | Retrieve relevant memories | `query`, `filters` | Auto |
| `consolidate_memories` | Summarize related memories | `topic`, `time_range` | Auto |
| `map_relationship` | Create entity relationship | `entity_a`, `entity_b`, `relation` | Auto |
| `curate_content` | Organize and categorize | `content_ids`, `rules` | Auto |
| `sync_data` | Synchronize across platforms | `source`, `target` | Auto |
| `deduplicate` | Remove duplicate content | `scope`, `strategy` | Auto |

## MCP Connections

| MCP Server | Purpose | Direction |
|------------|---------|-----------|
| `mcp-postgresql` | Structured memory storage | Bidirectional |
| `mcp-age` | Graph relationships | Bidirectional |
| `mcp-minio` | Object storage for files | Bidirectional |
| `mcp-local-filesystem` | Local file access | Inbound |
| `mcp-google-drive` | Cloud storage sync | Bidirectional |
| `mcp-onedrive` | Cloud storage sync | Bidirectional |

## Memory Architecture

### Storage Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                     MEMORY HIERARCHY                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  HOT MEMORY (Dragonfly)                                        │
│  ├── Active session context                                     │
│  ├── Recent agent interactions                                  │
│  └── Frequently accessed preferences                            │
│                                                                 │
│  WARM MEMORY (PostgreSQL)                                       │
│  ├── Consolidated conversation summaries                        │
│  ├── Entity relationships (Apache AGE)                         │
│  ├── User preferences and settings                             │
│  └── Indexed document metadata                                  │
│                                                                 │
│  COLD MEMORY (MinIO/OSS)                                       │
│  ├── Full conversation archives                                 │
│  ├── Document content                                          │
│  ├── Media files                                               │
│  └── Historical snapshots                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Configuration

```yaml
# memorix-config.yaml
agent:
  name: memorix
  version: "1.0.0"
  icon: "🧠"
  
memory:
  hot_cache_ttl: 3600          # 1 hour in Dragonfly
  warm_retention_days: 365      # 1 year in PostgreSQL
  cold_retention_days: 2555     # 7 years in MinIO
  
  consolidation:
    auto_enabled: true
    frequency: "0 2 * * 0"      # Weekly at 2 AM Sunday
    min_memories_threshold: 50
    
curation:
  deduplication:
    auto_enabled: true
    strategy: "similarity"
    threshold: 0.95
    
sync:
  default_strategy: "last_write"
  bandwidth_limit: "10MB/s"
  conflict_notification: true
```

## Monitoring

### Key Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `memorix_memories_total` | Total memory count | N/A |
| `memorix_recall_latency` | Recall response time | > 500ms |
| `memorix_deduplication_rate` | Duplicate detection rate | > 20% |
| `memorix_sync_conflicts` | Sync conflict count | > 10/day |

---

## See Also

- [Personal Data Ecosystem](../../06-personal-data/personal-data-ecosystem.md) — Data integration
- [Unified Data Fabric](../unified-data-fabric.md) — Data architecture

---

**Last Updated:** December 2025
