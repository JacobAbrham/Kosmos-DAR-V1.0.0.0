# Architectural Decision Records

**Documenting the "Why" Behind Technical Choices**

!!! abstract "Purpose"
    ADRs capture significant architectural decisions, preserving context for future maintainers and enabling informed changes.

---

## Active ADRs

| ID | Title | Status | Date |
|----|-------|--------|------|
| [ADR-005](ADR-005-data-storage-selection.md) | Data Storage Selection | ✅ Accepted | 2025-12 |
| [ADR-006](ADR-006-llm-provider-strategy.md) | LLM Provider Strategy | ✅ Accepted | 2025-12 |
| [ADR-007](ADR-007-observability-stack.md) | Observability Stack | ✅ Accepted | 2025-12 |
| [ADR-009](ADR-009-langgraph-selection.md) | LangGraph Selection | ✅ Accepted | 2025-12 |
| [ADR-011](ADR-011-rag-architecture.md) | RAG Architecture | ✅ Accepted | 2025-12 |
| [ADR-018](ADR-018-memory-architecture.md) | Memory Architecture | ✅ Accepted | 2025-12 |
| [ADR-024](ADR-024-security-architecture.md) | Security Architecture | ✅ Accepted | 2025-12 |

---

## Additional ADRs (Reference)

These ADRs exist in the repository but are not featured in primary navigation:

| ID | Title | Status |
|----|-------|--------|
| [ADR-001](ADR-001-documentation-framework.md) | Documentation Framework | ✅ Accepted |
| [ADR-002](ADR-002-version-control-strategy.md) | Version Control Strategy | ✅ Accepted |
| [ADR-003](ADR-003-deployment-pipeline.md) | Deployment Pipeline | ✅ Accepted |
| [ADR-004](ADR-004-authentication-strategy.md) | Authentication Strategy | ✅ Accepted |
| [ADR-008](ADR-008-api-versioning-strategy.md) | API Versioning Strategy | ✅ Accepted |
| [ADR-010](ADR-010-mcp-adoption.md) | MCP Adoption | ✅ Accepted |
| [ADR-012](ADR-012-multi-tenancy-strategy.md) | Multi-Tenancy Strategy | ✅ Accepted |
| [ADR-013](ADR-013-cost-optimization-strategy.md) | Cost Optimization | ✅ Accepted |
| [ADR-014](ADR-014-agent-communication-protocol.md) | Agent Communication | ✅ Accepted |

---

## ADR Format

Each ADR follows the standard format:

```markdown
# ADR-XXX: Title

## Status
Accepted | Proposed | Deprecated | Superseded

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that we're proposing and/or doing?

## Consequences
What becomes easier or more difficult to do because of this change?
```

---

## Creating New ADRs

1. Copy `template.md` to `ADR-XXX-descriptive-name.md`
2. Fill in all sections
3. Submit PR for review
4. Update this index after approval

---

**Last Updated:** December 2025
