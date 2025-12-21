#!/bin/bash
# Server-side deployment script for Kosmos
# Run this ON the ECS instance

echo "🚀 Starting Kosmos Production Deployment..."

# 1. Import Docker Images
echo "📦 Importing Docker images..."
if [ -f "kosmos-backend-v1.0.0.tar" ]; then
    sudo k3s ctr images import kosmos-backend-v1.0.0.tar
    echo "✅ Backend image imported."
else
    echo "❌ Backend tarball not found!"
fi

if [ -f "kosmos-frontend-v1.0.0.tar" ]; then
    sudo k3s ctr images import kosmos-frontend-v1.0.0.tar
    echo "✅ Frontend image imported."
else
    echo "❌ Frontend tarball not found!"
fi

# 2. Apply Kubernetes Manifests
echo "☸️ Applying Kubernetes manifests..."
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/database.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml

# 3. Restart Deployments to pick up new images
echo "🔄 Restarting deployments..."
kubectl rollout restart deployment/kosmos-backend
kubectl rollout restart deployment/kosmos-frontend

# 4. Verify Status
echo "🔍 Checking cluster status..."
kubectl get pods

echo "✅ Deployment sequence complete!"
