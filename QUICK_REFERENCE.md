# 🚀 KOSMOS Quick Reference - Post-Reorganization

**Updated:** December 18, 2025

## 📍 Where Things Are Now

### Common Files & Locations

| What You Need | Old Location | New Location |
|---------------|--------------|--------------|
| **Development .env** | `.env.example` | `config/environments/development/.env.example` |
| **Docker Compose** | `docker-compose.yml` | `config/environments/development/docker-compose.yml` |
| **Setup Scripts** | `scripts/setup-*.ps1` | `scripts/setup/setup-*.ps1` |
| **Run Scripts** | `scripts/run_*.ps1` | `scripts/development/run_*.ps1` |
| **Roadmap** | `IMPLEMENTATION_ROADMAP.md` | `docs/project-management/IMPLEMENTATION_ROADMAP.md` |
| **Deployment Guide** | `DEPLOYMENT_SUMMARY.md` | `docs/deployment/DEPLOYMENT_SUMMARY.md` |
| **Getting Started** | `GETTING_STARTED.md` | `docs/deployment/GETTING_STARTED.md` |
| **Gap Analysis** | `COMPREHENSIVE_GAP_ANALYSIS.md` | `docs/assessments/COMPREHENSIVE_GAP_ANALYSIS.md` |
| **Test Coverage** | `TEST_COVERAGE.md` | `docs/assessments/TEST_COVERAGE.md` |
| **Docker Files** | `docker/` | `infrastructure/docker/` |
| **Helm Charts** | `helm/` | `infrastructure/helm/` |
| **K8s Manifests** | `k8s/` | `infrastructure/kubernetes/raw-manifests/` |
| **MCP Code** | `src/mcp/` | `src/integrations/mcp/` |
| **Utilities** | `src/lib/` | `src/utils/` |

---

## ⚡ Quick Commands

### Start Development Environment
```powershell
# Interactive setup (first time)
.\scripts\setup\setup-interactive.ps1

# Docker Compose
docker-compose -f config/environments/development/docker-compose.yml up -d

# Native development
.\scripts\development\run_api.ps1
.\scripts\development\run_frontend.ps1
```

### Access Services
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MinIO Console: http://localhost:9001
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Common Docker Commands
```powershell
# Short alias (add to your profile)
$dc = "docker-compose -f config/environments/development/docker-compose.yml"

# Using alias
& docker-compose -f config/environments/development/docker-compose.yml up -d
& docker-compose -f config/environments/development/docker-compose.yml logs -f
& docker-compose -f config/environments/development/docker-compose.yml down
```

---

## 📂 Directory Cheat Sheet

### Most Commonly Used Directories

**For Development:**
- `config/environments/development/` - Dev environment config
- `src/` - Source code (agents, API, services)
- `scripts/development/` - Development helper scripts
- `tests/` - All test suites

**For Documentation:**
- `docs/deployment/` - Deployment guides
- `docs/guides/` - How-to guides
- `docs/project-management/` - Roadmaps and tracking

**For Infrastructure:**
- `infrastructure/docker/` - Container definitions
- `infrastructure/kubernetes/` - K8s manifests
- `infrastructure/helm/` - Helm charts

**For Configuration:**
- `config/environments/development/` - Dev settings
- `config/environments/staging/` - Staging settings
- `config/environments/production/` - Production settings

---

## 🔄 Import Path Changes

If you encounter import errors, update paths:

```python
# OLD IMPORTS
from src.lib.helpers import utility_function
from src.mcp.server import MCPServer

# NEW IMPORTS
from src.utils.helpers import utility_function
from src.integrations.mcp.server import MCPServer
```

---

## 🎯 What To Do First

1. **Pull latest changes:** `git pull origin master`
2. **Copy environment file:** `Copy-Item config/environments/development/.env.example .env`
3. **Start services:** `docker-compose -f config/environments/development/docker-compose.yml up -d`
4. **Verify it works:** Visit http://localhost:3000

---

## 📖 Need More Help?

- **Full reorganization details:** [REORGANIZATION_COMPLETE.md](REORGANIZATION_COMPLETE.md)
- **Documentation index:** [docs/README.md](docs/README.md)
- **Contributing guide:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Scripts guide:** [scripts/README.md](scripts/README.md)
- **Config guide:** [config/README.md](config/README.md)
- **Infrastructure guide:** [infrastructure/README.md](infrastructure/README.md)

---

**Pro Tip:** Bookmark this file for quick reference during the transition period!
