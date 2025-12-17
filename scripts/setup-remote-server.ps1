#!/usr/bin/env pwsh
# Remote Development Server Setup (Option 3)

Write-Host "🖥️  Setting up Remote Development Server" -ForegroundColor Cyan
Write-Host "="*70 -ForegroundColor Gray

Write-Host "`nThis script will help you connect to a remote development server.`n" -ForegroundColor Gray

# Get remote server details
$remoteHost = Read-Host "Enter remote server hostname or IP"
$remoteUser = Read-Host "Enter SSH username"
$remotePort = Read-Host "Enter SSH port (default: 22)"
if ([string]::IsNullOrWhiteSpace($remotePort)) { $remotePort = "22" }

Write-Host "`n1️⃣  Testing SSH connection..." -ForegroundColor Yellow
$sshTest = ssh -p $remotePort "${remoteUser}@${remoteHost}" "echo 'Connection successful'" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ SSH connection successful" -ForegroundColor Green
} else {
    Write-Host "❌ SSH connection failed" -ForegroundColor Red
    Write-Host "Error: $sshTest" -ForegroundColor Red
    Write-Host "`nPlease ensure:" -ForegroundColor Yellow
    Write-Host "  • SSH server is running on remote host" -ForegroundColor White
    Write-Host "  • You have SSH key access configured" -ForegroundColor White
    Write-Host "  • Firewall allows SSH connections" -ForegroundColor White
    exit 1
}

# Create SSH config entry
Write-Host "`n2️⃣  Configuring SSH..." -ForegroundColor Yellow
$sshConfigPath = "$env:USERPROFILE\.ssh\config"
$configEntry = @"

# KOSMOS Development Server
Host kosmos-dev
    HostName $remoteHost
    User $remoteUser
    Port $remotePort
    ForwardAgent yes
    # Port forwards for services
    LocalForward 5432 localhost:5432
    LocalForward 6379 localhost:6379
    LocalForward 8000 localhost:8000
    LocalForward 8080 localhost:8080
"@

if (Test-Path $sshConfigPath) {
    $existingConfig = Get-Content $sshConfigPath -Raw
    if ($existingConfig -notmatch "Host kosmos-dev") {
        Add-Content -Path $sshConfigPath -Value $configEntry
        Write-Host "✅ Added SSH config entry" -ForegroundColor Green
    } else {
        Write-Host "ℹ️  SSH config entry already exists" -ForegroundColor Cyan
    }
} else {
    New-Item -ItemType Directory -Path "$env:USERPROFILE\.ssh" -Force | Out-Null
    Set-Content -Path $sshConfigPath -Value $configEntry
    Write-Host "✅ Created SSH config" -ForegroundColor Green
}

# Setup remote environment
Write-Host "`n3️⃣  Setting up remote environment..." -ForegroundColor Yellow

$remoteSetup = @'
cd ~/kosmos || mkdir -p ~/kosmos && cd ~/kosmos
if [ ! -d ".git" ]; then
    echo "Cloning repository..."
    git clone YOUR_REPO_URL .
fi
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
docker compose up -d
'@

ssh -p $remotePort "${remoteUser}@${remoteHost}" $remoteSetup

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Remote environment configured" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some remote setup steps may have failed" -ForegroundColor Yellow
}

# Configure VS Code Remote SSH
Write-Host "`n4️⃣  VS Code Remote SSH Configuration..." -ForegroundColor Yellow
Write-Host "To use VS Code Remote SSH:" -ForegroundColor Cyan
Write-Host "  1. Install 'Remote - SSH' extension in VS Code" -ForegroundColor White
Write-Host "  2. Press F1, type 'Remote-SSH: Connect to Host'" -ForegroundColor White
Write-Host "  3. Select 'kosmos-dev' from the list" -ForegroundColor White
Write-Host "  4. Open folder: ~/kosmos" -ForegroundColor White

Write-Host "`n✅ Remote Development Server Setup Complete!" -ForegroundColor Green
Write-Host "`n📚 Connection Information:" -ForegroundColor Cyan
Write-Host "  • SSH Alias:    ssh kosmos-dev" -ForegroundColor White
Write-Host "  • Direct SSH:   ssh -p $remotePort ${remoteUser}@${remoteHost}" -ForegroundColor White
Write-Host "  • Port Forwards: PostgreSQL (5432), Redis (6379), API (8000), Docs (8080)" -ForegroundColor White

Write-Host "`n🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "  • Connect: ssh kosmos-dev" -ForegroundColor White
Write-Host "  • Or use VS Code Remote SSH extension" -ForegroundColor White
