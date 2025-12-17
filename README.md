# KOSMOS Documentation

**AI-Native Enterprise Operating System — V1.0.0**

## Overview

KOSMOS (Knowledge-Orchestrated System for Multi-agent Operational Superintelligence) is an AI-native enterprise operating system featuring 11 specialized agents designed for holding company operations.

**Core Philosophy:** *"Agents Work. Humans Approve."*

## Key Features

- **11 Specialized Agents** — Zeus, Hermes, AEGIS, Chronos, Athena, Hephaestus, Nur PROMETHEUS, Iris, MEMORIX, Hestia, Morpheus
- **88 MCP Servers** — Comprehensive tool integration across 9 domains
- **Pentarchy Governance** — Multi-agent decision-making for operations $50-$100
- **32GB RAM Target** — Optimized for single-node deployment
- **Multi-Jurisdiction Compliance** — GDPR, CCPA, UAE PDPL, ISO 42001

## Quick Links

- [Philosophy](philosophy.md) — Core principles and paradigm
- [Roadmap](docs/00-executive/roadmap.md) — Implementation timeline
- [Agent Pantheon](docs/02-architecture/agents/README.md) — Agent documentation
- [Deployment Checklist](docs/04-operations/deployment-checklist.md) — Deployment guide

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional)

### Running the System

1. **Start the API Gateway** (Backend)
   ```powershell
   ./scripts/run_api.ps1
   ```
   *Runs on http://localhost:8000*

2. **Start the Frontend** (UI)
   ```powershell
   ./scripts/run_frontend.ps1
   ```
   *Runs on http://localhost:3000*

3. **Run Integration Tests**
   ```powershell
   python tests/test_swarm_integration.py
   ```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     KOSMOS ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────┤
│  Layer 4: Human Interface (Nexus Dashboard, K-Palette)          │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3: AI Kernel (11 Agents, LangGraph, MCP Servers)         │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: Unified Data Fabric (PostgreSQL+, Dragonfly, MinIO)   │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1: Cloud Infrastructure (K3s, Alibaba Cloud)             │
└─────────────────────────────────────────────────────────────────┘
```

## Documentation Structure

```
docs/
├── 00-executive/      # Strategy, roadmap, value proposition
├── 01-governance/     # Pentarchy, cost governance, kill switch
├── 02-architecture/   # Data fabric, agents, ADRs
├── 03-engineering/    # MCP, prompts, API design
├── 04-operations/     # Deployment, observability, incident response
├── 05-human-factors/  # UI/UX, accessibility, ergonomics
├── 06-personal-data/  # Personal data ecosystem, privacy
└── 07-entertainment/  # Media management, curation
```

## Getting Started

1. Review the [Philosophy](philosophy.md)
2. Understand the [Roadmap](docs/00-executive/roadmap.md)
3. Follow the [Deployment Checklist](docs/04-operations/deployment-checklist.md)

## Development Options

- **GitHub Codespaces (recommended for day-to-day)**  
  Uses `.devcontainer/devcontainer.json` to install deps automatically. Create a Codespace from GitHub, then run `uvicorn src.main:app --reload --host 0.0.0.0 --port 8000` to start the stub API, or `docker compose up -d` if you want the full stack.

- **Local Docker (optional fallback)**  
  A `docker-compose.yml` is available. Run `.\scripts\setup-local-docker.ps1` on Windows/PowerShell to set up venv, install deps, and start Postgres/Redis/MinIO + the API.

## Building Docs

```bash
# Install MkDocs
pip install mkdocs-material

# Serve locally
mkdocs serve

# Build static site
mkdocs build
```

## License

Copyright © 2025 Nuvanta Holding

---

**Version:** 1.0.0  
**Last Updated:** December 2025
