#!/bin/bash
# Transfer artifacts to ECS using Aliyun OSS and Cloud Assistant
# Usage: ./scripts/transfer_via_aliyun.sh <OSS_BUCKET_NAME> <ECS_INSTANCE_ID> <REGION_ID>

BUCKET_NAME=$1
INSTANCE_ID=$2
REGION_ID=$3

if [ -z "$BUCKET_NAME" ] || [ -z "$INSTANCE_ID" ] || [ -z "$REGION_ID" ]; then
    echo "Usage: $0 <OSS_BUCKET_NAME> <ECS_INSTANCE_ID> <REGION_ID>"
    echo "Example: $0 kosmos-artifacts i-eb3ce85peqozeocmrwtd me-east-1"
    exit 1
fi

echo "🚀 Starting Artifact Transfer via Aliyun OSS..."

# 0. Prepare k8s.tar
echo "📦 Packaging k8s manifests..."
tar -cvf k8s.tar k8s/

# 1. Upload to OSS
echo "☁️ Uploading artifacts to OSS bucket: $BUCKET_NAME..."
aliyun ossutil cp kosmos-backend-v1.0.0.tar oss://$BUCKET_NAME/ -f
aliyun ossutil cp kosmos-frontend-v1.0.0.tar oss://$BUCKET_NAME/ -f
aliyun ossutil cp k8s.tar oss://$BUCKET_NAME/ -f
aliyun ossutil cp scripts/deploy_to_ecs.sh oss://$BUCKET_NAME/deploy_to_ecs.sh -f

echo "✅ Upload complete."

# 2. Generate Signed URLs
echo "🔑 Generating signed URLs..."
URL_BACKEND=$(aliyun ossutil sign oss://$BUCKET_NAME/kosmos-backend-v1.0.0.tar --expires-duration 1h)
URL_FRONTEND=$(aliyun ossutil sign oss://$BUCKET_NAME/kosmos-frontend-v1.0.0.tar --expires-duration 1h)
URL_K8S=$(aliyun ossutil sign oss://$BUCKET_NAME/k8s.tar --expires-duration 1h)
URL_SCRIPT=$(aliyun ossutil sign oss://$BUCKET_NAME/deploy_to_ecs.sh --expires-duration 1h)

# 3. Create Download & Deploy Script for Cloud Assistant
echo "📜 Generating Cloud Assistant command..."

COMMAND_CONTENT='#!/bin/bash
cd /root
echo "⬇️ Downloading artifacts from OSS using signed URLs..."

wget "'"$URL_BACKEND"'" -O kosmos-backend-v1.0.0.tar
wget "'"$URL_FRONTEND"'" -O kosmos-frontend-v1.0.0.tar
wget "'"$URL_K8S"'" -O k8s.tar
wget "'"$URL_SCRIPT"'" -O deploy_to_ecs.sh

echo "📦 Extracting k8s manifests..."
tar -xf k8s.tar

chmod +x deploy_to_ecs.sh
./deploy_to_ecs.sh
'

# Encode command in Base64
COMMAND_CONTENT_B64=$(echo "$COMMAND_CONTENT" | base64 -w 0)

# 4. Invoke Command on ECS
echo "⚡ Invoking deployment on ECS instance: $INSTANCE_ID..."
aliyun ecs RunCommand     --RegionId $REGION_ID     --InstanceId.1 $INSTANCE_ID     --Type RunShellScript     --Name "DeployKosmosV1"     --ContentEncoding Base64     --CommandContent "$COMMAND_CONTENT_B64"

echo "✅ Command invoked. Check ECS console for execution results."
