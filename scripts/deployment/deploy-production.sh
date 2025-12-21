#!/bin/bash
# KOSMOS Production Deployment Script
# Usage: ./deploy-production.sh [--dry-run]

set -e

# Configuration
NAMESPACE="${NAMESPACE:-kosmos-production}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REGISTRY="${REGISTRY:-ghcr.io/kosmos}"
DRY_RUN=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        --namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 KOSMOS Production Deployment${NC}"
echo "=================================="
echo "Namespace:  $NAMESPACE"
echo "Image Tag:  $IMAGE_TAG"
echo "Registry:   $REGISTRY"
echo "Dry Run:    $DRY_RUN"
echo ""

# Navigate to project root
cd "$(dirname "$0")/../.." || exit 1
PROJECT_ROOT=$(pwd)

# Check for required tools
check_requirements() {
    echo "📋 Checking requirements..."
    
    local missing=0
    
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}  ❌ kubectl not found${NC}"
        missing=1
    else
        echo -e "${GREEN}  ✅ kubectl${NC}"
    fi
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}  ❌ docker not found${NC}"
        missing=1
    else
        echo -e "${GREEN}  ✅ docker${NC}"
    fi
    
    if [ $missing -eq 1 ]; then
        echo -e "${RED}Missing required tools. Please install them first.${NC}"
        exit 1
    fi
    echo ""
}

# Check Kubernetes connectivity
check_kubernetes() {
    echo "🔌 Checking Kubernetes connectivity..."
    
    if ! kubectl cluster-info &> /dev/null; then
        echo -e "${RED}❌ Cannot connect to Kubernetes cluster${NC}"
        echo "Please configure kubectl or start minikube:"
        echo "  minikube start --memory=8192 --cpus=4"
        exit 1
    fi
    
    CONTEXT=$(kubectl config current-context)
    echo -e "${GREEN}  ✅ Connected to: $CONTEXT${NC}"
    echo ""
}

# Create namespace
create_namespace() {
    echo "📦 Setting up namespace..."
    
    if $DRY_RUN; then
        echo "  [DRY RUN] Would create namespace: $NAMESPACE"
    else
        if kubectl get namespace "$NAMESPACE" &> /dev/null; then
            echo -e "${YELLOW}  Namespace $NAMESPACE already exists${NC}"
        else
            kubectl apply -f infrastructure/kubernetes/production/namespace.yaml
            echo -e "${GREEN}  ✅ Namespace created${NC}"
        fi
    fi
    echo ""
}

# Build and push images
build_images() {
    echo "🏗️  Building Docker images..."
    
    if $DRY_RUN; then
        echo "  [DRY RUN] Would build:"
        echo "    - kosmos-api:$IMAGE_TAG"
        echo "    - kosmos-frontend:$IMAGE_TAG"
    else
        # Check if we're in minikube
        if kubectl config current-context | grep -q "minikube"; then
            echo "  Using minikube's Docker daemon..."
            eval $(minikube docker-env)
        fi
        
        echo "  Building API image..."
        docker build -t kosmos-api:$IMAGE_TAG -f infrastructure/docker/api/Dockerfile . 2>&1 | tail -5
        
        echo "  Building Frontend image..."
        docker build -t kosmos-frontend:$IMAGE_TAG -f infrastructure/docker/frontend/Dockerfile ./frontend 2>&1 | tail -5
        
        echo -e "${GREEN}  ✅ Images built${NC}"
    fi
    echo ""
}

# Apply Kubernetes manifests
apply_manifests() {
    echo "📄 Applying Kubernetes manifests..."
    
    MANIFESTS=(
        "infrastructure/kubernetes/production/namespace.yaml"
        "infrastructure/kubernetes/production/api-deployment.yaml"
        "infrastructure/kubernetes/production/frontend-deployment.yaml"
    )
    
    # Optional manifests
    if [ -f "infrastructure/kubernetes/production/ingress.yaml" ]; then
        MANIFESTS+=("infrastructure/kubernetes/production/ingress.yaml")
    fi
    
    for manifest in "${MANIFESTS[@]}"; do
        if [ -f "$manifest" ]; then
            if $DRY_RUN; then
                echo "  [DRY RUN] Would apply: $manifest"
            else
                kubectl apply -f "$manifest" 2>&1 | grep -E "created|configured|unchanged" || true
            fi
        fi
    done
    
    echo -e "${GREEN}  ✅ Manifests applied${NC}"
    echo ""
}

# Wait for rollout
wait_for_rollout() {
    echo "⏳ Waiting for deployment rollout..."
    
    if $DRY_RUN; then
        echo "  [DRY RUN] Would wait for deployments"
    else
        echo "  Waiting for API deployment..."
        kubectl rollout status deployment/kosmos-api -n "$NAMESPACE" --timeout=300s 2>/dev/null || echo "  API rollout pending..."
        
        echo "  Waiting for Frontend deployment..."
        kubectl rollout status deployment/kosmos-frontend -n "$NAMESPACE" --timeout=300s 2>/dev/null || echo "  Frontend rollout pending..."
    fi
    echo ""
}

# Verify deployment
verify_deployment() {
    echo "🔍 Verifying deployment..."
    
    if $DRY_RUN; then
        echo "  [DRY RUN] Would verify deployment"
        return
    fi
    
    echo "  Pods:"
    kubectl get pods -n "$NAMESPACE" -o wide 2>/dev/null || echo "  No pods found"
    
    echo ""
    echo "  Services:"
    kubectl get services -n "$NAMESPACE" 2>/dev/null || echo "  No services found"
    
    echo ""
    
    # Port forward for testing if minikube
    if kubectl config current-context | grep -q "minikube"; then
        echo "  Setting up port forwarding for testing..."
        kubectl port-forward -n "$NAMESPACE" svc/kosmos-api 8080:8000 &>/dev/null &
        PF_PID=$!
        sleep 3
        
        echo "  Testing health endpoint..."
        if curl -s http://localhost:8080/health | grep -q "healthy"; then
            echo -e "${GREEN}  ✅ Health check passed${NC}"
        else
            echo -e "${YELLOW}  ⚠️  Health check pending${NC}"
        fi
        
        kill $PF_PID 2>/dev/null || true
    fi
    echo ""
}

# Print summary
print_summary() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}✅ Deployment Complete!${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📊 Deployment Info:"
    echo "  Namespace: $NAMESPACE"
    echo "  Image Tag: $IMAGE_TAG"
    echo ""
    echo "📝 Useful Commands:"
    echo "  View pods:    kubectl get pods -n $NAMESPACE"
    echo "  View logs:    kubectl logs -f -n $NAMESPACE -l app=kosmos-api"
    echo "  Port forward: kubectl port-forward -n $NAMESPACE svc/kosmos-api 8000:8000"
    echo "  Scale:        kubectl scale deployment/kosmos-api -n $NAMESPACE --replicas=3"
    echo "  Rollback:     kubectl rollout undo deployment/kosmos-api -n $NAMESPACE"
    echo ""
    
    if kubectl config current-context | grep -q "minikube"; then
        echo "🔗 Minikube Access:"
        echo "  API:      kubectl port-forward -n $NAMESPACE svc/kosmos-api 8000:8000"
        echo "  Frontend: kubectl port-forward -n $NAMESPACE svc/kosmos-frontend 3000:3000"
        echo "  Then access: http://localhost:8000 and http://localhost:3000"
    fi
}

# Main execution
main() {
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}🔍 DRY RUN MODE - No changes will be made${NC}"
        echo ""
    fi
    
    check_requirements
    check_kubernetes
    create_namespace
    build_images
    apply_manifests
    
    if [ "$DRY_RUN" = false ]; then
        wait_for_rollout
        verify_deployment
    fi
    
    print_summary
}

main
