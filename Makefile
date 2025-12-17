# KOSMOS Makefile
# Common commands for development, testing, and deployment

.PHONY: help setup dev build test clean deploy

# Default target
.DEFAULT_GOAL := help

DOCKER_COMPOSE ?= docker compose

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ============================================================================
# Setup & Installation
# ============================================================================

setup: ## Initial project setup
	@echo "🔧 Setting up development environment..."
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	@if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi
	@echo "Installing pre-commit hooks..."
	pip install pre-commit
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "Setting up environment file..."
	@if [ ! -f .env ]; then cp .env.example .env 2>/dev/null || echo "No .env.example found"; fi
	@echo "✅ Setup complete! Run 'make dev' to start development environment"

install: setup ## Alias for setup

setup-frontend: ## Setup frontend dependencies
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ Frontend setup complete!"

# ============================================================================
# Development
# ============================================================================

dev: ## Start development environment
	@echo "🚀 Starting development environment..."
	$(DOCKER_COMPOSE) up -d
	@echo ""
	@echo "✅ Development environment started!"
	@echo "   🌐 API: http://localhost:8000"
	@echo "   🎨 Frontend: http://localhost:3000"
	@echo "   📚 Docs: http://localhost:8080"
	@echo "   💾 PostgreSQL: localhost:5432"
	@echo "   🔴 Redis: localhost:6379"
	@echo ""
	@echo "Run 'make dev-logs' to view logs"
	@echo "Run 'make dev-stop' to stop all services"

dev-stop: ## Stop development environment
	@echo "🛑 Stopping development environment..."
	$(DOCKER_COMPOSE) down
	@echo "✅ Development environment stopped"

dev-clean: ## Stop and remove all containers, volumes, and networks
	@echo "🗑️  Cleaning development environment..."
	$(DOCKER_COMPOSE) down -v --remove-orphans
	@echo "✅ Development environment cleaned"

dev-logs: ## Show development logs
	$(DOCKER_COMPOSE) logs -f

dev-restart: ## Restart development environment
	@echo "🔄 Restarting development environment..."
	$(DOCKER_COMPOSE) restart
	@echo "✅ Restarted"

dev-ps: ## Show running containers
	$(DOCKER_COMPOSE) ps

# ============================================================================
# Building
# ============================================================================

build: ## Build all containers
	@echo "🏗️  Building all containers..."
	$(DOCKER_COMPOSE) build
	@echo "✅ Build complete"

build-backend: ## Build backend container only
	@echo "🏗️  Building backend container..."
	docker build -t kosmos/api:dev -f docker/backend/Dockerfile .
	@echo "✅ Backend built"

build-frontend: ## Build frontend container only
	@echo "🏗️  Building frontend container..."
	docker build -t kosmos/frontend:dev -f docker/frontend/Dockerfile ./frontend
	@echo "✅ Frontend built"

build-prod: ## Build production containers
	@echo "🏗️  Building production containers..."
	docker build -t kosmos/api:latest -f docker/backend/Dockerfile .
	docker build -t kosmos/frontend:latest -f docker/frontend/Dockerfile ./frontend
	@echo "✅ Production builds complete"

# ============================================================================
# Testing
# ============================================================================

test: ## Run all tests
	@echo "🧪 Running all tests..."
	pytest tests/ -v --tb=short

test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	pytest tests/unit -v

test-integration: ## Run integration tests
	@echo "🧪 Running integration tests..."
	pytest tests/integration -v

test-e2e: ## Run end-to-end tests
	@echo "🧪 Running E2E tests..."
	npx playwright test

test-coverage: ## Generate coverage report
	@echo "📊 Generating coverage report..."
	pytest tests/ --cov=src --cov-report=html --cov-report=term
	@echo "✅ Coverage report generated: htmlcov/index.html"

test-watch: ## Run tests in watch mode
	@echo "👀 Running tests in watch mode..."
	pytest-watch tests/

test-mcp: ## Run MCP integration tests
	@echo "🧪 Running MCP tests..."
	node tests/test_memory_server.js
	node tests/test_sequential_thinking.js
	node tests/test_context7.js

# ============================================================================
# Code Quality
# ============================================================================

lint: ## Run all linters
	@echo "🔍 Running linters..."
	@echo "  → Python (ruff)"
	ruff check src/ tests/
	@echo "  → Python (mypy)"
	mypy src/
	@echo "  → Python (black)"
	black --check src/ tests/
	@if [ -d frontend ]; then \
		echo "  → TypeScript/JavaScript"; \
		cd frontend && npm run lint; \
	fi
	@echo "✅ All linters passed"

format: ## Format code
	@echo "✨ Formatting code..."
	black src/ tests/
	ruff check --fix src/ tests/
	@if [ -d frontend ]; then \
		cd frontend && npm run format; \
	fi
	@echo "✅ Code formatted"

lint-fix: format ## Alias for format

type-check: ## Run type checking
	@echo "🔍 Running type checker..."
	mypy src/
	@if [ -d frontend ]; then \
		cd frontend && npm run type-check; \
	fi

pre-commit: ## Run pre-commit on all files
	@echo "🔍 Running pre-commit checks..."
	pre-commit run --all-files

# ============================================================================
# Database
# ============================================================================

db-migrate: ## Run database migrations
	@echo "🗄️  Running database migrations..."
	alembic upgrade head
	@echo "✅ Migrations complete"

db-rollback: ## Rollback last migration
	@echo "⏪ Rolling back last migration..."
	alembic downgrade -1
	@echo "✅ Rollback complete"

db-reset: ## Reset database (WARNING: deletes all data)
	@echo "⚠️  WARNING: This will delete all database data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "🗑️  Resetting database..."; \
		$(DOCKER_COMPOSE) down -v; \
		$(DOCKER_COMPOSE) up -d postgres; \
		sleep 5; \
		alembic upgrade head; \
		echo "✅ Database reset complete"; \
	fi

db-seed: ## Seed database with test data
	@echo "🌱 Seeding database..."
	python scripts/seed_database.py
	@echo "✅ Database seeded"

db-shell: ## Open PostgreSQL shell
	$(DOCKER_COMPOSE) exec postgres psql -U kosmos -d kosmos_dev

db-backup: ## Backup database
	@echo "💾 Backing up database..."
	@mkdir -p backups
	$(DOCKER_COMPOSE) exec -T postgres pg_dump -U kosmos kosmos_dev > backups/backup-$$(date +%Y%m%d-%H%M%S).sql
	@echo "✅ Backup saved to backups/"

db-restore: ## Restore database from latest backup
	@echo "📥 Restoring database from latest backup..."
	@latest=$$(ls -t backups/*.sql | head -1); \
	if [ -z "$$latest" ]; then \
		echo "❌ No backups found"; \
		exit 1; \
	fi; \
	echo "Restoring from $$latest"; \
	cat $$latest | $(DOCKER_COMPOSE) exec -T postgres psql -U kosmos kosmos_dev
	@echo "✅ Database restored"

# ============================================================================
# Documentation
# ============================================================================

docs-serve: ## Serve documentation locally
	@echo "📚 Starting documentation server..."
	mkdocs serve
	@echo "✅ Docs available at http://localhost:8000"

docs-build: ## Build documentation
	@echo "📚 Building documentation..."
	mkdocs build --strict
	@echo "✅ Documentation built to site/"

docs-deploy: ## Deploy documentation to Cloudflare Pages
	@echo "🚀 Deploying documentation..."
	mkdocs build --strict
	@echo "✅ Documentation ready for deployment"

# ============================================================================
# Deployment
# ============================================================================

deploy-staging: ## Deploy to staging environment
	@echo "🚀 Deploying to staging..."
	@echo "Building images..."
	docker build -t ghcr.io/nuvanta-holding/kosmos:staging .
	@echo "Deploying with Helm..."
	helm upgrade --install kosmos ./helm/kosmos \
		-f helm/kosmos/values-staging.yaml \
		--set image.tag=staging \
		-n kosmos-staging \
		--create-namespace \
		--wait --timeout 10m
	@echo "✅ Deployed to staging"
	@echo "   🌐 URL: https://staging.kosmos.internal"

deploy-prod: ## Deploy to production (requires confirmation)
	@echo "⚠️  DEPLOYING TO PRODUCTION"
	@echo "This will deploy to the live production environment."
	@read -p "Are you sure? Type 'yes' to continue: " -r; \
	echo; \
	if [[ $$REPLY == "yes" ]]; then \
		echo "🚀 Deploying to production..."; \
		helm upgrade --install kosmos ./helm/kosmos \
			-f helm/kosmos/values-production.yaml \
			--set image.tag=$$(git rev-parse --short HEAD) \
			-n kosmos-production \
			--create-namespace \
			--wait --timeout 15m; \
		echo "✅ Deployed to production"; \
		echo "   🌐 URL: https://kosmos.nuvanta.cloud"; \
	else \
		echo "❌ Deployment cancelled"; \
	fi

rollback-staging: ## Rollback staging deployment
	@echo "⏪ Rolling back staging deployment..."
	helm rollback kosmos -n kosmos-staging
	@echo "✅ Rollback complete"

rollback-prod: ## Rollback production deployment
	@echo "⚠️  WARNING: Rolling back production!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		helm rollback kosmos -n kosmos-production; \
		echo "✅ Production rollback complete"; \
	fi

# ============================================================================
# Validation & Security
# ============================================================================

validate: ## Validate all configuration files
	@echo "✅ Validating configuration files..."
	python scripts/validate_all.py
	@echo "✅ Validation complete"

security-scan: ## Run security scans
	@echo "🔒 Running security scans..."
	@echo "  → Bandit (Python)"
	bandit -r src/ -f screen
	@echo "  → Safety (Dependencies)"
	safety check --json || true
	@echo "  → Trivy (Filesystem)"
	trivy fs . --severity HIGH,CRITICAL
	@echo "✅ Security scan complete"

secrets-scan: ## Scan for secrets in code
	@echo "🔐 Scanning for secrets..."
	gitleaks detect --source . --verbose
	@echo "✅ Secrets scan complete"

# ============================================================================
# Dependencies
# ============================================================================

update-deps: ## Update dependencies
	@echo "📦 Updating dependencies..."
	pip-compile --upgrade requirements.in -o requirements.txt || pip list --outdated
	@if [ -d frontend ]; then \
		cd frontend && npm update; \
	fi
	@echo "✅ Dependencies updated"

install-deps: ## Install/update all dependencies
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi
	@if [ -d frontend ]; then \
		cd frontend && npm install; \
	fi
	@echo "✅ Dependencies installed"

check-deps: ## Check for outdated dependencies
	@echo "🔍 Checking for outdated dependencies..."
	@echo "Python:"
	pip list --outdated
	@if [ -d frontend ]; then \
		echo "Node.js:"; \
		cd frontend && npm outdated; \
	fi

# ============================================================================
# Cleanup
# ============================================================================

clean: ## Clean up generated files
	@echo "🧹 Cleaning up..."
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"

clean-all: clean dev-clean ## Clean everything including Docker volumes
	@echo "🗑️  Deep cleaning..."
	docker system prune -af --volumes
	@echo "✅ All cleaned"

# ============================================================================
# Monitoring & Logs
# ============================================================================

logs-api: ## Show API logs
	$(DOCKER_COMPOSE) logs -f api

logs-frontend: ## Show frontend logs
	$(DOCKER_COMPOSE) logs -f frontend

logs-db: ## Show database logs
	$(DOCKER_COMPOSE) logs -f postgres

logs-all: dev-logs ## Show all logs

health-check: ## Check health of all services
	@echo "🏥 Checking service health..."
	@curl -s http://localhost:8000/health | jq . || echo "API not responding"
	@curl -s http://localhost:3000 > /dev/null && echo "Frontend: ✅" || echo "Frontend: ❌"
	@$(DOCKER_COMPOSE) exec postgres pg_isready && echo "Database: ✅" || echo "Database: ❌"

# ============================================================================
# CI/CD Helpers
# ============================================================================

ci-test: ## Run tests in CI mode
	@echo "🤖 Running tests in CI mode..."
	pytest tests/ -v --cov=src --cov-report=xml --junitxml=junit.xml

ci-build: ## Build for CI
	@echo "🤖 Building for CI..."
	docker build -t kosmos/api:ci -f docker/backend/Dockerfile .

ci-lint: ## Run linters in CI mode
	@echo "🤖 Running linters in CI mode..."
	ruff check src/ tests/ --output-format=github
	mypy src/ --junit-xml=mypy.xml

# ============================================================================
# Development Tools
# ============================================================================

shell: ## Open Python shell with app context
	@echo "🐍 Opening Python shell..."
	python -i -c "from src import *; print('KOSMOS shell loaded')"

shell-db: db-shell ## Alias for db-shell

psql: db-shell ## Alias for db-shell

redis-cli: ## Open Redis CLI
	$(DOCKER_COMPOSE) exec redis redis-cli

minio-browser: ## Open MinIO browser
	@echo "🗂️  MinIO Console: http://localhost:9001"
	@echo "   Username: minioadmin"
	@echo "   Password: minioadmin"

# ============================================================================
# Version & Release
# ============================================================================

version: ## Show current version
	@echo "KOSMOS v1.0.0"
	@git describe --tags --always 2>/dev/null || echo "No git tags"

release: ## Create a new release (requires VERSION=x.y.z)
	@if [ -z "$(VERSION)" ]; then \
		echo "❌ Please specify VERSION=x.y.z"; \
		exit 1; \
	fi
	@echo "📦 Creating release $(VERSION)..."
	git tag -a v$(VERSION) -m "Release v$(VERSION)"
	git push origin v$(VERSION)
	@echo "✅ Release v$(VERSION) created"

# ============================================================================

.PHONY: $(MAKECMDGOALS)
