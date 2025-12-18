# 🔄 Migration Guide - Old to New Structure

**For developers transitioning to the reorganized repository**

## Quick Command Updates

### Docker Compose

**OLD:**
```bash
docker-compose up
docker-compose down
```

**NEW:**
```bash
docker-compose -f config/environments/development/docker-compose.yml up
docker-compose -f config/environments/development/docker-compose.yml down
```

**TIP:** Create an alias:
```powershell
# Add to your PowerShell profile
function dc { docker-compose -f config/environments/development/docker-compose.yml @args }

# Usage
dc up -d
dc logs -f
dc down
```

### Environment Setup

**OLD:**
```bash
cp .env.example .env
```

**NEW:**
```bash
cp config/environments/development/.env.example .env
```

### Scripts

**OLD:**
```bash
.\scripts\setup-local-docker.ps1
.\scripts\run_api.ps1
.\scripts\run_frontend.ps1
```

**NEW:**
```bash
.\scripts\setup\setup-local-docker.ps1
.\scripts\development\run_api.ps1
.\scripts\development\run_frontend.ps1
```

## Import Path Changes

### Python Imports

**OLD:**
```python
from src.lib.helpers import function
from src.mcp.server import MCPServer
```

**NEW:**
```python
from src.utils.helpers import function
from src.integrations.mcp.server import MCPServer
```

### Configuration Imports

**OLD:**
```python
from src.core.config import settings
```

**NEW:**
```python
# Same - no change
from src.core.config import settings
```

## File Location Changes

| Old Location | New Location |
|--------------|--------------|
| `.env.example` | `config/environments/development/.env.example` |
| `docker-compose.yml` | `config/environments/development/docker-compose.yml` |
| `IMPLEMENTATION_ROADMAP.md` | `docs/project-management/IMPLEMENTATION_ROADMAP.md` |
| `DEPLOYMENT_SUMMARY.md` | `docs/deployment/DEPLOYMENT_SUMMARY.md` |
| `TEST_COVERAGE.md` | `docs/assessments/TEST_COVERAGE.md` |
| `docker/` | `infrastructure/docker/` |
| `helm/` | `infrastructure/helm/` |
| `k8s/` | `infrastructure/kubernetes/raw-manifests/` |
| `monitoring/` | `infrastructure/monitoring/` |
| `src/lib/` | `src/utils/` |
| `src/mcp/` | `src/integrations/mcp/` |
| `scripts/setup-*.ps1` | `scripts/setup/` |
| `scripts/run_*.ps1` | `scripts/development/` |

## CI/CD Workflow Changes

Workflow files have been renamed with numeric prefixes:

| Old Name | New Name |
|----------|----------|
| `validate.yml` | `01-validate.yml` |
| `ci.yml` | `02-test-unit.yml` |
| `test-integration.yml` | `03-test-integration.yml` |
| `test-e2e.yml` | `04-test-e2e.yml` |
| `security.yml` | `05-security.yml` |
| `deploy-staging.yml` | `20-deploy-staging.yml` |
| `deploy-production.yml` | `21-deploy-production.yml` |

**No action needed** - GitHub Actions automatically uses the new names.

## Common Issues & Solutions

### Issue: "docker-compose.yml not found"

**Solution:**
```bash
# Use the new path
docker-compose -f config/environments/development/docker-compose.yml up
```

### Issue: "ModuleNotFoundError: No module named 'src.lib'"

**Solution:**
Update your imports:
```python
# Change this:
from src.lib.helpers import function

# To this:
from src.utils.helpers import function
```

### Issue: "Cannot find IMPLEMENTATION_ROADMAP.md"

**Solution:**
Check the new location:
```bash
# It's now at:
docs/project-management/IMPLEMENTATION_ROADMAP.md
```

### Issue: "Scripts not found"

**Solution:**
Scripts are now organized in subdirectories:
```bash
# Setup scripts
.\scripts\setup\setup-interactive.ps1

# Development scripts
.\scripts\development\run_api.ps1

# Utility scripts
.\scripts\utilities\generate_c4.py
```

## Database Changes

### New Database Names

- **Development:** `kosmos_dev` (no change)
- **Staging:** `kosmos_staging` (NEW - create this)
- **Production:** `kosmos_prod` (NEW - create this)

### Create Staging Database

```sql
CREATE DATABASE kosmos_staging;
GRANT ALL PRIVILEGES ON DATABASE kosmos_staging TO kosmos;
```

### Create Production Database

```sql
CREATE DATABASE kosmos_prod;
GRANT ALL PRIVILEGES ON DATABASE kosmos_prod TO kosmos;
```

## Testing Your Setup

After migration, verify everything works:

```bash
# 1. Check environment config
cat config/environments/development/.env.example

# 2. Start services
docker-compose -f config/environments/development/docker-compose.yml up -d

# 3. Check services are running
docker-compose -f config/environments/development/docker-compose.yml ps

# 4. Run tests
pytest tests/integration/

# 5. Access services
# Frontend: http://localhost:3000
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## Updating Your Local Repository

```bash
# Pull latest changes
git pull origin master

# Clean up old paths (if safe)
# Review changes first!
git status

# Commit your local adaptations
git add .
git commit -m "chore: adapt to new repository structure"
```

## Getting Help

- **Quick Reference:** See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Full Details:** See [REORGANIZATION_COMPLETE.md](REORGANIZATION_COMPLETE.md)
- **Documentation:** See [docs/README.md](docs/README.md)

## Rollback (Emergency Only)

If you need to temporarily rollback:

```bash
# This is not recommended - contact the team instead
git checkout <previous-commit-hash>
```

Better approach: Report issues so we can fix them for everyone!
