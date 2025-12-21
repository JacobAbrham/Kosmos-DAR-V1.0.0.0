#!/bin/bash
# Initialize HashiCorp Vault with KOSMOS secrets
# Usage: ./init-vault.sh

set -e

VAULT_ADDR="${VAULT_ADDR:-http://localhost:8200}"
VAULT_TOKEN="${VAULT_TOKEN:-kosmos-dev-token}"

echo "🔐 KOSMOS Vault Initialization"
echo "=============================="
echo "Vault Address: $VAULT_ADDR"
echo ""

export VAULT_ADDR
export VAULT_TOKEN

# Wait for Vault to be ready
echo "⏳ Waiting for Vault to be ready..."
for i in {1..30}; do
    if curl -s "$VAULT_ADDR/v1/sys/health" > /dev/null 2>&1; then
        echo "✅ Vault is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Vault failed to start"
        exit 1
    fi
    sleep 1
done

# Check if vault CLI is available, otherwise use curl
if command -v vault &> /dev/null; then
    USE_CLI=true
else
    USE_CLI=false
    echo "ℹ️  Vault CLI not found, using curl"
fi

# Enable KV secrets engine
echo ""
echo "📦 Enabling KV secrets engine..."
if [ "$USE_CLI" = true ]; then
    vault secrets enable -path=kosmos kv-v2 2>/dev/null || echo "  Already enabled"
else
    curl -s -X POST \
        -H "X-Vault-Token: $VAULT_TOKEN" \
        -d '{"type": "kv-v2"}' \
        "$VAULT_ADDR/v1/sys/mounts/kosmos" 2>/dev/null || echo "  Already enabled"
fi

# Store LLM secrets
echo ""
echo "🤖 Storing LLM secrets..."
LLM_DATA=$(cat <<EOF
{
  "data": {
    "openai_api_key": "${OPENAI_API_KEY:-sk-dev-placeholder}",
    "anthropic_api_key": "${ANTHROPIC_API_KEY:-sk-ant-dev-placeholder}",
    "google_api_key": "${GOOGLE_API_KEY:-}",
    "default_provider": "${LLM_DEFAULT_PROVIDER:-openai}"
  }
}
EOF
)

curl -s -X POST \
    -H "X-Vault-Token: $VAULT_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$LLM_DATA" \
    "$VAULT_ADDR/v1/kosmos/data/llm" > /dev/null

echo "  ✅ LLM secrets stored"

# Store Database secrets
echo "🗄️  Storing database secrets..."
DB_DATA=$(cat <<EOF
{
  "data": {
    "host": "${POSTGRES_HOST:-localhost}",
    "port": "${POSTGRES_PORT:-5432}",
    "database": "${POSTGRES_DB:-kosmos}",
    "username": "${POSTGRES_USER:-kosmos}",
    "password": "${POSTGRES_PASSWORD:-kosmos_secret}"
  }
}
EOF
)

curl -s -X POST \
    -H "X-Vault-Token: $VAULT_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$DB_DATA" \
    "$VAULT_ADDR/v1/kosmos/data/database" > /dev/null

echo "  ✅ Database secrets stored"

# Store Redis secrets
echo "📮 Storing Redis secrets..."
REDIS_DATA=$(cat <<EOF
{
  "data": {
    "host": "${REDIS_HOST:-localhost}",
    "port": "${REDIS_PORT:-6379}",
    "password": "${REDIS_PASSWORD:-}"
  }
}
EOF
)

curl -s -X POST \
    -H "X-Vault-Token: $VAULT_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$REDIS_DATA" \
    "$VAULT_ADDR/v1/kosmos/data/redis" > /dev/null

echo "  ✅ Redis secrets stored"

# Store Auth secrets
echo "🔑 Storing auth secrets..."
JWT_SECRET="${JWT_SECRET:-$(openssl rand -hex 32 2>/dev/null || head -c 32 /dev/urandom | xxd -p)}"
AUTH_DATA=$(cat <<EOF
{
  "data": {
    "jwt_secret": "$JWT_SECRET",
    "jwt_expiry_hours": "${JWT_EXPIRY_HOURS:-24}"
  }
}
EOF
)

curl -s -X POST \
    -H "X-Vault-Token: $VAULT_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$AUTH_DATA" \
    "$VAULT_ADDR/v1/kosmos/data/auth" > /dev/null

echo "  ✅ Auth secrets stored"

# Store MinIO secrets
echo "📁 Storing MinIO secrets..."
MINIO_DATA=$(cat <<EOF
{
  "data": {
    "endpoint": "${MINIO_ENDPOINT:-localhost:9000}",
    "access_key": "${MINIO_ACCESS_KEY:-kosmos}",
    "secret_key": "${MINIO_SECRET_KEY:-kosmos_secret}"
  }
}
EOF
)

curl -s -X POST \
    -H "X-Vault-Token: $VAULT_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$MINIO_DATA" \
    "$VAULT_ADDR/v1/kosmos/data/minio" > /dev/null

echo "  ✅ MinIO secrets stored"

# Verify secrets
echo ""
echo "🔍 Verifying secrets..."
PATHS=("llm" "database" "redis" "auth" "minio")
for path in "${PATHS[@]}"; do
    RESULT=$(curl -s -H "X-Vault-Token: $VAULT_TOKEN" "$VAULT_ADDR/v1/kosmos/data/$path" | grep -c "data" || echo "0")
    if [ "$RESULT" -gt 0 ]; then
        echo "  ✅ kosmos/$path"
    else
        echo "  ❌ kosmos/$path - failed"
    fi
done

echo ""
echo "=============================="
echo "✅ Vault initialization complete!"
echo ""
echo "Access Vault UI: $VAULT_ADDR/ui"
echo "Token: $VAULT_TOKEN"
echo ""
echo "To use in your app, set:"
echo "  export VAULT_ADDR=$VAULT_ADDR"
echo "  export VAULT_TOKEN=$VAULT_TOKEN"
