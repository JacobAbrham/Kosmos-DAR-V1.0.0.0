#!/usr/bin/env pwsh
# PowerShell setup script for Windows users
# Usage: .\scripts\setup.ps1

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        KOSMOS Development Environment Setup               ║" -ForegroundColor Cyan
Write-Host "║        AI-Native Enterprise Operating System              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

function Test-Command {
    param($Command)
    try {
        if (Get-Command $Command -ErrorAction Stop) {
            return $true
        }
    }
    catch {
        return $false
    }
}

# Check prerequisites
Write-Host "`n🔍 Checking prerequisites..." -ForegroundColor Yellow

$prerequisites = @{
    "python" = "Python"
    "docker" = "Docker"
    "git" = "Git"
}

$missing = @()
foreach ($cmd in $prerequisites.Keys) {
    if (Test-Command $cmd) {
        Write-Host "  ✅ $($prerequisites[$cmd]) is installed" -ForegroundColor Green
    }
    else {
        Write-Host "  ❌ $($prerequisites[$cmd]) is NOT installed" -ForegroundColor Red
        $missing += $prerequisites[$cmd]
    }
}

if ($missing.Count -gt 0) {
    Write-Host "`n❌ Missing required tools: $($missing -join ', ')" -ForegroundColor Red
    Write-Host "Please install them before continuing." -ForegroundColor Yellow
    exit 1
}

Write-Host "`n✅ All prerequisites are installed!" -ForegroundColor Green

# Create virtual environment
Write-Host "`n📦 Creating Python virtual environment..." -ForegroundColor Yellow
python -m venv .venv

# Activate virtual environment
Write-Host "`n🔧 Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "`n⬆️  Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "`n📦 Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if (Test-Path "requirements-dev.txt") {
    pip install -r requirements-dev.txt
}

# Install pre-commit
Write-Host "`n🪝 Setting up pre-commit hooks..." -ForegroundColor Yellow
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg

# Setup .env file
Write-Host "`n📝 Setting up environment file..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "  ✅ Created .env file from .env.example" -ForegroundColor Green
        Write-Host "  ⚠️  Please review and update .env with your settings" -ForegroundColor Yellow
    }
    else {
        Write-Host "  ⚠️  .env.example not found" -ForegroundColor Yellow
    }
}
else {
    Write-Host "  ℹ️  .env file already exists" -ForegroundColor Cyan
}

# Start Docker containers
Write-Host "`n🐳 Starting Docker containers..." -ForegroundColor Yellow
docker compose up -d

Write-Host "`n⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check container status
Write-Host "`n📊 Container status:" -ForegroundColor Yellow
docker compose ps

# Print summary
Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              🎉 KOSMOS SETUP COMPLETE! 🎉                 ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Review and update .env file with your settings"
Write-Host "  2. Activate virtual environment: .\.venv\Scripts\Activate.ps1"
Write-Host "  3. View documentation: mkdocs serve"
Write-Host "  4. Run tests: pytest tests/"

Write-Host "`n📚 Services Available:" -ForegroundColor Cyan
Write-Host "  • Docs:         http://localhost:8080"
Write-Host "  • PostgreSQL:   localhost:5432"
Write-Host "  • Redis:        localhost:6379"
Write-Host "  • MinIO:        http://localhost:9001"

Write-Host "`n✨ Setup completed successfully!" -ForegroundColor Green
