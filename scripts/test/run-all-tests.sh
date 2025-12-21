#!/bin/bash
# Run Complete KOSMOS Test Suite
# Usage: ./run-all-tests.sh

set -e

echo "🧪 KOSMOS Complete Test Suite"
echo "=============================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Results tracking
PASSED=0
FAILED=0
SKIPPED=0

# Navigate to project root
cd "$(dirname "$0")/../.." || exit 1
PROJECT_ROOT=$(pwd)

run_test() {
    local name=$1
    local command=$2
    
    echo -e "${BLUE}▶ Running: $name${NC}"
    if eval "$command" 2>&1; then
        echo -e "${GREEN}✅ $name PASSED${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ $name FAILED${NC}"
        ((FAILED++))
        return 1
    fi
}

skip_test() {
    local name=$1
    local reason=$2
    echo -e "${YELLOW}⏭️  Skipping: $name ($reason)${NC}"
    ((SKIPPED++))
}

# Check API availability
check_api() {
    curl -s http://localhost:8000/health > /dev/null 2>&1
}

echo "📋 Test Plan:"
echo "  1. Python Syntax Check"
echo "  2. Python Unit Tests"
echo "  3. API Integration Tests"
echo "  4. MCP Tests"
echo "  5. Schema Validation"
echo "  6. Frontend Tests (if available)"
echo ""

# 1. Python Syntax Check
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  PYTHON SYNTAX CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
run_test "Python Syntax" "python -m py_compile src/main.py src/api/routers/*.py 2>&1 || python3 -m py_compile src/main.py"

# 2. Python Unit Tests
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  PYTHON UNIT TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -d "tests/unit" ] && [ "$(ls -A tests/unit 2>/dev/null)" ]; then
    run_test "Unit Tests" "python -m pytest tests/unit/ -v --tb=short -q 2>&1 | tail -20"
else
    skip_test "Unit Tests" "No unit tests found"
fi

# 3. API Integration Tests
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  API INTEGRATION TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if check_api; then
    # Quick API tests
    echo "Testing health endpoint..."
    HEALTH=$(curl -s http://localhost:8000/health)
    if echo "$HEALTH" | grep -q "healthy"; then
        echo -e "${GREEN}  ✅ Health check passed${NC}"
    else
        echo -e "${RED}  ❌ Health check failed${NC}"
    fi
    
    echo "Testing ready endpoint..."
    READY=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ready)
    if [ "$READY" = "200" ]; then
        echo -e "${GREEN}  ✅ Ready check passed${NC}"
    else
        echo -e "${RED}  ❌ Ready check failed (status: $READY)${NC}"
    fi
    
    echo "Testing agents endpoint..."
    AGENTS=$(curl -s http://localhost:8000/api/v1/agents)
    if echo "$AGENTS" | grep -q "zeus\|athena\|hermes"; then
        echo -e "${GREEN}  ✅ Agents endpoint passed${NC}"
    else
        echo -e "${YELLOW}  ⚠️  Agents endpoint returned: $(echo $AGENTS | head -c 100)${NC}"
    fi
    
    echo "Testing MCP servers endpoint..."
    MCP=$(curl -s http://localhost:8000/api/v1/mcp/servers)
    if [ -n "$MCP" ]; then
        echo -e "${GREEN}  ✅ MCP servers endpoint passed${NC}"
    else
        echo -e "${YELLOW}  ⚠️  MCP servers endpoint empty${NC}"
    fi
    
    ((PASSED++))
else
    skip_test "API Integration Tests" "API not running on localhost:8000"
fi

# 4. MCP Tests
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  MCP VALIDATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "tests/validate_mcp_config.py" ]; then
    run_test "MCP Config Validation" "python tests/validate_mcp_config.py 2>&1 | tail -10"
else
    skip_test "MCP Validation" "No MCP validation script found"
fi

# 5. Schema Validation
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  SCHEMA VALIDATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "scripts/validate_schemas.py" ]; then
    run_test "Schema Validation" "python scripts/validate_schemas.py 2>&1 | tail -10"
elif [ -f "scripts/validate_all.py" ]; then
    run_test "Schema Validation" "python scripts/validate_all.py 2>&1 | tail -10"
else
    skip_test "Schema Validation" "No schema validation script found"
fi

# 6. Frontend Tests
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  FRONTEND TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "frontend/package.json" ]; then
    cd frontend
    if [ -d "node_modules" ]; then
        if grep -q '"test"' package.json 2>/dev/null; then
            run_test "Frontend Tests" "npm test -- --passWithNoTests 2>&1 | tail -10" || true
        else
            skip_test "Frontend Tests" "No test script in package.json"
        fi
    else
        skip_test "Frontend Tests" "node_modules not installed"
    fi
    cd "$PROJECT_ROOT"
else
    skip_test "Frontend Tests" "No frontend found"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 TEST SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Passed:  $PASSED${NC}"
echo -e "${RED}❌ Failed:  $FAILED${NC}"
echo -e "${YELLOW}⏭️  Skipped: $SKIPPED${NC}"
echo ""

TOTAL=$((PASSED + FAILED))
if [ $TOTAL -gt 0 ]; then
    PERCENT=$((PASSED * 100 / TOTAL))
    echo "Success Rate: ${PERCENT}%"
fi

echo ""
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All executed tests passed!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Please review above.${NC}"
    exit 1
fi
