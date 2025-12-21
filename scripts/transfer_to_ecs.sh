#!/bin/bash
# Client-side transfer script
# Usage: ./scripts/transfer_to_ecs.sh <SSH_KEY_PATH>

SSH_KEY=$1
USER="root"
HOST="47.91.123.78"

if [ -z "$SSH_KEY" ]; then
    echo "Usage: $0 <SSH_KEY_PATH>"
    exit 1
fi

echo "🚀 Starting Artifact Transfer to $HOST..."

# Transfer Tarballs
echo "📦 Transferring Backend Image..."
scp -i "$SSH_KEY" kosmos-backend-v1.0.0.tar $USER@$HOST:~/

echo "📦 Transferring Frontend Image..."
scp -i "$SSH_KEY" kosmos-frontend-v1.0.0.tar $USER@$HOST:~/

# Transfer Configs
echo "📂 Transferring Kubernetes Manifests..."
scp -i "$SSH_KEY" -r k8s/ $USER@$HOST:~/

# Transfer Deployment Script
echo "📜 Transferring Deployment Script..."
scp -i "$SSH_KEY" scripts/deploy_to_ecs.sh $USER@$HOST:~/

echo "✅ Transfer Complete!"
echo "👉 Now SSH into the server and run: ./deploy_to_ecs.sh"
echo "   ssh -i $SSH_KEY $USER@$HOST"
