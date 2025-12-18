# ✅ Post-Reorganization Checklist

**Date:** December 18, 2025  
**Status:** Ready for Team Adoption

Use this checklist to ensure smooth transition to the new repository structure.

---

## 🔄 For All Team Members

### Immediate Actions (Do Today)

- [ ] **Pull latest changes**
  ```bash
  git pull origin master
  ```

- [ ] **Read migration guide**
  - [ ] Review [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
  - [ ] Bookmark [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

- [ ] **Update Docker Compose commands**
  ```bash
  # Old: docker-compose up
  # New: docker-compose -f config/environments/development/docker-compose.yml up
  ```

- [ ] **Create PowerShell alias (recommended)**
  ```powershell
  # Add to profile: $PROFILE
  function dc { docker-compose -f config/environments/development/docker-compose.yml @args }
  ```

- [ ] **Verify local environment works**
  - [ ] Copy new .env: `cp config/environments/development/.env.example .env`
  - [ ] Start services: `docker-compose -f config/environments/development/docker-compose.yml up`
  - [ ] Test frontend: http://localhost:3000
  - [ ] Test API: http://localhost:8000/docs

### Within This Week

- [ ] **Update any local scripts** that reference old paths
  - [ ] Check for hardcoded paths to `docker-compose.yml`
  - [ ] Update script paths (`scripts/run_api.ps1` → `scripts/development/run_api.ps1`)

- [ ] **Review import changes** in your working branches
  - [ ] Change `from src.lib` → `from src.utils`
  - [ ] Change `from src.mcp` → `from src.integrations.mcp`

- [ ] **Update bookmarks/shortcuts** to documentation
  - [ ] Roadmap: `docs/project-management/IMPLEMENTATION_ROADMAP.md`
  - [ ] Deployment: `docs/deployment/DEPLOYMENT_SUMMARY.md`
  - [ ] Gap Analysis: `docs/assessments/COMPREHENSIVE_GAP_ANALYSIS.md`

---

## 🔧 For DevOps/Infrastructure Team

### Configuration Updates

- [ ] **Create staging database**
  ```sql
  CREATE DATABASE kosmos_staging;
  GRANT ALL PRIVILEGES ON DATABASE kosmos_staging TO kosmos;
  \c kosmos_staging
  \i database/schemas/001_initial_schema.sql
  ```

- [ ] **Create production database**
  ```sql
  CREATE DATABASE kosmos_prod;
  GRANT ALL PRIVILEGES ON DATABASE kosmos_prod TO kosmos;
  \c kosmos_prod
  \i database/schemas/001_initial_schema.sql
  ```

- [ ] **Update GitHub Secrets**
  - [ ] Verify `KUBE_CONFIG_STAGING` exists
  - [ ] Verify `KUBE_CONFIG_PRODUCTION` exists
  - [ ] Update any secrets referencing old paths

- [ ] **Test CI/CD pipelines**
  - [ ] Verify `01-validate.yml` runs
  - [ ] Verify `02-test-unit.yml` runs
  - [ ] Verify `03-test-integration.yml` runs
  - [ ] Verify `04-test-e2e.yml` runs
  - [ ] Verify `05-security.yml` runs
  - [ ] Test staging deployment workflow
  - [ ] Test production deployment workflow (dry run)

- [ ] **Update deployment documentation**
  - [ ] Verify Helm values paths in `infrastructure/helm/`
  - [ ] Update any deployment runbooks
  - [ ] Test Kustomize overlays (if implemented)

### Infrastructure Verification

- [ ] **Verify Docker builds**
  ```bash
  docker build -f infrastructure/docker/backend/Dockerfile .
  docker build -f infrastructure/docker/frontend/Dockerfile .
  ```

- [ ] **Verify Helm charts**
  ```bash
  helm lint infrastructure/helm/kosmos
  helm template infrastructure/helm/kosmos -f infrastructure/helm/kosmos/values-staging.yaml
  ```

- [ ] **Verify monitoring configs**
  - [ ] Prometheus alerts: `infrastructure/monitoring/prometheus/alerts/`
  - [ ] Grafana dashboards: `infrastructure/monitoring/grafana/dashboards/`

---

## 👨‍💻 For Backend Developers

### Code Updates

- [ ] **Update import statements** in active branches
  ```python
  # Before
  from src.lib.helpers import function
  from src.mcp.server import MCPServer
  
  # After
  from src.utils.helpers import function
  from src.integrations.mcp.server import MCPServer
  ```

- [ ] **Review new directories**
  - [ ] `src/models/` - Place database models here
  - [ ] `src/services/` - Place business logic here
  - [ ] `src/api/routes/` - Organize API routes here
  - [ ] `src/api/middleware/` - Custom middleware here

- [ ] **Test database setup**
  ```bash
  # Apply schema
  psql -U kosmos -d kosmos_dev -f database/schemas/001_initial_schema.sql
  
  # Or use Alembic
  cd database
  alembic upgrade head
  ```

- [ ] **Run integration tests**
  ```bash
  pytest tests/integration/ -v
  ```

---

## 🎨 For Frontend Developers

### Updates Required

- [ ] **Verify frontend still works**
  ```bash
  cd frontend
  npm install
  npm run dev
  ```

- [ ] **Update any hardcoded paths** in frontend code
  - [ ] API endpoint references
  - [ ] Asset paths

- [ ] **Run E2E tests**
  ```bash
  cd frontend
  npx playwright test
  ```

- [ ] **Review centralized E2E tests**
  - [ ] Tests copied to `tests/e2e/`
  - [ ] Original location: `frontend/tests/e2e/` (still exists)

---

## 📝 For Documentation Team

### Documentation Tasks

- [ ] **Review all new README files**
  - [ ] `docs/README.md`
  - [ ] `config/README.md`
  - [ ] `infrastructure/README.md`
  - [ ] `scripts/README.md`
  - [ ] `database/schemas/README.md`
  - [ ] `database/docs/README.md`

- [ ] **Update external documentation** (if any)
  - [ ] Wiki pages
  - [ ] Confluence pages
  - [ ] Training materials
  - [ ] Onboarding docs

- [ ] **Verify MkDocs builds**
  ```bash
  cd docs
  mkdocs serve
  # Visit http://localhost:8000
  ```

- [ ] **Update architecture diagrams** (if needed)
  - [ ] Reflect new directory structure
  - [ ] Update C4 diagrams

---

## 🧪 For QA Team

### Testing Checklist

- [ ] **Environment setup**
  - [ ] Development environment
  - [ ] Staging environment
  - [ ] Test environment

- [ ] **Run full test suite**
  ```bash
  # Integration tests
  pytest tests/integration/ -v
  
  # E2E tests
  cd frontend && npx playwright test
  
  # Unit tests
  pytest tests/unit/ -v
  ```

- [ ] **Verify test fixtures**
  - [ ] Check `tests/fixtures/` directory
  - [ ] Verify test data loads correctly

- [ ] **Update test documentation**
  - [ ] Review `docs/assessments/TEST_COVERAGE.md`
  - [ ] Update test plans with new paths

---

## 🔒 For Security Team

### Security Review

- [ ] **Review .gitignore changes**
  - [ ] Verify `config/secrets/*` is ignored
  - [ ] Verify `*.secret.*` pattern works
  - [ ] Check certificate files are ignored

- [ ] **Review CODEOWNERS**
  - [ ] Verify team assignments
  - [ ] Test code review automation

- [ ] **Audit secret management**
  - [ ] Ensure no secrets in git history
  - [ ] Verify Infisical integration
  - [ ] Review GitHub Secrets usage

- [ ] **Test security workflows**
  - [ ] Run `05-security.yml` workflow
  - [ ] Verify Trivy scans
  - [ ] Check dependency scanning

---

## 📊 Project Manager Checklist

### Team Coordination

- [ ] **Announce reorganization** to team
  - [ ] Send email with key changes
  - [ ] Schedule team sync if needed
  - [ ] Share this checklist

- [ ] **Track adoption**
  - [ ] Monitor team questions
  - [ ] Document common issues
  - [ ] Update FAQ as needed

- [ ] **Verify milestones**
  - [ ] All team members pulled changes
  - [ ] All environments working
  - [ ] No blockers reported

### Documentation

- [ ] **Update project board**
  - [ ] Close reorganization tasks
  - [ ] Create follow-up tasks if needed

- [ ] **Update sprint planning**
  - [ ] Account for transition time
  - [ ] Plan database creation tasks

---

## 🎯 Success Criteria

Mark complete when ALL of these are true:

- [ ] All team members have pulled latest changes
- [ ] Development environment works for everyone
- [ ] Staging database created and initialized
- [ ] Production database created (when ready)
- [ ] All CI/CD workflows passing
- [ ] No critical issues reported
- [ ] Team familiar with new structure
- [ ] Documentation up to date

---

## 📞 Need Help?

**Resources:**
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Transition guide
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick lookup
- [REORGANIZATION_COMPLETE.md](REORGANIZATION_COMPLETE.md) - Full details
- [docs/README.md](docs/README.md) - Documentation index

**Contact:**
- DevOps Team: For infrastructure issues
- Backend Team: For import/code issues
- Frontend Team: For UI/build issues
- Team Lead: For process questions

---

**Last Updated:** December 18, 2025  
**Status:** ✅ All items ready for team adoption
