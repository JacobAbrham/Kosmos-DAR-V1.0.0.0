#!/bin/bash
# Configure LLM API Keys for KOSMOS
# Usage: ./configure-llm-keys.sh [.env-file]

set -e

ENV_FILE="${1:-.env}"

echo "🔐 KOSMOS LLM API Key Configuration"
echo "===================================="
echo ""
echo "This script will configure LLM provider API keys."
echo "Leave blank to skip a provider."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Validation functions
validate_openai_key() {
    [[ $1 =~ ^sk-[a-zA-Z0-9_-]{20,}$ ]] || [[ $1 =~ ^sk-proj-[a-zA-Z0-9_-]{20,}$ ]]
}

validate_anthropic_key() {
    [[ $1 =~ ^sk-ant-[a-zA-Z0-9_-]{20,}$ ]]
}

# Function to update .env
update_env_var() {
    local key=$1
    local value=$2
    local file=$3
    
    if [ -z "$value" ]; then
        return
    fi
    
    # Create file if it doesn't exist
    touch "$file"
    
    # Update or add the variable
    if grep -q "^${key}=" "$file" 2>/dev/null; then
        sed -i "s|^${key}=.*|${key}=${value}|" "$file"
    else
        echo "${key}=${value}" >> "$file"
    fi
}

# OpenAI Configuration
echo -e "${YELLOW}OpenAI Configuration${NC}"
echo "Get your API key at: https://platform.openai.com/api-keys"
read -p "Enter OpenAI API Key (or press Enter to skip): " -s OPENAI_KEY
echo ""

if [ -n "$OPENAI_KEY" ]; then
    if validate_openai_key "$OPENAI_KEY"; then
        echo -e "${GREEN}✅ OpenAI key format valid${NC}"
        update_env_var "OPENAI_API_KEY" "$OPENAI_KEY" "$ENV_FILE"
    else
        echo -e "${YELLOW}⚠️  Warning: OpenAI key format may be invalid${NC}"
        update_env_var "OPENAI_API_KEY" "$OPENAI_KEY" "$ENV_FILE"
    fi
fi
echo ""

# Anthropic Configuration
echo -e "${YELLOW}Anthropic Configuration${NC}"
echo "Get your API key at: https://console.anthropic.com/settings/keys"
read -p "Enter Anthropic API Key (or press Enter to skip): " -s ANTHROPIC_KEY
echo ""

if [ -n "$ANTHROPIC_KEY" ]; then
    if validate_anthropic_key "$ANTHROPIC_KEY"; then
        echo -e "${GREEN}✅ Anthropic key format valid${NC}"
        update_env_var "ANTHROPIC_API_KEY" "$ANTHROPIC_KEY" "$ENV_FILE"
    else
        echo -e "${YELLOW}⚠️  Warning: Anthropic key format may be invalid${NC}"
        update_env_var "ANTHROPIC_API_KEY" "$ANTHROPIC_KEY" "$ENV_FILE"
    fi
fi
echo ""

# Google AI Configuration
echo -e "${YELLOW}Google AI Configuration${NC}"
echo "Get your API key at: https://aistudio.google.com/apikey"
read -p "Enter Google AI API Key (or press Enter to skip): " -s GOOGLE_KEY
echo ""

if [ -n "$GOOGLE_KEY" ]; then
    update_env_var "GOOGLE_API_KEY" "$GOOGLE_KEY" "$ENV_FILE"
    echo -e "${GREEN}✅ Google AI key saved${NC}"
fi
echo ""

# Select default provider
echo -e "${YELLOW}Select Default LLM Provider:${NC}"
echo "  1) OpenAI (GPT-4o) - Best overall quality"
echo "  2) Anthropic (Claude) - Best for reasoning"
echo "  3) Google (Gemini) - Best value"
echo "  4) Ollama (Local) - Free, runs locally"
read -p "Enter choice [1-4, default=1]: " PROVIDER_CHOICE

case $PROVIDER_CHOICE in
    1|"") DEFAULT_PROVIDER="openai" ;;
    2) DEFAULT_PROVIDER="anthropic" ;;
    3) DEFAULT_PROVIDER="google" ;;
    4) DEFAULT_PROVIDER="ollama" ;;
    *) DEFAULT_PROVIDER="openai" ;;
esac

update_env_var "LLM_DEFAULT_PROVIDER" "$DEFAULT_PROVIDER" "$ENV_FILE"

echo ""
echo -e "${GREEN}✅ LLM configuration complete!${NC}"
echo ""
echo "Configuration saved to: $ENV_FILE"
echo ""
echo "Configured providers:"
[ -n "$OPENAI_KEY" ] && echo "  • OpenAI: ✅"
[ -n "$ANTHROPIC_KEY" ] && echo "  • Anthropic: ✅"
[ -n "$GOOGLE_KEY" ] && echo "  • Google: ✅"
echo "  • Default: $DEFAULT_PROVIDER"
echo ""
echo "🔄 Restart services to apply changes:"
echo "   docker compose restart api"
