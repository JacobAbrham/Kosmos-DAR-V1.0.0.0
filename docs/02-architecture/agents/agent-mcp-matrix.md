# Agent-MCP Integration Matrix

!!! info "Integration Overview"
    This matrix documents the connections between KOSMOS agents and MCP servers, defining which tools each agent can access and the nature of those integrations.

## Core Agent-MCP Matrix

| Agent | MCP Server | Purpose | Direction | Priority |
|-------|------------|---------|-----------|----------|
| **Zeus** | `mcp-postgresql` | State persistence | Bidirectional | Critical |
| | `mcp-nats` | Agent coordination | Bidirectional | Critical |
| | `mcp-zitadel` | Identity verification | Outbound | Critical |
| | `mcp-infisical` | Secret retrieval | Outbound | Critical |
| **Hermes** | `mcp-nats` | Message routing | Bidirectional | Critical |
| | `mcp-litellm` | LLM inference | Outbound | Critical |
| **AEGIS** | `mcp-falco` | Runtime security | Inbound | Critical |
| | `mcp-kyverno` | Policy enforcement | Bidirectional | Critical |
| | `mcp-trivy` | Vulnerability scan | Outbound | High |
| | `mcp-zitadel` | Access validation | Outbound | Critical |
| **Chronos** | `mcp-postgresql` | Schedule storage | Bidirectional | High |
| | `mcp-calendar` | Calendar sync | Bidirectional | Medium |
| **Athena** | `mcp-haystack` | RAG operations | Bidirectional | Critical |
| | `mcp-paperless-ngx` | Document mgmt | Bidirectional | High |
| | `mcp-outline` | Wiki access | Bidirectional | Medium |
| | `mcp-searxng` | Web search | Outbound | Medium |
| | `mcp-pgvector` | Vector search | Bidirectional | Critical |
| **Hephaestus** | `mcp-argocd` | GitOps | Bidirectional | High |
| | `mcp-harbor` | Container registry | Bidirectional | High |
| | `mcp-n8n` | Workflow automation | Bidirectional | High |
| **Nur PROMETHEUS** | `mcp-langfuse` | LLM analytics | Inbound | High |
| | `mcp-signoz` | System metrics | Inbound | High |
| | `mcp-postgresql` | Analytics queries | Bidirectional | High |
| **Iris** | `mcp-n8n` | Workflow triggers | Outbound | High |
| | `mcp-smtp` | Email sending | Outbound | High |
| | `mcp-webhooks` | External notify | Outbound | Medium |
| **MEMORIX** | `mcp-postgresql` | Memory storage | Bidirectional | Critical |
| | `mcp-age` | Graph relationships | Bidirectional | High |
| | `mcp-minio` | Object storage | Bidirectional | High |
| **Hestia** | `mcp-postgresql` | Preferences | Bidirectional | High |
| | `mcp-minio` | Media storage | Bidirectional | High |
| | `mcp-local-filesystem` | Local files | Inbound | High |
| **Morpheus** | `mcp-langfuse` | LLM traces | Inbound | High |
| | `mcp-signoz` | System metrics | Inbound | High |
| | `mcp-nats` | Event stream | Inbound | High |

## Holding Company Extensions (88 MCP Servers)

### By Domain

| Domain | MCP Server Count | Key Servers |
|--------|------------------|-------------|
| Governance | 8 | board-portal, resolution-tracker |
| Compliance | 12 | sanctions-screening, aml, ubo-tracker |
| Finance | 15 | erpnext, treasury, intercompany |
| Legal | 10 | contract-memory, entity-management |
| Investment | 8 | deal-flow, portfolio-analysis |
| HR | 10 | hris, payroll, performance |
| Communications | 8 | investor-relations, press-releases |
| IT | 12 | asset-inventory, license-management |
| Core | 5 | postgresql, nats, litellm, zitadel, infisical |

### Implementation Status

| Status | Count |
|--------|-------|
| ✅ Implemented | 12 |
| 🔄 In Progress | 8 |
| 📋 Planned | 68 |

## See Also

- [MCP Strategy](../../03-engineering/mcp-strategy.md)
- [Agent Pantheon](README.md)

---

**Last Updated:** December 2025
