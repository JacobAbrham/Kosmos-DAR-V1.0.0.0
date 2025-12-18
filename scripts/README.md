# KOSMOS Scripts

This directory contains scripts for development, deployment, and utilities.

## Directory Structure

### 📁 setup/
One-time setup scripts for different development environments:
- `setup-interactive.ps1` - Interactive menu for choosing setup option
- `setup-local-docker.ps1` - Local Docker Compose development
- `setup-codespaces.ps1` - GitHub Codespaces setup
- `setup-remote-server.ps1` - Remote server development
- `setup-k8s-dev.ps1` - Kubernetes development environment

### 📁 development/
Daily development helper scripts:
- `run_api.ps1` - Start the FastAPI backend
- `run_frontend.ps1` - Start the Next.js frontend
- Scripts for database reset, testing, etc.

### 📁 deployment/
Deployment and build scripts:
- Docker image building
- Kubernetes deployment helpers
- Health check scripts

### 📁 utilities/
Miscellaneous utility scripts:
- `generate_c4.py` - Generate C4 architecture diagrams
- `extract_metrics.py` - Extract metrics from logs
- `check_yaml_files.py` - Validate YAML configuration

## Quick Start

**First time setup:**
```powershell
.\setup\setup-interactive.ps1
```

**Daily development:**
```powershell
# Start backend
.\development\run_api.ps1

# Start frontend
.\development\run_frontend.ps1
```

## Adding New Scripts

When adding new scripts:
1. Place in appropriate subdirectory
2. Add descriptive header comments
3. Update this README
4. Make executable if shell script: `chmod +x script.sh`
