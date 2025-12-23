# Changelog

All notable changes to KOSMOS documentation are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Navigation audit and remediation tracking

### Changed
- ADR section reorganized to match existing ADR files

### Fixed
- Broken navigation references to non-existent ADR files

---

## [1.0.0] - 2025-12-14

### Added

#### Executive Section
- `digital-agentic-realm.md` - Source of Truth document
- `philosophy.md` - Core philosophy and guiding principles
- `roadmap.md` - Implementation roadmap
- `value-proposition.md` - Internal value proposition
- `closing-recommendations.md` - Strategic recommendations

#### Governance
- `pentarchy-governance.md` - Pentarchy voting model
- `cost-governance.md` - Cost control framework (Spec C)
- `kill-switch-protocol.md` - Emergency halt procedures
- `ethics-scorecard.md` - Ethics evaluation framework

#### Architecture
- `unified-data-fabric.md` - Data architecture
- `cloud-inference.md` - HuggingFace inference strategy

#### Agent Documentation (11 agents)
- `zeus-orchestrator.md` - Supervisor agent
- `hermes-communications.md` - Communication orchestrator
- `aegis-security.md` - Security & compliance (NEW - replaces Ares)
- `chronos-scheduling.md` - Time & scheduling
- `athena-knowledge.md` - Knowledge & research
- `hephaestus-tooling.md` - Operations & tooling
- `nur-prometheus-strategy.md` - Strategy & analytics (NEW)
- `iris-interface.md` - User interface & communications
- `memorix-memory.md` - Memory management (NEW)
- `hestia-personal.md` - Personal assistant (NEW)
- `morpheus-learning.md` - Learning & adaptation (NEW)
- `agent-mcp-matrix.md` - Agent-MCP mapping

#### ADRs
- `ADR-018-memory-architecture.md` - MEMORIX memory strategy
- `ADR-024-security-architecture.md` - Zitadel + Falco + Kyverno

#### Engineering
- `api-design.md` - REST API standards
- `testing-strategy.md` - Test pyramid and LLM testing

#### Operations
- `boot-sequence.md` - 7-wave boot sequence
- `alibaba-cloud.md` - Cloud infrastructure setup
- `k3s-config.md` - K3s cluster configuration
- `signoz.md` - Unified observability
- `langfuse.md` - LLM observability
- `incident-response.md` - Incident playbook index
- `backup-recovery.md` - Backup procedures

#### Security
- `falco-runtime.md` - Runtime threat detection
- `kyverno-policies.md` - Kubernetes policies
- `zitadel-identity.md` - Identity management

#### Human Factors
- `ui-ux-guidelines.md` - Design standards
- `ergonomic-design.md` - 16-hour ergonomic design
- `accessibility.md` - WCAG compliance

#### Personal Data
- `personal-data-ecosystem.md` - Digital life integration
- `cloud-integrations.md` - Google, OneDrive, iCloud
- `privacy-controls.md` - Privacy zones
- `data-portability.md` - Export/import capabilities

#### Entertainment
- `media-management.md` - Media stack overview
- `music-curation.md` - Smart playlists
- `content-compliance.md` - Content filtering

#### Appendices
- `resource-allocation.md` - Appendix A resource tables
- `glossary.md` - KOSMOS terminology

### Changed

#### Agent Pantheon
- **Deprecated**: Apollo, Dionysus, Demeter, Ares, Prometheus (metrics)
- **Added**: AEGIS, Nur PROMETHEUS, MEMORIX, Hestia, Morpheus
- Zeus role clarified as supervisor with Pentarchy governance

#### Infrastructure Stack
- SigNoz replaces Prometheus + Grafana + Jaeger
- Zitadel replaces Keycloak for identity
- Infisical for secrets management

#### Target Environment
- Staging: Single CCX33 node (32GB RAM)
- Production: 3-node K3s cluster

### Removed
- Legacy agent documentation (moved to `archive/v0-agents/`)
- Redundant infrastructure references

---

## [0.9.0] - 2025-12-12

### Added
- Initial documentation structure
- Gap analysis framework
- 170+ markdown files scaffolded

### Changed
- MkDocs configuration standardized
- Navigation structure defined

---

## [0.1.0] - 2025-11-01

### Added
- Repository initialization
- Basic MkDocs setup
- Initial README

---

[Unreleased]: https://github.com/Nuvanta-Holding/kosmos/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Nuvanta-Holding/kosmos/compare/v0.9.0...v1.0.0
[0.9.0]: https://github.com/Nuvanta-Holding/kosmos/compare/v0.1.0...v0.9.0
[0.1.0]: https://github.com/Nuvanta-Holding/kosmos/releases/tag/v0.1.0
