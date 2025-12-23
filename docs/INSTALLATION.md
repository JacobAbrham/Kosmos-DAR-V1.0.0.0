# KOSMOS Installation Guide

Complete installation instructions for the KOSMOS AI-Native Enterprise Operating System.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Quick Start (Docker Compose)](#quick-start-docker-compose)
- [Native Installation](#native-installation)
- [Kubernetes Installation](#kubernetes-installation)
- [Post-Installation](#post-installation)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum:**

- CPU: 4 cores
- RAM: 8GB
- Disk: 50GB free space
- OS: Linux, macOS, or Windows 10/11

**Recommended:**

- CPU: 8+ cores
- RAM: 32GB
- Disk: 200GB SSD
- OS: Ubuntu 22.04 LTS or similar

### Required Software

- **Docker Desktop 24.0+** (for containerized deployment)
- **Python 3.11+** (for native deployment)
- **Node.js 18+** (for frontend development)
- **Git 2.30+**

### Optional Software

- **kubectl 1.28+** (for Kubernetes deployment)
- **Helm 3.12+** (for Helm charts)
- **make** (for Makefile commands)

---

## Installation Methods

Choose the installation method that best fits your needs:

| Method | Best For | Time | Difficulty |
|--------|----------|------|------------|
| [Docker Compose](#quick-start-docker-compose) | Quick testing, development | 10 min | Easy |
| [Native](#native-installation) | Local development, customization | 20 min | Medium |
| [Kubernetes](#kubernetes-installation) | Production, scaling | 30 min | Advanced |

---

## Quick Start (Docker Compose)

The fastest way to get KOSMOS running.

### 1. Clone Repository

```bash
git clone https://github.com/JacobAbrham/Kosmos-DAR-V1.0.0.0.git
cd Kosmos-DAR-V1.0.0.0
```

### 2. Configure Environment

```bash
# Copy environment template
cp config/environments/development/.env.example .env

# Edit .env file with your settings (optional for development)
nano .env
```

**Key variables to configure:**

```env
# Database
POSTGRES_PASSWORD=your_secure_password

# API Keys (optional for development)
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 3. Start Services

```bash
# Start all services
docker-compose -f config/environments/development/docker-compose.yml up -d

# Or use the Makefile
make dev
```

### 4. Verify Installation

```bash
# Check service health
curl http://localhost:8000/health

# View logs
docker-compose -f config/environments/development/docker-compose.yml logs -f
```

### 5. Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| API Gateway | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| Frontend UI | http://localhost:3000 | - |
| MkDocs | http://localhost:8080 | - |
| MinIO Console | http://localhost:9001 | minioadmin / minioadmin |
| PostgreSQL | localhost:5432 | kosmos / (from .env) |

---

## Native Installation

For local development with more control.

### 1. System Setup

#### Ubuntu/Debian

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
```

#### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11

# Install Node.js
brew install node@18

# Install Docker Desktop
brew install --cask docker
```

#### Windows (PowerShell as Administrator)

```powershell
# Install Chocolatey (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Python
choco install python311 -y

# Install Node.js
choco install nodejs-lts -y

# Install Docker Desktop
choco install docker-desktop -y

# Install Git
choco install git -y
```

### 2. Clone and Setup

```bash
# Clone repository
git clone https://github.com/JacobAbrham/Kosmos-DAR-V1.0.0.0.git
cd Kosmos-DAR-V1.0.0.0

# Run setup script
make setup

# Or manual setup:
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Start Infrastructure

```bash
# Start only infrastructure services (PostgreSQL, Redis, MinIO, NATS)
docker-compose -f config/environments/development/docker-compose.yml up postgres redis minio nats -d
```

### 4. Initialize Database

```bash
# Run migrations
alembic upgrade head

# Or use the script
python scripts/database/init_db.py
```

### 5. Start Application

**Terminal 1 - API Backend:**

```bash
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend (optional):**

```bash
cd frontend
npm install
npm run dev
```

**Terminal 3 - Documentation (optional):**

```bash
cd docs
mkdocs serve
```

---

## Kubernetes Installation

For production deployments.

### Prerequisites

- Kubernetes cluster (1.28+)
- kubectl configured
- Helm 3.12+
- Storage class with dynamic provisioning

### 1. Add Helm Repository

```bash
# Add KOSMOS Helm repo (if using private repo)
helm repo add kosmos https://charts.kosmos.internal
helm repo update
```

### 2. Create Namespace

```bash
kubectl create namespace kosmos-core
kubectl config set-context --current --namespace=kosmos-core
```

### 3. Configure Secrets

```bash
# Create secrets from environment file
kubectl create secret generic kosmos-secrets \
  --from-env-file=config/environments/production/.env

# Or use individual secrets
kubectl create secret generic postgres-secret \
  --from-literal=password=your_secure_password

kubectl create secret generic api-keys \
  --from-literal=openai-api-key=sk-your-key \
  --from-literal=anthropic-api-key=sk-ant-your-key
```

### 4. Install with Helm

```bash
# Install KOSMOS
helm install kosmos infrastructure/helm/kosmos \
  --namespace kosmos-core \
  --values infrastructure/helm/kosmos/values-production.yaml \
  --wait --timeout 10m

# Or use Kustomize
kubectl apply -k infrastructure/kubernetes/overlays/production
```

### 5. Verify Installation

```bash
# Check pods
kubectl get pods -n kosmos-core

# Check services
kubectl get svc -n kosmos-core

# Check ingress
kubectl get ingress -n kosmos-core
```

### 6. Access Services

```bash
# Port forward for testing
kubectl port-forward -n kosmos-core svc/kosmos-api 8000:80

# Or access via ingress (production)
curl https://api.kosmos.yourdomain.com/health
```

---

## Post-Installation

### 1. Verify Installation

```bash
# Run smoke tests
make test-smoke

# Or manual verification
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

### 2. Create Admin User

```bash
# Using the API
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourdomain.com",
    "password": "your_secure_password",
    "full_name": "Admin User"
  }'
```

### 3. Configure Authentication

See [Security Configuration](security/iam.md) for details on:

- Setting up Zitadel
- Configuring OAuth providers
- Managing API keys
- Setting up MFA

### 4. Load Sample Data (Optional)

```bash
# Load demo agents
python scripts/database/seed_data.py

# Import sample documents
python scripts/utilities/import_documents.py --path ./sample-data
```

### 5. Configure Monitoring

```bash
# Deploy monitoring stack
kubectl apply -k infrastructure/monitoring/overlays/development

# Access Grafana
kubectl port-forward -n monitoring svc/grafana 3000:80
```

---

## Troubleshooting

### Common Issues

#### Docker Services Won't Start

```bash
# Check Docker is running
docker ps

# Check logs
docker-compose -f config/environments/development/docker-compose.yml logs

# Restart services
docker-compose -f config/environments/development/docker-compose.yml restart
```

#### Database Connection Errors

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Test connection
docker exec -it kosmos-postgres psql -U kosmos -d kosmos -c "SELECT 1;"

# Reset database
docker-compose -f config/environments/development/docker-compose.yml down -v
docker-compose -f config/environments/development/docker-compose.yml up -d
```

#### Port Conflicts

```bash
# Check what's using ports
lsof -i :8000  # API port
lsof -i :3000  # Frontend port
lsof -i :5432  # PostgreSQL port

# Stop conflicting services or change ports in .env
```

#### Permission Errors (Linux)

```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Fix file permissions
sudo chown -R $USER:$USER .
```

### Getting Help

- **Documentation:** [docs/README.md](README.md)
- **GitHub Issues:** https://github.com/JacobAbrham/Kosmos-DAR-V1.0.0.0/issues
- **Deployment Guide:** [docs/deployment/DEPLOYMENT_SUMMARY.md](deployment/DEPLOYMENT_SUMMARY.md)
- **Development Guide:** [docs/guides/DEVELOPMENT_ENVIRONMENT_GUIDE.md](guides/DEVELOPMENT_ENVIRONMENT_GUIDE.md)

---

## Next Steps

After installation:

1. ✅ **Configure Agents** - See [Agent Documentation](02-architecture/agents/README.md)
2. ✅ **Set Up MCP Servers** - See [MCP Integration Guide](developer-guide/mcp-integration/README.md)
3. ✅ **Configure Security** - See [Security Guide](security/iam.md)
4. ✅ **Deploy to Production** - See [Deployment Summary](deployment/DEPLOYMENT_SUMMARY.md)

---

**Last Updated:** December 2025  
**Version:** 1.0.0
