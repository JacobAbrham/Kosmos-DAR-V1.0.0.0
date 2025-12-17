# MCP Server Strategy

!!! info "Model Context Protocol"
    KOSMOS uses the **Model Context Protocol (MCP)** as its standard for tool integration, enabling agents to interact with external services through a unified interface.

## Overview

MCP servers provide standardized tool interfaces for KOSMOS agents. The architecture supports 88 MCP servers across 9 domains for comprehensive Nuvanta Holding operations.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AGENT LAYER                              │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │  Zeus   │ │ Hermes  │ │  AEGIS  │ │ Athena  │ │   ...   │  │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘  │
│       │          │          │          │          │           │
│       └──────────┴──────────┴──────────┴──────────┘           │
│                             │                                  │
│                     ┌───────▼───────┐                         │
│                     │  MCP Router   │                         │
│                     └───────┬───────┘                         │
└─────────────────────────────┼─────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
    ┌───────────┐       ┌───────────┐       ┌───────────┐
    │ Core MCP  │       │ Domain    │       │ External  │
    │ Servers   │       │ MCP       │       │ MCP       │
    │           │       │ Servers   │       │ Servers   │
    │ postgresql│       │ erpnext   │       │ searxng   │
    │ nats      │       │ paperless │       │ google    │
    │ litellm   │       │ outline   │       │ stripe    │
    └───────────┘       └───────────┘       └───────────┘
```

## Server Categories

### Core Infrastructure (5 servers)

| Server | Purpose | Agent Users |
|--------|---------|-------------|
| `mcp-postgresql` | Primary database | All agents |
| `mcp-nats` | Message bus | Zeus, Hermes, all |
| `mcp-litellm` | LLM routing | Hermes, all |
| `mcp-zitadel` | Identity | Zeus, AEGIS |
| `mcp-infisical` | Secrets | Zeus, AEGIS |

### Security & Compliance (12 servers)

| Server | Purpose |
|--------|---------|
| `mcp-falco` | Runtime security |
| `mcp-kyverno` | Policy enforcement |
| `mcp-trivy` | Vulnerability scanning |
| `mcp-compliance-monitor` | Compliance tracking |
| `mcp-sanctions-screening` | OFAC/EU/UN screening |
| `mcp-aml` | Anti-money laundering |

### Knowledge & Documents (10 servers)

| Server | Purpose |
|--------|---------|
| `mcp-haystack` | RAG pipeline |
| `mcp-pgvector` | Vector search |
| `mcp-paperless-ngx` | Document management |
| `mcp-outline` | Wiki/knowledge base |
| `mcp-searxng` | Web search |
| `mcp-unstructured` | Document processing |

## Implementation Status

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Implemented | 12 | 14% |
| 🔄 In Progress | 8 | 9% |
| 📋 Planned | 68 | 77% |

### Phase 1 Priority

| Priority | Servers | Timeline |
|----------|---------|----------|
| P0 Critical | postgresql, nats, litellm, zitadel, infisical | Week 1-2 |
| P1 High | haystack, pgvector, falco, kyverno, signoz, langfuse | Week 3-4 |
| P2 Medium | paperless-ngx, outline, n8n, argocd | Week 5-8 |

## Configuration

```yaml
# mcp-config.yaml
servers:
  postgresql:
    endpoint: http://mcp-postgresql:8080
    timeout: 30s
    retry: 3
    
  litellm:
    endpoint: http://litellm:4000
    timeout: 120s
    
permissions:
  zeus: ["postgresql:*", "nats:*", "zitadel:verify_*"]
  aegis: ["falco:*", "kyverno:*", "trivy:*"]
  athena: ["haystack:*", "pgvector:*", "paperless-ngx:*"]
```

---

## See Also

- [Agent-MCP Matrix](../02-architecture/agents/agent-mcp-matrix.md) — Agent integrations
- [LiteLLM Gateway](../02-architecture/cloud-inference.md) — LLM routing

---

**Last Updated:** December 2025
