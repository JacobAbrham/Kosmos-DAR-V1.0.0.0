# KOSMOS GUI Setup - Quick Start Guide

Choose your preferred interface:

## 🖥️ Option 1: Windows Desktop App (Recommended for Windows users)

### Download & Run (Easiest)
1. Download `KOSMOS-Setup.exe` from releases
2. Double-click to run
3. Select environment → Start setup → Done!

### Build from Source
```powershell
# Install requirements
pip install -r gui/requirements.txt

# Run GUI
python gui/setup_gui.py

# OR build .exe for distribution
python gui/build_exe.py
# Output: dist/KOSMOS-Setup.exe
```

**Features:**
- ✅ Native Windows interface
- ✅ No browser needed
- ✅ Offline-capable
- ✅ Easy for non-technical users
- ✅ Real-time progress
- ✅ Visual environment selection
- ✅ **Interactive .env configuration**

---

## 🌐 Option 2: Web Dashboard (Works on any OS)

### Start Web Server
```powershell
# Install requirements
pip install -r gui/requirements.txt

# Start server
python gui/web_setup.py

# Open browser to: http://localhost:5000
```

**Features:**
- ✅ Cross-platform (Windows/Mac/Linux)
- ✅ Modern web UI
- ✅ Mobile-friendly
- ✅ Real-time WebSocket updates
- ✅ Multi-user support
- ✅ Beautiful gradient design
- ✅ **Interactive .env configuration**

---

## 📋 What Both Tools Do

1. **Show 5 environment options** with descriptions
2. **Configure .env variables** interactively (NEW!)
4. **Run automated setup** scripts
5. **Show real-time progress** with color-coded output
6. **Handle errors** gracefully with clear messages
7. **Handle errors** gracefully with clear messages
6. **Guide next steps** after completion

---

## 🎯 Which Should I Use?

| Use Case | Recommended Tool |
|----------|-----------------|
| Windows user, prefer desktop apps | Windows .exe |
| Mac/Linux user | Web dashboard |
| Mobile device | Web dashboard |
| Share with team | Web dashboard |
| Offline setup | Windows .exe |
| Non-technical user | Windows .exe |
| Remote server setup | Web dashboard |

---

## 🚀 After Setup Completes

Both tools will show:
- ✅ Setup success message
- 📝 Next steps to start developing
- 🔗 Links to documentation
- ⚙️ Configuration details

Then you can:
```powershell
# Start development
make dev

# Access documentation
http://localhost:8000

# Begin Phase 1 implementation
```

---

## 📖 Full Documentation

See [gui/README.md](gui/README.md) for:
- Detailed setup instructions
- Customization options
- Troubleshooting guide
- Building for distribution
- Screenshots and examples

---

## ⚡ TL;DR

**Absolute quickest start:**

```powershell
# Web dashboard (3 commands)
pip install -r gui/requirements.txt
python gui/web_setup.py
# Open: http://localhost:5000

# OR Windows app (1 download)
# Download KOSMOS-Setup.exe → Double-click → Done!
```

Both methods take **3-30 minutes** depending on environment choice.
Codespaces/Gitpod = 3-5 minutes (fastest!)
