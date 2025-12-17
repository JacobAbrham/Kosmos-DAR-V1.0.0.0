# Development Environment Setup

**Document Type:** Developer Guide  
**Owner:** Engineering Team  
**Last Updated:** 2025-12-13  
**Status:** 🟢 Active

---

## Overview

This guide provides comprehensive instructions for setting up a local KOSMOS development environment. Whether you're using GitHub Codespaces or a local machine, this guide covers all prerequisites, configuration, and verification steps.

---

## Quick Start Options

| Method | Setup Time | Best For |
|--------|------------|----------|
| [GitHub Codespaces](#github-codespaces) | 5 minutes | Quick start, no local setup |
| [Local Development](#local-development) | 30 minutes | Full control, offline work |
| [Docker Compose](#docker-compose-development) | 15 minutes | Consistent environment |

---

## System Requirements

### Minimum Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 4 cores | 8 cores |
| RAM | 8 GB | 16 GB |
| Disk | 20 GB free | 50 GB SSD |
| OS | Windows 10/11, macOS 12+, Ubuntu 22.04+ | Ubuntu 22.04 LTS |

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Git | 2.30+ | Version control |
| Python | 3.10+ | Agent services |
| Node.js | 18+ | MCP servers, frontend |
| Docker | 24+ | Service containers |
| Docker Compose | 2.20+ | Local orchestration |

---

## GitHub Codespaces

### Creating a Codespace

1. Navigate to the repository: `https://github.com/Nuvanta-Holding/kosmos`

2. Click **Code** → **Codespaces** → **Create codespace on main**

3. Wait for environment initialization (~3-5 minutes)

4. Verify the environment:
   ```bash
   # Check Python
   python --version  # Should be 3.10+
   
   # Check Node.js
   node --version    # Should be 18+
   
   # Check Docker
   docker --version  # Should be 24+
   ```

### Codespace Configuration

The repository includes `.devcontainer/devcontainer.json`:

```json
{
  "name": "KOSMOS Development",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "features": {
    "ghcr.io/devcontainers/features/node:1": {"version": "18"},
    "ghcr.io/devcontainers/features/docker-in-docker:2": {}
  },
  "postCreateCommand": "pip install -r requirements.txt && npm install",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "dbaeumer.vscode-eslint"
      ]
    }
  },
  "forwardPorts": [8000, 5432, 6379, 4222]
}
```

---

## Local Development

### Step 1: Install Prerequisites

#### Ubuntu/Debian
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Node.js (via nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt install docker-compose-plugin -y
```


#### Windows (WSL2)
```powershell
# Install WSL2 (PowerShell as Admin)
wsl --install -d Ubuntu-22.04

# After restart, configure WSL memory (create/edit .wslconfig)
# Location: C:\Users\<username>\.wslconfig
```

```ini
# .wslconfig
[wsl2]
memory=8GB
processors=4
swap=4GB
```

```bash
# Inside WSL2, follow Ubuntu instructions above
```

#### macOS
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install prerequisites
brew install python@3.11 node@18 docker docker-compose

# Start Docker Desktop
open -a Docker
```

### Step 2: Clone Repository

```bash
# Clone the repository
git clone https://github.com/Nuvanta-Holding/kosmos.git
cd kosmos

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# or: .\venv\Scripts\activate  # Windows

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies (for MCP servers)
npm install
```

### Step 3: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit environment variables
nano .env  # or your preferred editor
```

**Required Environment Variables:**

```bash
# .env file
# ============================
# Core Configuration
# ============================
KOSMOS_ENV=development
KOSMOS_DEBUG=true
KOSMOS_LOG_LEVEL=DEBUG

# ============================
# Database Configuration
# ============================
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=kosmos
POSTGRES_USER=kosmos
POSTGRES_PASSWORD=development_password

# ============================
# Cache Configuration
# ============================
DRAGONFLY_HOST=localhost
DRAGONFLY_PORT=6379

# ============================
# Message Queue
# ============================
NATS_URL=nats://localhost:4222

# ============================
# Object Storage
# ============================
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# ============================
# LLM Configuration
# ============================
HUGGINGFACE_API_KEY=your_api_key_here
LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.3

# ============================
# Observability
# ============================
LANGFUSE_PUBLIC_KEY=your_key_here
LANGFUSE_SECRET_KEY=your_secret_here
LANGFUSE_HOST=https://cloud.langfuse.com
```

### Step 4: Start Infrastructure Services

```bash
# Start all required services
docker compose up -d

# Verify services are running
docker compose ps

# Expected output:
# NAME                STATUS
# kosmos-postgres     running (healthy)
# kosmos-dragonfly    running (healthy)
# kosmos-nats         running (healthy)
# kosmos-minio        running (healthy)
```

---

## Docker Compose Development

### docker-compose.yml Overview

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: kosmos-postgres
    environment:
      POSTGRES_DB: kosmos
      POSTGRES_USER: kosmos
      POSTGRES_PASSWORD: development_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U kosmos"]
      interval: 5s
      timeout: 5s
      retries: 5

  dragonfly:
    image: docker.dragonflydb.io/dragonflydb/dragonfly
    container_name: kosmos-dragonfly
    ports:
      - "6379:6379"
    ulimits:
      memlock: -1
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  nats:
    image: nats:2.10-alpine
    container_name: kosmos-nats
    ports:
      - "4222:4222"
      - "8222:8222"
    command: ["--jetstream", "--http_port", "8222"]
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:8222/healthz"]
      interval: 5s
      timeout: 5s
      retries: 5

  minio:
    image: minio/minio
    container_name: kosmos-minio
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data
    healthcheck:
      test: ["CMD", "mc", "ready", "local"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  minio_data:
```


---

## Database Initialization

### Initialize Schema

```bash
# Run database migrations
python scripts/migrate.py up

# Verify tables exist
docker exec -it kosmos-postgres psql -U kosmos -c "\dt"
```

### Enable pgvector Extension

```sql
-- Run via psql or migration
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

---

## Running the Application

### Start Agent Services

```bash
# Activate virtual environment
source venv/bin/activate

# Start Zeus orchestrator (development mode)
python -m kosmos.agents.zeus --reload

# In another terminal, start other agents as needed
python -m kosmos.agents.athena --reload
```

### Start MCP Servers

```bash
# Start Context7 MCP server
npx -y @anthropic/context7-mcp

# Start Memory server
npx -y @anthropic/memory-mcp

# Start Sequential Thinking server
npx -y @anthropic/sequential-thinking-mcp
```

---

## Verification Checklist

### Service Health Checks

```bash
# PostgreSQL
docker exec kosmos-postgres pg_isready -U kosmos
# Expected: localhost:5432 - accepting connections

# Dragonfly (Redis-compatible)
docker exec kosmos-dragonfly redis-cli ping
# Expected: PONG

# NATS
curl http://localhost:8222/healthz
# Expected: {"status":"ok"}

# MinIO
curl http://localhost:9000/minio/health/live
# Expected: HTTP 200
```

### Application Health

```bash
# Start health check endpoint
curl http://localhost:8000/health
# Expected: {"status": "healthy", "services": {...}}

# Test agent availability
curl http://localhost:8000/api/v1/agents
# Expected: List of available agents
```

### Full System Test

```bash
# Run integration tests
pytest tests/integration/ -v

# Run specific test
pytest tests/integration/test_zeus_routing.py -v
```

---

## Troubleshooting

### Common Issues

#### Docker Services Won't Start

```bash
# Check Docker daemon
docker info

# View service logs
docker compose logs postgres
docker compose logs dragonfly

# Reset and restart
docker compose down -v
docker compose up -d
```

#### Python Import Errors

```bash
# Ensure virtual environment is active
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Database Connection Refused

```bash
# Check if PostgreSQL is running
docker compose ps postgres

# Check PostgreSQL logs
docker compose logs postgres

# Verify connection
docker exec -it kosmos-postgres psql -U kosmos -c "SELECT 1"
```

#### MCP Server Connection Issues

```bash
# Check if MCP server is running
ps aux | grep mcp

# Test MCP server directly
npx -y @anthropic/context7-mcp --test

# Check MCP configuration
cat mcp-config.json
```

#### Port Conflicts

```bash
# Find process using port
lsof -i :5432  # Linux/macOS
netstat -ano | findstr :5432  # Windows

# Kill conflicting process or use different ports
```

---

## IDE Configuration

### VS Code

**Recommended Extensions:**
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Docker (ms-azuretools.vscode-docker)
- GitLens (eamodio.gitlens)

**settings.json:**
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "editor.formatOnSave": true
}
```

### PyCharm

1. Open project folder
2. Configure Python interpreter → Add Local → Select `venv/bin/python`
3. Enable Docker integration
4. Configure database tool for PostgreSQL

---

## Next Steps

After setting up your environment:

1. Read the [Architecture Overview](../02-architecture/index.md)
2. Review [Agent Documentation](../02-architecture/agents/README.md)
3. Explore [MCP Integration](mcp-integration/README.md)
4. Run the test suite: `pytest tests/`

---

**Questions?** Open an issue or contact engineering@nuvanta-holding.com
