#!/usr/bin/env pwsh
# KOSMOS Development Environment Setup - Interactive Mode
# Supports all 5 development environment options from Implementation Roadmap

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        KOSMOS Development Environment Setup               ║" -ForegroundColor Cyan
Write-Host "║        Select Your Development Environment                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

# Display environment options
Write-Host "`n📋 Available Development Environments:`n" -ForegroundColor Yellow

Write-Host "1. 🐳 Local Docker Compose" -ForegroundColor Green
Write-Host "   • Best for: Individual developers with Docker Desktop" -ForegroundColor Gray
Write-Host "   • Requirements: Docker Desktop, 8GB RAM, 20GB disk" -ForegroundColor Gray
Write-Host "   • Cost: FREE" -ForegroundColor Gray
Write-Host ""

Write-Host "2. ☁️  GitHub Codespaces" -ForegroundColor Green
Write-Host "   • Best for: Cloud-based development, no local setup" -ForegroundColor Gray
Write-Host "   • Requirements: GitHub account, browser" -ForegroundColor Gray
Write-Host "   • Cost: Free tier available, then usage-based" -ForegroundColor Gray
Write-Host ""

Write-Host "3. 🖥️  Remote Development Server" -ForegroundColor Green
Write-Host "   • Best for: Teams sharing a development server" -ForegroundColor Gray
Write-Host "   • Requirements: SSH access, remote server with Docker" -ForegroundColor Gray
Write-Host "   • Cost: Server costs (variable)" -ForegroundColor Gray
Write-Host ""

Write-Host "4. ☸️  Shared Kubernetes (K3s) Cluster" -ForegroundColor Green
Write-Host "   • Best for: Teams wanting production-like environment" -ForegroundColor Gray
Write-Host "   • Requirements: K8s cluster access, kubectl configured" -ForegroundColor Gray
Write-Host "   • Cost: Cluster costs (variable)" -ForegroundColor Gray
Write-Host ""

Write-Host "5. 🌐 Gitpod Cloud IDE" -ForegroundColor Green
Write-Host "   • Best for: Quick setup, browser-based development" -ForegroundColor Gray
Write-Host "   • Requirements: GitHub account, browser" -ForegroundColor Gray
Write-Host "   • Cost: Free tier available, then usage-based" -ForegroundColor Gray
Write-Host ""

# Get user selection
$choice = Read-Host "Select your development environment (1-5)"

switch ($choice) {
    "1" {
        Write-Host "`n🐳 Setting up Local Docker Compose environment...`n" -ForegroundColor Cyan
        & "$PSScriptRoot\setup-local-docker.ps1"
    }
    "2" {
        Write-Host "`n☁️  Setting up GitHub Codespaces environment...`n" -ForegroundColor Cyan
        & "$PSScriptRoot\setup-codespaces.ps1"
    }
    "3" {
        Write-Host "`n🖥️  Setting up Remote Development Server...`n" -ForegroundColor Cyan
        & "$PSScriptRoot\setup-remote-server.ps1"
    }
    "4" {
        Write-Host "`n☸️  Setting up Shared Kubernetes environment...`n" -ForegroundColor Cyan
        & "$PSScriptRoot\setup-k8s-dev.ps1"
    }
    "5" {
        Write-Host "`n🌐 Setting up Gitpod environment...`n" -ForegroundColor Cyan
        & "$PSScriptRoot\setup-gitpod.ps1"
    }
    default {
        Write-Host "`n❌ Invalid selection. Please run the script again and choose 1-5." -ForegroundColor Red
        exit 1
    }
}
