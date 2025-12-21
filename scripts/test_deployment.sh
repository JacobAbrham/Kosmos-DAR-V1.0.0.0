#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:8000"

echo -e "${BLUE}=== KOSMOS Deployment Verification ===${NC}"

# 1. Check Health
echo -e "\n${BLUE}[1] Checking API Health...${NC}"
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/health)
if [ "$HEALTH_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✅ API is Healthy (200 OK)${NC}"
else
    echo -e "❌ API Health Check Failed (Status: $HEALTH_RESPONSE)"
    echo "Make sure port-forwarding is active: kubectl port-forward svc/kosmos-backend 8000:8000"
    exit 1
fi

# 2. Test Simple Task (Routing to Hugging Face)
echo -e "\n${BLUE}[2] Testing Simple Task Routing (Should use Hugging Face)...${NC}"
echo "Query: 'Summarize this: Hello world.'"
SIMPLE_RESPONSE=$(curl -s -X POST "$BASE_URL/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Summarize this: Hello world.", "conversation_id": "test-simple-cli", "user_id": "cli-user"}')

echo "Response: $SIMPLE_RESPONSE"

# 3. Test Complex Task (Routing to OpenAI/Anthropic)
echo -e "\n${BLUE}[3] Testing Complex Task Routing (Should use OpenAI/Anthropic)...${NC}"
echo "Query: 'Architect a microservices system.'"
COMPLEX_RESPONSE=$(curl -s -X POST "$BASE_URL/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Architect a microservices system.", "conversation_id": "test-complex-cli", "user_id": "cli-user"}')

echo "Response: $COMPLEX_RESPONSE"

echo -e "\n${BLUE}=== Verification Complete ===${NC}"
echo "To verify routing decisions, check the logs:"
echo "kubectl logs -l app=kosmos-backend --tail=20"
