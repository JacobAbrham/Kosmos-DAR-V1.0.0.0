# Personal Data Ecosystem

:::info Digital Life Integration
    KOSMOS extends beyond enterprise operations to manage personal digital life, creating a unified context across professional, personal, and entertainment domains.

## Overview

The Personal Data Ecosystem provides comprehensive management of user's digital footprint while maintaining strict privacy controls and data sovereignty.

## Three Domains

```
┌─────────────────────────────────────────────────────────────────┐
│                     KOSMOS PERSONAL DATA                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐│
│  │   PROFESSIONAL   │ │     PERSONAL     │ │  ENTERTAINMENT   ││
│  │                  │ │                  │ │                  ││
│  │ • Work documents │ │ • Personal files │ │ • Music library  ││
│  │ • Projects       │ │ • Photos         │ │ • Video content  ││
│  │ • Communications │ │ • Notes          │ │ • Podcasts       ││
│  │ • Calendar       │ │ • Contacts       │ │ • Reading list   ││
│  └──────────────────┘ └──────────────────┘ └──────────────────┘│
│                              │                                  │
│                    ┌─────────▼─────────┐                       │
│                    │   UNIFIED INDEX   │                       │
│                    │    (MEMORIX)      │                       │
│                    └───────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

## Data Sources

### Priority Integration Order

| Priority | Source | Agent Owner | Status |
|----------|--------|-------------|--------|
| P0 | Local filesystem | MEMORIX | Phase 1 |
| P0 | Google Drive | MEMORIX | Phase 1 |
| P1 | OneDrive | MEMORIX | Phase 2 |
| P1 | Email archives | ATHENA | Phase 2 |
| P2 | iCloud | MEMORIX | Phase 3 |
| P2 | Dropbox | MEMORIX | Phase 3 |
| P3 | Social archives | MEMORIX | Phase 4 |

### MCP Servers

| MCP Server | Purpose |
|------------|---------|
| `mcp-local-filesystem` | Local file access |
| `mcp-google-drive` | Google Drive integration |
| `mcp-onedrive` | OneDrive integration |
| `mcp-icloud` | iCloud integration |
| `mcp-email-archive` | Email processing |

## Data Categories

### Documents

| Type | Processing | Storage |
|------|------------|---------|
| Text (txt, md) | Direct indexing | PostgreSQL + pgvector |
| Office (docx, xlsx) | Unstructured extraction | MinIO + metadata |
| PDF | OCR + extraction | MinIO + pgvector |
| Code | Syntax-aware indexing | PostgreSQL |

### Media

| Type | Processing | Storage |
|------|------------|---------|
| Images | EXIF + AI tagging | MinIO + metadata |
| Audio | Metadata + transcription | MinIO |
| Video | Metadata + scene detection | MinIO |

## Privacy Architecture

### Data Sovereignty Principles

1. **User owns all data** — Full export capability always available
2. **Local-first processing** — Sensitive data processed on-device when possible
3. **Encryption at rest** — All stored data encrypted
4. **Granular permissions** — User controls access per-source
5. **Audit trail** — Complete log of all data access

### Privacy Zones

```
┌─────────────────────────────────────────────────┐
│              PRIVACY ZONE MODEL                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  ZONE 1: PUBLIC                                │
│  └── Shared across all contexts                │
│                                                 │
│  ZONE 2: PROFESSIONAL                          │
│  └── Work-related, shareable with colleagues   │
│                                                 │
│  ZONE 3: PERSONAL                              │
│  └── Private, user-only access                 │
│                                                 │
│  ZONE 4: SENSITIVE                             │
│  └── Encrypted, explicit unlock required       │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Configuration

```yaml
# personal-data-config.yaml
sync:
  enabled: true
  interval: 300  # 5 minutes
  bandwidth_limit: "10MB/s"
  
sources:
  local_filesystem:
    enabled: true
    paths:
      - ~/Documents
      - ~/Desktop
    exclude:
      - "*.tmp"
      - ".git"
      
  google_drive:
    enabled: true
    sync_mode: "selective"
    
privacy:
  default_zone: PERSONAL
  encryption: AES-256-GCM
  
retention:
  documents: 2555  # 7 years
  media: 3650      # 10 years
  communications: 365  # 1 year default
```

---

## See Also

- [MEMORIX Agent](../02-architecture/agents/memorix-memory) — Memory management
- [Entertainment & Media](../07-entertainment/media-management) — Media features

---

**Last Updated:** December 2025
