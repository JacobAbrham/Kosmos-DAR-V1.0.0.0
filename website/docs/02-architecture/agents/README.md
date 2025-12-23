# The Agent Pantheon

:::info V1.0.0 Agent Architecture
    KOSMOS V1.0.0 features **11 specialized AI agents** designed for maximum efficiency. Agents are not separate containers but **Nodes** within the unified LangGraph runtime, activated on demand.

## Agent Inventory

| # | Agent | Icon | Domain | Status |
|---|-------|------|--------|--------|
| 1 | [Zeus](zeus-orchestrator) | ⚡ | Supervisor & Governance | Active |
| 2 | [Hermes](hermes-communications) | 📨 | Communications & Routing | Active |
| 3 | [AEGIS](aegis-security) | 🛡️ | Security & Compliance | Active |
| 4 | [Chronos](chronos-scheduling) | ⏰ | Scheduling & Temporal | Active |
| 5 | [Athena](athena-knowledge) | 🦉 | Knowledge & RAG | Active |
| 6 | [Hephaestus](hephaestus-tooling) | 🔨 | Operations & DevOps | Active |
| 7 | [Nur PROMETHEUS](nur-prometheus-strategy) | 🔥 | Analytics & Strategy | Active |
| 8 | [Iris](iris-interface) | 🌈 | Communications | Active |
| 9 | [MEMORIX](memorix-memory) | 🧠 | Memory & Curation | Active |
| 10 | [Hestia](hestia-personal) | 🏠 | Personal & Media | Active |
| 11 | [Morpheus](morpheus-learning) | ✨ | Learning & Optimization | Active |

## Agent Specifications

| Agent | Role | Key Integrations |
|-------|------|------------------|
| **Zeus** | Overmind Supervisor - Enforces Constitution, routes tasks, Pentarchy governance | postgresql, nats, zitadel |
| **Hermes** | Orchestrator - Task routing, agent coordination, request/response | nats, litellm |
| **AEGIS** | Guardian - Security monitoring, compliance, threat detection, kill-switch | falco, kyverno, trivy |
| **Chronos** | Scheduler - Calendar, deadlines, temporal context, scheduling | postgresql, calendar |
| **Athena** | Knowledge - RAG operations, document processing, research | haystack, paperless-ngx, pgvector |
| **Hephaestus** | Operations - Code generation, DevOps, infrastructure, workflows | argocd, harbor, n8n |
| **Nur PROMETHEUS** | Strategy - Data analysis, planning, prediction, recommendations | langfuse, signoz |
| **Iris** | Communications - Email, messaging, notifications | n8n, smtp, webhooks |
| **MEMORIX** | Memory - Long-term memory, context, relationships, sync | postgresql/age, minio |
| **Hestia** | Personal - Preferences, UI adaptation, media, wellness | postgresql, minio |
| **Morpheus** | Learning - Pattern recognition, feedback, optimization | langfuse, signoz, nats |

## Pentarchy Governance

Three agents vote for decisions $50-$100:

| Voter | Evaluation |
|-------|------------|
| **Nur PROMETHEUS** | Financial viability |
| **Hephaestus** | Technical feasibility |
| **Athena** | Compliance verification |

## Deprecated Agents (V0)

| Agent | Replaced By |
|-------|-------------|
| Apollo | Nur PROMETHEUS + SigNoz |
| Ares | AEGIS |
| Demeter | ATHENA + MEMORIX + n8n |
| Dionysus | LiteLLM + distributed |
| Prometheus | Nur PROMETHEUS + SigNoz |

See [Archived Agents](../../archive/v0-agents/README) for migration details.

## Integration Matrix

See [Agent-MCP Matrix](agent-mcp-matrix) for complete integration mapping.

---

**Last Updated:** December 2025
