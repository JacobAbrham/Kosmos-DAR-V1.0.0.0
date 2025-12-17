# KOSMOS GUI Setup Tools

This directory contains graphical user interfaces for KOSMOS setup.

## Available Interfaces

### 1. Windows Desktop Application (.exe)

**Best for:** Windows users who prefer native applications

#### Features:
- ✅ Native Windows GUI built with tkinter
- ✅ No browser required
- ✅ Offline-capable after download
- ✅ Real-time progress tracking
- ✅ Visual environment selection
- ✅ Color-coded status indicators

#### Quick Start:

**Option A: Download Pre-built Executable (Recommended)**
```powershell
# Download from GitHub Releases
# Double-click KOSMOS-Setup.exe to run
```

**Option B: Build from Source**
```powershell
# Install dependencies
pip install -r gui/requirements.txt

# Run directly
python gui/setup_gui.py

# OR build .exe
python gui/build_exe.py

# Find executable at: dist/KOSMOS-Setup.exe
```

#### Usage:
1. Launch `KOSMOS-Setup.exe`
2. Select your preferred environment
3. Review requirements and details
4. Click "Start Setup"
5. Monitor progress in real-time
6. Done! Follow on-screen next steps

---

### 2. Web Dashboard (Browser-based)

**Best for:** Cross-platform users, remote setups, team environments

#### Features:
- ✅ Works on any OS (Windows, Mac, Linux)
- ✅ Modern responsive web interface
- ✅ Real-time WebSocket updates
- ✅ Mobile-friendly design
- ✅ No installation required (just Python)
- ✅ Multi-user support
- ✅ Beautiful gradient UI

#### Quick Start:

```powershell
# Install dependencies
pip install -r gui/requirements.txt

# Start web server
python gui/web_setup.py

# Open browser
# Navigate to: http://localhost:5000
```

#### Usage:
1. Open browser to http://localhost:5000
2. Click on your preferred environment card
3. Review details panel
4. Click "Start Setup"
5. Watch live output in terminal-style log
6. Status bar shows real-time progress

#### Customization:
```python
# Change port
socketio.run(app, host='0.0.0.0', port=8080)

# Enable production mode
socketio.run(app, debug=False)

# Allow external access
socketio.run(app, host='0.0.0.0')
```

---

## Comparison Matrix

| Feature | Windows .exe | Web Dashboard |
|---------|-------------|---------------|
| **Platform** | Windows only | Any OS |
| **Installation** | Download & run | Python + pip |
| **Interface** | Native tkinter | Modern web UI |
| **Mobile Support** | ❌ | ✅ |
| **Offline** | ✅ (after download) | ❌ (needs server) |
| **Multi-user** | ❌ | ✅ |
| **File Size** | ~15-20 MB | ~2 MB |
| **Startup Time** | Instant | 1-2 seconds |
| **Updates** | Re-download | Pull git |

---

## Screenshots

### Windows Desktop App
```
┌─────────────────────────────────────────┐
│  🚀 KOSMOS Development Environment      │
│                                         │
│  ○ 🐳 Local Docker Compose             │
│  ● ☁️  GitHub Codespaces   [SELECTED]  │
│  ○ 🖥️  Remote Development Server       │
│  ○ ☸️  Shared Kubernetes Cluster       │
│  ○ 🌐 Gitpod Cloud IDE                 │
│                                         │
│  ┌─ Environment Details ─────────────┐ │
│  │ Cloud-based from GitHub           │ │
│  │ Requirements: GitHub account      │ │
│  │ Cost: Free tier (60 hrs/month)    │ │
│  │ Skill: ⭐ Beginner                │ │
│  │ Time: 3-5 minutes                 │ │
│  └───────────────────────────────────┘ │
│                                         │
│  [▶ Start Setup] [✖ Cancel] [❓ Help] │
│                                         │
│  ┌─ Setup Progress ──────────────────┐ │
│  │ ▶ Starting setup...               │ │
│  │ ✅ Checking prerequisites...      │ │
│  │ ⏳ Installing dependencies...     │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Web Dashboard
```
Beautiful gradient background with cards:
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│   🐳           │  │   ☁️           │  │   🖥️           │
│ Local Docker   │  │  Codespaces    │  │ Remote Server  │
│                │  │                │  │                │
│ ⭐ Beginner    │  │ ⭐ Beginner    │  │ ⭐⭐ Inter.    │
│ 10-15 min      │  │ 3-5 min        │  │ 15-20 min      │
└────────────────┘  └────────────────┘  └────────────────┘

[Selected environment details appear below]
[▶ Start Setup button]
[Real-time terminal output]
[Status bar with live updates]
```

---

## Building for Distribution

### Create Windows Installer

```powershell
# Build standalone .exe
python gui/build_exe.py

# Creates: dist/KOSMOS-Setup.exe (~15-20 MB)

# Optional: Create installer with NSIS
# Download NSIS: https://nsis.sourceforge.io/
makensis gui/installer.nsi
```

### Create Web Container

```dockerfile
# Dockerfile for web dashboard
FROM python:3.11-slim

WORKDIR /app
COPY gui/ /app/gui/
COPY scripts/ /app/scripts/

RUN pip install -r gui/requirements.txt

EXPOSE 5000
CMD ["python", "gui/web_setup.py"]
```

```powershell
# Build and run
docker build -t kosmos-web-setup .
docker run -p 5000:5000 kosmos-web-setup

# Access at: http://localhost:5000
```

---

## Development

### Running in Development Mode

```powershell
# Windows GUI (with auto-reload)
python gui/setup_gui.py

# Web dashboard (with debug)
python gui/web_setup.py
# Flask debug mode enabled automatically
```

### Testing

```powershell
# Test GUI components
python -m pytest tests/test_gui.py

# Test web endpoints
python -m pytest tests/test_web.py

# Test WebSocket communication
python -m pytest tests/test_socketio.py
```

---

## Troubleshooting

### Windows .exe Issues

**Problem:** "Windows protected your PC" warning
**Solution:** Click "More info" → "Run anyway" (unsigned executable)

**Problem:** Antivirus flags executable
**Solution:** Add exception or build from source

**Problem:** .exe won't start
**Solution:** Ensure all DLLs included, run from dist/ folder

### Web Dashboard Issues

**Problem:** Port 5000 already in use
**Solution:** Change port in web_setup.py or kill existing process

**Problem:** WebSocket connection failed
**Solution:** Check firewall, ensure SocketIO installed

**Problem:** Slow performance
**Solution:** Disable debug mode for production

---

## Security Notes

⚠️ **Important:**
- Both tools run PowerShell scripts with `-ExecutionPolicy Bypass`
- Review scripts before running in production
- Web dashboard should be localhost-only in untrusted networks
- Consider HTTPS for remote access
- Validate all user inputs

---

## Next Steps

After successful setup:
1. ✅ Environment is configured
2. ✅ Dependencies installed
3. ✅ Services running

**Now you can:**
- Open VS Code in environment
- Run `make dev` to start development
- Access docs at http://localhost:8000
- Begin Phase 1 implementation

---

## Support

- 📖 Full documentation: [DEVELOPMENT_ENVIRONMENT_GUIDE.md](../DEVELOPMENT_ENVIRONMENT_GUIDE.md)
- 📊 Automation assessment: [DEV_STAGE_AUTOMATION_ASSESSMENT.md](../DEV_STAGE_AUTOMATION_ASSESSMENT.md)
- 🎥 Video tutorials: [VIDEO_SCRIPTS.md](../VIDEO_SCRIPTS.md)
- 🐛 Report issues: [GitHub Issues](https://github.com/your-org/kosmos/issues)

---

## License

Same as main KOSMOS project - see [LICENSE](../LICENSE)
