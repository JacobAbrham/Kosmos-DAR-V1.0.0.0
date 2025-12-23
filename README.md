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
- [Installation](docs/INSTALLATION.md) — Complete installation guide
- [Architecture](docs/ARCHITECTURE.md) — System architecture overview
- [Testing](docs/TESTING.md) — Testing guide and best practices
- [API Reference](docs/developer-guide/api-reference/README.md) — API documentation
- [Roadmap](docs/project-management/IMPLEMENTATION_ROADMAP.md) — Implementation timeline
- [Agent Pantheon](docs/02-architecture/agents/README.md) — Agent documentation
- [Getting Started](docs/deployment/GETTING_STARTED.md) — Quick start guide
- [Deployment Summary](docs/deployment/DEPLOYMENT_SUMMARY.md) — Deployment status

## 📂 Repository Structure

```
KOSMOS-Digital-Agentic-V-1.0.0/
├── config/                  # Environment-specific configurations
│   └── environments/        # Dev, staging, production configs
├── docs/                    # Comprehensive documentation
│   ├── project-management/  # Roadmaps, task tracking
│   ├── deployment/          # Deployment guides
│   ├── assessments/         # Gap analysis, audits
│   ├── technical-debt/      # Debt tracking
│   └── guides/              # How-to guides
├── infrastructure/          # Infrastructure as Code
│   ├── docker/              # Container definitions
│   ├── kubernetes/          # K8s manifests & overlays
│   ├── helm/                # Helm charts
│   └── monitoring/          # Observability stack
├── src/                     # Application source code
│   ├── agents/              # 11 specialized agents
│   ├── api/                 # FastAPI REST API
│   ├── models/              # Database models
│   ├── services/            # Business logic
│   ├── integrations/        # MCP & external services
│   └── utils/               # Shared utilities
├── scripts/                 # Development & deployment scripts
│   ├── setup/               # Environment setup
│   ├── development/         # Dev helper scripts
│   ├── deployment/          # Deployment scripts
│   └── utilities/           # Utility scripts
├── tests/                   # Test suites
│   ├── integration/         # 52 integration tests
│   ├── e2e/                 # End-to-end tests
│   ├── unit/                # Unit tests
│   └── fixtures/            # Test data
├── database/                # Database schemas & migrations
├── frontend/                # Next.js web application
└── gui/                     # Setup wizard
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (recommended)

### Option 1: Docker Compose (Recommended)

Run the entire stack with one command:

```powershell
# Copy environment template
Copy-Item config/environments/development/.env.example .env

# Start all services (API, Frontend, Postgres, Redis, MinIO, Docs)
docker-compose -f config/environments/development/docker-compose.yml up

# Or run in detached mode
docker-compose -f config/environments/development/docker-compose.yml up -d

# View logs
docker-compose -f config/environments/development/docker-compose.yml logs -f api frontend

# Stop all services
docker-compose -f config/environments/development/docker-compose.yml down
```

**Services:**

- API Gateway: http://localhost:8000
- Frontend UI: http://localhost:3000
- API Docs: http://localhost:8000/docs
- MinIO Console: http://localhost:9001
- MkDocs: http://localhost:8080
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Option 2: Native Development

1. **Setup Environment**

   ```powershell
   # Use interactive setup wizard
   .\scripts\setup\setup-interactive.ps1
   
   # Or manually copy environment template
   Copy-Item config/environments/development/.env.example .env
   
   # Start infrastructure only
   docker-compose -f config/environments/development/docker-compose.yml up postgres redis minio -d
   ```

2. **Start the API Gateway** (Backend)

   ```powershell
   .\scripts\development\run_api.ps1
   ```

   *Runs on http://localhost:8000*

3. **Start the Frontend** (UI)

   ```powershell
   .\scripts\development\run_frontend.ps1
   ```

   *Runs on http://localhost:3000*

4. **Run Integration Tests**

   ```powershell
   python tests/test_swarm_integration.py
   ```

### Docker Compose Commands

```powershell
# Start specific services
docker-compose -f config/environments/development/docker-compose.yml up api frontend

# Rebuild images after code changes
docker-compose -f config/environments/development/docker-compose.yml up --build

# View service status
docker-compose -f config/environments/development/docker-compose.yml ps

# View logs
docker-compose -f config/environments/development/docker-compose.yml logs -f

# Clean up
docker-compose -f config/environments/development/docker-compose.yml down -v
```

## 📖 Documentation

Comprehensive documentation is available in the [`docs/`](docs/) directory:

### Core Documentation

- **[Installation Guide](docs/INSTALLATION.md)** - Complete setup instructions
- **[Architecture Overview](docs/ARCHITECTURE.md)** - System design and components
- **[Testing Guide](docs/TESTING.md)** - Testing strategy and practices
- **[API Reference](docs/developer-guide/api-reference/README.md)** - REST API documentation

### Detailed Documentation

- **[Project Management](docs/project-management/)** - Roadmaps, task tracking, changelog
- **[Deployment](docs/deployment/)** - Deployment guides and status
- **[Guides](docs/guides/)** - Development and contribution guides
- **[Assessments](docs/assessments/)** - Gap analysis and test coverage
- **[Architecture](docs/02-architecture/)** - Detailed architecture and ADRs
- **[Engineering](docs/03-engineering/)** - Engineering standards and practices
- **[Security](docs/security/)** - Security architecture and IAM
- **[Architecture](docs/02-architecture/)** - System design and agent specifications

See [docs/README.md](docs/README.md) for complete documentation index.

## 🤝 Contributing

We welcome contributions! Please see:

- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [Development Environment Guide](docs/guides/DEVELOPMENT_ENVIRONMENT_GUIDE.md) - Setup instructions
- [Code Owners](.github/CODEOWNERS) - Review assignments

## 📝 License

See LICENSE file for details.
docker-compose ps

# Access service logs

docker-compose logs -f <service-name>

# Execute commands in running container

docker-compose exec api python -c "print('Hello')"

# Clean up volumes (WARNING: deletes data)

docker-compose down -v

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

Copyright © 2025 Nuvanta Holding. All Rights Reserved.

This is proprietary software. See [LICENSE](LICENSE) for details.

---

**Version:** 1.0.0  
**Last Updated:** December 2025
