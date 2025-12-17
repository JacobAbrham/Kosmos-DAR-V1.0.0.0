# Archived Agents (V0)

!!! info "Archive Purpose"
    This directory contains agent documentation from pre-V1.0.0 versions that have been deprecated, merged, or superseded by new agents in the current architecture.

## Deprecated Agents

| Agent | Original Role | Deprecated In | Replaced By |
|-------|---------------|---------------|-------------|
| [Apollo](apollo-monitoring.md) | Monitoring & Observability | V1.0.0 | Nur PROMETHEUS + SigNoz |
| [Ares](ares-security.md) | Security & Access Control | V1.0.0 | AEGIS |
| [Demeter](demeter-data.md) | Data Management & ETL | V1.0.0 | ATHENA + MEMORIX + n8n |
| [Dionysus](dionysus-creative.md) | Creative Content | V1.0.0 | ATHENA + HESTIA + IRIS |
| [Prometheus](prometheus-metrics.md) | Metrics & Alerting | V1.0.0 | Nur PROMETHEUS + SigNoz |

## V1.0.0 Agent Pantheon

The current KOSMOS V1.0.0 architecture includes 11 agents:

| # | Agent | Icon | Role |
|---|-------|------|------|
| 1 | **Zeus** | ⚡ | Overmind Supervisor |
| 2 | **Hermes** | 🦉 | Orchestrator |
| 3 | **AEGIS** | 🛡️ | Security & Compliance |
| 4 | **Chronos** | ⏰ | Scheduler & Temporal |
| 5 | **Athena** | 🦉 | Knowledge & RAG |
| 6 | **Hephaestus** | 🔨 | Operations & DevOps |
| 7 | **Nur PROMETHEUS** | 🔥 | Analytics & Strategy |
| 8 | **Iris** | 🌈 | Communications |
| 9 | **MEMORIX** | 🧠 | Memory & Curation |
| 10 | **Hestia** | 🏠 | Personal & Media |
| 11 | **Morpheus** | ✨ | Learning & Optimization |

## Migration Notes

When migrating from V0 to V1.0.0:

1. **Apollo → Nur PROMETHEUS**: Monitoring moved to SigNoz; strategic analytics to Nur PROMETHEUS
2. **Ares → AEGIS**: Enhanced with Falco, Kyverno, Trivy integration
3. **Demeter → Distributed**: ETL to n8n, knowledge to ATHENA, curation to MEMORIX
4. **Dionysus → Distributed**: Creative capabilities distributed to all agents via LiteLLM
5. **Prometheus → Nur PROMETHEUS**: Metrics to SigNoz; strategic insights to Nur PROMETHEUS

## Why Archive Instead of Delete?

1. **Historical reference** for understanding architectural evolution
2. **Migration guide** for existing implementations
3. **Audit trail** for governance compliance
4. **Rollback reference** if needed

---

**Archive Created:** 2025-12-13  
**KOSMOS Version:** V1.0.0
