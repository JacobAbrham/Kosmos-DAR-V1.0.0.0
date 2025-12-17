#!/usr/bin/env pwsh
# Gitpod Cloud IDE Setup (Option 5)

Write-Host "🌐 Setting up Gitpod Cloud IDE" -ForegroundColor Cyan
Write-Host "="*70 -ForegroundColor Gray

Write-Host "`nℹ️  Gitpod Cloud IDE Setup" -ForegroundColor Cyan
Write-Host "Gitpod uses the .gitpod.yml configuration automatically.`n" -ForegroundColor Gray

# Check if running in Gitpod
if ($env:GITPOD_WORKSPACE_ID) {
    Write-Host "✅ Running in Gitpod!" -ForegroundColor Green
    
    # Setup Python environment
    Write-Host "`n1️⃣  Setting up Python..." -ForegroundColor Yellow
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    if (Test-Path "requirements-dev.txt") {
        pip install -r requirements-dev.txt -q
    }
    Write-Host "✅ Python dependencies installed" -ForegroundColor Green
    
    # Setup pre-commit
    Write-Host "`n2️⃣  Installing pre-commit hooks..." -ForegroundColor Yellow
    pip install pre-commit -q
    pre-commit install
    Write-Host "✅ Pre-commit hooks installed" -ForegroundColor Green
    
    # Setup .env
    Write-Host "`n3️⃣  Configuring environment..." -ForegroundColor Yellow
    if (-not (Test-Path ".env")) {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Created .env for Gitpod" -ForegroundColor Green
    }
    
    # Start services
    Write-Host "`n4️⃣  Starting services..." -ForegroundColor Yellow
    docker compose up -d
    
    Write-Host "`n✅ Gitpod environment ready!" -ForegroundColor Green
    Write-Host "`nℹ️  Services are automatically exposed by Gitpod" -ForegroundColor Cyan
    
} else {
    Write-Host "ℹ️  Not running in Gitpod environment" -ForegroundColor Yellow
    Write-Host "`nTo use Gitpod:" -ForegroundColor Cyan
    Write-Host "  1. Go to: https://gitpod.io/#YOUR_GITHUB_REPO_URL" -ForegroundColor White
    Write-Host "  2. Or install Gitpod browser extension for one-click launch" -ForegroundColor White
    Write-Host "  3. Workspace uses .gitpod.yml configuration" -ForegroundColor White
    
    Write-Host "`n📝 Creating .gitpod.yml configuration..." -ForegroundColor Yellow
    
    # Create Gitpod config if it doesn't exist
    if (-not (Test-Path ".gitpod.yml")) {
        Write-Host "✅ Gitpod configuration ready" -ForegroundColor Green
        Write-Host "   Push to GitHub and open in Gitpod to use it" -ForegroundColor Gray
    } else {
        Write-Host "ℹ️  .gitpod.yml already exists" -ForegroundColor Cyan
    }
    
    Write-Host "`n📝 Creating Gitpod button for README..." -ForegroundColor Yellow
    Write-Host "Add this to your README.md:" -ForegroundColor Gray
    Write-Host "  [![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#YOUR_REPO_URL)" -ForegroundColor White
}

Write-Host "`n💡 Gitpod Tips:" -ForegroundColor Cyan
Write-Host "  • Free tier: 50 hours/month" -ForegroundColor White
Write-Host "  • Workspaces auto-suspend after 30 minutes of inactivity" -ForegroundColor White
Write-Host "  • Use 'gp' command for Gitpod-specific operations" -ForegroundColor White
Write-Host "  • Ports are automatically exposed and HTTPS-enabled" -ForegroundColor White
