#!/usr/bin/env pwsh
# Shared Kubernetes Development Setup (Option 4)

Write-Host "☸️  Setting up Shared Kubernetes Development Environment" -ForegroundColor Cyan
Write-Host "="*70 -ForegroundColor Gray

# Check kubectl
Write-Host "`n1️⃣  Checking kubectl..." -ForegroundColor Yellow
if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
    Write-Host "❌ kubectl is not installed!" -ForegroundColor Red
    Write-Host "Install from: https://kubernetes.io/docs/tasks/tools/" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ kubectl is installed" -ForegroundColor Green

# Check Helm
Write-Host "`n2️⃣  Checking Helm..." -ForegroundColor Yellow
if (-not (Get-Command helm -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Helm is not installed!" -ForegroundColor Red
    Write-Host "Install from: https://helm.sh/docs/intro/install/" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Helm is installed" -ForegroundColor Green

# Check cluster connection
Write-Host "`n3️⃣  Checking cluster connection..." -ForegroundColor Yellow
$clusterInfo = kubectl cluster-info 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Connected to Kubernetes cluster" -ForegroundColor Green
    Write-Host $clusterInfo -ForegroundColor Gray
} else {
    Write-Host "❌ Not connected to a Kubernetes cluster" -ForegroundColor Red
    Write-Host "`nPlease configure kubectl:" -ForegroundColor Yellow
    Write-Host "  • Get kubeconfig from your cluster admin" -ForegroundColor White
    Write-Host "  • Set KUBECONFIG environment variable" -ForegroundColor White
    Write-Host "  • Or run: kubectl config use-context <context-name>" -ForegroundColor White
    exit 1
}

# Get developer namespace
Write-Host "`n4️⃣  Setting up developer namespace..." -ForegroundColor Yellow
$devName = $env:USERNAME.ToLower() -replace '[^a-z0-9-]', '-'
$namespace = "kosmos-dev-$devName"

Write-Host "Your namespace will be: $namespace" -ForegroundColor Cyan

# Create namespace
kubectl create namespace $namespace --dry-run=client -o yaml | kubectl apply -f -
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Namespace created/verified" -ForegroundColor Green
} else {
    Write-Host "⚠️  Namespace creation failed - you may need admin permissions" -ForegroundColor Yellow
}

# Set default namespace
kubectl config set-context --current --namespace=$namespace
Write-Host "✅ Set default namespace to $namespace" -ForegroundColor Green

# Deploy development environment
Write-Host "`n5️⃣  Deploying development environment..." -ForegroundColor Yellow

# Check if Helm chart exists
if (Test-Path "helm/kosmos") {
    $devValuesFile = "helm/kosmos/values-dev-k8s.yaml"
    
    # Create dev values if not exists
    if (-not (Test-Path $devValuesFile)) {
        Write-Host "Creating development values file..." -ForegroundColor Gray
        @"
# Development K8s Environment
replicaCount: 1

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

postgresql:
  enabled: true
  primary:
    resources:
      limits:
        memory: 256Mi

redis:
  enabled: true
  master:
    resources:
      limits:
        memory: 128Mi

ingress:
  enabled: true
  hosts:
    - host: kosmos-$devName.dev.local
      paths:
        - path: /
          pathType: Prefix
"@ | Set-Content $devValuesFile
    }
    
    # Deploy with Helm
    helm upgrade --install kosmos-dev ./helm/kosmos `
        -f $devValuesFile `
        --namespace $namespace `
        --wait --timeout 5m
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Development environment deployed" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Deployment encountered issues" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Helm chart not found - manual deployment needed" -ForegroundColor Yellow
    Write-Host "Apply manifests from k8s/ directory manually" -ForegroundColor Gray
}

# Setup port forwarding
Write-Host "`n6️⃣  Setting up port forwarding..." -ForegroundColor Yellow
Write-Host "Creating port-forward script..." -ForegroundColor Gray

$portForwardScript = @"
# Port forward script for $namespace
`$jobs = @()

Write-Host "Starting port forwards for $namespace..." -ForegroundColor Cyan

# PostgreSQL
`$jobs += Start-Job -ScriptBlock { kubectl port-forward -n $namespace svc/postgresql 5432:5432 }
Write-Host "  PostgreSQL: localhost:5432" -ForegroundColor White

# Redis
`$jobs += Start-Job -ScriptBlock { kubectl port-forward -n $namespace svc/redis 6379:6379 }
Write-Host "  Redis: localhost:6379" -ForegroundColor White

# API (when deployed)
`$jobs += Start-Job -ScriptBlock { kubectl port-forward -n $namespace svc/kosmos-api 8000:8000 }
Write-Host "  API: localhost:8000" -ForegroundColor White

Write-Host "`nPort forwards active. Press Ctrl+C to stop." -ForegroundColor Yellow
`$jobs | Wait-Job
"@

Set-Content -Path "scripts/port-forward-k8s.ps1" -Value $portForwardScript
Write-Host "✅ Created port-forward script: scripts/port-forward-k8s.ps1" -ForegroundColor Green

# Print pod status
Write-Host "`n7️⃣  Pod Status:" -ForegroundColor Yellow
kubectl get pods -n $namespace

Write-Host "`n✅ Kubernetes Development Environment Setup Complete!" -ForegroundColor Green

Write-Host "`n📚 Your Development Environment:" -ForegroundColor Cyan
Write-Host "  • Namespace:    $namespace" -ForegroundColor White
Write-Host "  • Context:      $(kubectl config current-context)" -ForegroundColor White

Write-Host "`n🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "  • View pods:    kubectl get pods" -ForegroundColor White
Write-Host "  • View logs:    kubectl logs -f <pod-name>" -ForegroundColor White
Write-Host "  • Port forward: .\scripts\port-forward-k8s.ps1" -ForegroundColor White
Write-Host "  • Shell into:   kubectl exec -it <pod-name> -- /bin/bash" -ForegroundColor White
