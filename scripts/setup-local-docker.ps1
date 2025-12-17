#!/usr/bin/env pwsh
# Local Docker setup for KOSMOS
# Usage: .\scripts\setup-local-docker.ps1

$ErrorActionPreference = "Stop"

function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Get-ComposeCommand {
    if (Test-Command "docker") {
        try {
            docker compose version | Out-Null
            return "docker compose"
        } catch {}
    }
    if (Test-Command "docker-compose") {
        return "docker-compose"
    }
    return $null
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  KOSMOS Local Docker Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$repoRoot = (Split-Path -Parent $PSScriptRoot)
Set-Location $repoRoot

# Prerequisites
Write-Host "`nChecking prerequisites..." -ForegroundColor Yellow
$composeCmd = Get-ComposeCommand
$missing = @()
if (-not (Test-Command "python")) { $missing += "Python 3.11+" }
if (-not (Test-Command "docker")) { $missing += "Docker Desktop" }
if (-not $composeCmd) { $missing += "Docker Compose plugin" }
if ($missing.Count -gt 0) {
    Write-Host "Missing: $($missing -join ', ')" -ForegroundColor Red
    Write-Host "Install Docker Desktop and ensure 'docker compose' works." -ForegroundColor Yellow
    exit 1
}
Write-Host "Prerequisites look good (using '$composeCmd')." -ForegroundColor Green

# Virtual environment
if (-not (Test-Path ".venv")) {
    Write-Host "`nCreating Python virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
} else {
    Write-Host "`nVirtual environment already exists, skipping creation." -ForegroundColor Cyan
}

$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Unable to locate venv Python at $venvPython" -ForegroundColor Red
    exit 1
}

Write-Host "`nUpgrading pip and installing Python dependencies..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt
if (Test-Path "requirements-dev.txt") {
    & $venvPython -m pip install -r requirements-dev.txt
}

Write-Host "`nInstalling pre-commit hooks..." -ForegroundColor Yellow
& $venvPython -m pip install pre-commit
& $venvPython -m pre-commit install
& $venvPython -m pre-commit install --hook-type commit-msg

# Environment file
Write-Host "`nEnsuring .env exists..." -ForegroundColor Yellow
if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example" -ForegroundColor Green
} elseif (-not (Test-Path ".env")) {
    Write-Host ".env.example not found; create .env manually." -ForegroundColor Red
}

# Start stack
Write-Host "`nStarting Docker services..." -ForegroundColor Yellow
& $composeCmd up -d --build

# Basic health wait
Write-Host "Waiting for API to report healthy..." -ForegroundColor Yellow
$healthy = $false
for ($i = 0; $i -lt 10; $i++) {
    Start-Sleep -Seconds 5
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 3
        if ($response.StatusCode -eq 200) {
            $healthy = $true
            break
        }
    } catch {}
}

Write-Host "`nService status:" -ForegroundColor Cyan
& $composeCmd ps

if ($healthy) {
    Write-Host "`nAPI responded OK." -ForegroundColor Green
} else {
    Write-Host "`nAPI health check did not respond yet. Check logs if needed." -ForegroundColor Yellow
}

Write-Host "`nSetup complete. Services:" -ForegroundColor Green
Write-Host "  API:            http://localhost:8000"
Write-Host "  Docs:           http://localhost:8080"
Write-Host "  Postgres:       localhost:5432 (user: kosmos)"
Write-Host "  Redis:          localhost:6379"
Write-Host "  MinIO console:  http://localhost:9001 (minioadmin/minioadmin)"

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "  1) Activate venv: .\.venv\Scripts\Activate.ps1"
Write-Host "  2) Run tests:     make test"
Write-Host "  3) View logs:     $composeCmd logs -f"
Write-Host "  4) Stop stack:    $composeCmd down"
