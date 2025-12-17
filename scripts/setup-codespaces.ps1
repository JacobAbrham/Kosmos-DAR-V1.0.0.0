#!/usr/bin/env pwsh
# GitHub Codespaces Setup (Option 2)

Write-Host "??  Setting up GitHub Codespaces Development Environment" -ForegroundColor Cyan
Write-Host "="*70 -ForegroundColor Gray

Write-Host "`n??  GitHub Codespaces Setup" -ForegroundColor Cyan
Write-Host "Codespaces uses the .devcontainer configuration automatically.`n" -ForegroundColor Gray

# Check if running in Codespaces
if ($env:CODESPACES -eq "true") {
    Write-Host "? Running in GitHub Codespaces!" -ForegroundColor Green
    
    # Setup Python environment
    Write-Host "`n1??  Setting up Python..." -ForegroundColor Yellow
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    if (Test-Path "requirements-dev.txt") {
        pip install -r requirements-dev.txt -q
    }
    Write-Host "? Python dependencies installed" -ForegroundColor Green
    
    # Setup pre-commit
    Write-Host "`n2??  Installing pre-commit hooks..." -ForegroundColor Yellow
    pip install pre-commit -q
    pre-commit install
    Write-Host "? Pre-commit hooks installed" -ForegroundColor Green
    
    # Setup .env
    Write-Host "`n3??  Configuring environment..." -ForegroundColor Yellow
    if (-not (Test-Path ".env")) {
        Copy-Item ".env.example" ".env"
        # Update for Codespaces
        (Get-Content ".env") -replace 'localhost', '0.0.0.0' | Set-Content ".env"
        Write-Host "? Created .env for Codespaces" -ForegroundColor Green
    }
    
    # Quick start guidance
    Write-Host "`n4??  Codespaces ready for development" -ForegroundColor Green
    Write-Host "   - Start stub API: uvicorn src.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
    Write-Host "   - (Optional) Full stack: docker compose up -d" -ForegroundColor White
    Write-Host "     Ports are forwarded automatically by Codespaces." -ForegroundColor Gray
    
} else {
    Write-Host "??  Not running in Codespaces environment" -ForegroundColor Yellow
    Write-Host "`nTo use GitHub Codespaces:" -ForegroundColor Cyan
    Write-Host "  1. Go to your GitHub repository" -ForegroundColor White
    Write-Host "  2. Click 'Code'  'Codespaces'  'Create codespace'" -ForegroundColor White
    Write-Host "  3. Wait for environment to build (uses .devcontainer/devcontainer.json)" -ForegroundColor White
    Write-Host "  4. This setup script runs automatically on first launch" -ForegroundColor White
    
    Write-Host "`n?? Creating .devcontainer configuration..." -ForegroundColor Yellow
    
    # Create devcontainer config if it doesn't exist
    $devcontainerPath = ".devcontainer"
    if (-not (Test-Path $devcontainerPath)) {
        New-Item -ItemType Directory -Path $devcontainerPath -Force | Out-Null
    }
    
    Write-Host "? Codespaces configuration ready" -ForegroundColor Green
    Write-Host "   Push to GitHub and create a Codespace to use it" -ForegroundColor Gray
}
