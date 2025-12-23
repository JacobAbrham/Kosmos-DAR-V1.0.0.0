# 🚀 KOSMOS Development Environment - Quick Start Guide

## Choose Your Development Environment

Run the **interactive setup** to select from 5 options:

```powershell
.\scripts\setup-interactive.ps1
```

---

## 📋 Environment Options

### 🐳 Option 1: Local Docker Compose
**Best for:** Individual developers with Docker Desktop

```powershell
.\scripts\setup-local-docker.ps1
```

**What you get:**
- ✅ PostgreSQL (localhost:5432)
- ✅ Redis (localhost:6379)
- ✅ MinIO (localhost:9001)
- ✅ NATS (localhost:4222)
- ✅ Ollama (localhost:11434)
- ✅ Docs (localhost:8080)

**Requirements:**
- Docker Desktop
- 8GB RAM
- 20GB disk space

**Cost:** FREE

---

### ☁️ Option 2: GitHub Codespaces
**Best for:** Cloud-based development, no local setup

```powershell
# From GitHub repository:
# Code → Codespaces → Create codespace
```

**What you get:**
- ✅ Auto-configured environment
- ✅ All services in cloud
- ✅ Browser-based VS Code
- ✅ Automatic port forwarding

**Requirements:**
- GitHub account
- Browser

**Cost:** Free tier (60 hours/month), then $0.18/hour

---

### 🖥️ Option 3: Remote Development Server
**Best for:** Teams sharing a development server

```powershell
.\scripts\setup-remote-server.ps1
```

**What you get:**
- ✅ Shared development server
- ✅ SSH port forwarding
- ✅ VS Code Remote SSH support
- ✅ Team collaboration

**Requirements:**
- SSH access to remote server
- Remote server with Docker

**Cost:** Server costs (variable)

---

### ☸️ Option 4: Shared Kubernetes (K3s)
**Best for:** Production-like environment, team development

```powershell
.\scripts\setup-k8s-dev.ps1
```

**What you get:**
- ✅ Personal K8s namespace
- ✅ Production-like setup
- ✅ Helm deployments
- ✅ Isolated environment per developer

**Requirements:**
- kubectl installed
- Helm installed
- K8s cluster access

**Cost:** Cluster costs (variable, ~$50-200/month shared)

---

### 🌐 Option 5: Gitpod Cloud IDE
**Best for:** Quick setup, browser-based development

```powershell
# Open in browser:
# https://gitpod.io/#<YOUR_GITHUB_REPO_URL>
```

**What you get:**
- ✅ Pre-configured workspace
- ✅ Auto-starts on repo open
- ✅ Browser-based IDE
- ✅ Automatic HTTPS for all ports

**Requirements:**
- GitHub account
- Browser

**Cost:** Free tier (50 hours/month), then $0.36/hour

---

## 📊 Comparison Matrix

| Feature | Local Docker | Codespaces | Remote Server | K8s Dev | Gitpod |
|---------|-------------|------------|---------------|---------|--------|
| **Setup Time** | 10 min | 5 min | 15 min | 20 min | 3 min |
| **Local Resources** | High | None | None | Low | None |
| **Production-like** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Cost** | FREE | Free tier | Variable | Shared | Free tier |
| **Team Collaboration** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Offline Work** | ✅ Yes | ❌ No | ❌ No | ❌ No | ❌ No |

---

## 🎯 Recommendations

### For Individual Developers:
→ **Start with Option 1** (Local Docker) or **Option 2** (Codespaces)

### For Small Teams (2-5 developers):
→ **Option 3** (Remote Server) or **Option 2** (Codespaces)

### For Larger Teams (5+ developers):
→ **Option 4** (Shared K8s) for production-like development

### For Quick Demos/POCs:
→ **Option 5** (Gitpod) for instant environment

---

## 🚀 After Setup

### Common Commands (All Environments):

```powershell
# View all commands
make help

# Run tests
make test

# Lint code
make lint

# Format code
make format

# View service logs
make dev-logs  # or: docker-compose logs -f

# Stop services
make dev-stop  # or: docker-compose down
```

### Access Services:

- **Documentation**: http://localhost:8080
- **PostgreSQL**: localhost:5432 (user: kosmos, db: kosmos_dev)
- **Redis**: localhost:6379
- **MinIO**: http://localhost:9001 (admin/admin)

---

## 🆘 Troubleshooting

### Docker issues:
```powershell
# Restart Docker Desktop
# Then:
docker-compose down -v
docker-compose up -d
```

### Port conflicts:
```powershell
# Check what's using ports
netstat -ano | findstr :5432
netstat -ano | findstr :6379

# Kill process or change ports in docker-compose.yml
```

### Permission issues:
```powershell
# Run PowerShell as Administrator
# Then re-run setup
```

---

## 📚 Next Steps

1. ✅ Choose and setup your environment
2. ✅ Review `.env` file and update settings
3. ✅ Run `make test` to verify setup
4. ✅ Start coding! Check [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP)

---

## 🔗 Resources

- [Full Automation Checklist](AUTOMATION_CHECKLIST)
- [Implementation Roadmap](IMPLEMENTATION_ROADMAP)
- [Gap Analysis](COMPREHENSIVE_GAP_ANALYSIS)
- [Automation Best Practices](AUTOMATION_GAPS_AND_BEST_PRACTICES)
