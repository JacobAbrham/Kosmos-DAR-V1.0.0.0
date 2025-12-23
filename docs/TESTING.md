# KOSMOS Testing Guide

Comprehensive guide to testing the KOSMOS AI-Native Enterprise Operating System.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Types](#test-types)
- [Writing Tests](#writing-tests)
- [Test Coverage](#test-coverage)
- [Continuous Integration](#continuous-integration)

---

## Overview

KOSMOS employs a comprehensive testing strategy with multiple test levels:

```
┌─────────────────────────────────────────┐
│         End-to-End Tests (E2E)          │  ← Full system testing
├─────────────────────────────────────────┤
│       Integration Tests                 │  ← Multi-component testing
├─────────────────────────────────────────┤
│          Unit Tests                     │  ← Individual component testing
├─────────────────────────────────────────┤
│      Performance Tests                  │  ← Load and stress testing
├─────────────────────────────────────────┤
│       Security Tests                    │  ← Vulnerability scanning
└─────────────────────────────────────────┘
```

**Test Statistics:**

- Total Tests: 150+
- Unit Tests: 80+
- Integration Tests: 50+
- E2E Tests: 20+
- Coverage Target: 80%+

---

## Test Structure

```
tests/
├── unit/                       # Unit tests
│   ├── test_agents/           # Agent unit tests
│   ├── test_services/         # Service unit tests
│   └── test_utils/            # Utility function tests
├── integration/               # Integration tests
│   ├── test_api_endpoints.py  # API integration tests
│   ├── test_database.py       # Database integration
│   └── test_mcp_servers.py    # MCP server integration
├── e2e/                       # End-to-end tests
│   ├── test_frontend.py       # Frontend E2E tests
│   └── test_workflows.py      # Complete workflow tests
├── performance/               # Performance tests
│   ├── load_test.py          # Load testing
│   └── stress_test.py        # Stress testing
├── smoke/                     # Smoke tests
│   └── test_basic.py         # Basic functionality checks
├── fixtures/                  # Test fixtures and data
│   ├── sample_data.py
│   └── mock_responses.py
├── conftest.py               # Pytest configuration
└── README.md                 # This file (moved to docs/)
```

---

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Or use make
make setup
```

### Run All Tests

```bash
# Using pytest
pytest

# Using make
make test

# With coverage
make test-coverage
```

### Run Specific Test Types

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# E2E tests only
pytest tests/e2e/

# Smoke tests only
pytest tests/smoke/
```

### Run Specific Test Files

```bash
# Single test file
pytest tests/unit/test_agents/test_zeus.py

# Single test function
pytest tests/unit/test_agents/test_zeus.py::test_zeus_initialization

# Tests matching pattern
pytest -k "test_auth"
```

### Run Tests with Options

```bash
# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run in parallel (faster)
pytest -n auto

# Generate HTML report
pytest --html=report.html --self-contained-html
```

---

## Test Types

### 1. Unit Tests

Test individual components in isolation.

**Example: Testing Zeus Agent**

```python
# tests/unit/test_agents/test_zeus.py
import pytest
from src.agents.zeus.main import ZeusAgent

@pytest.fixture
def zeus_agent():
    """Create a Zeus agent for testing."""
    return ZeusAgent()

def test_zeus_initialization(zeus_agent):
    """Test that Zeus initializes correctly."""
    assert zeus_agent.name == "zeus"
    assert zeus_agent.version == "2.0.0"
    assert zeus_agent.llm is not None

def test_zeus_route_query(zeus_agent):
    """Test query routing logic."""
    query = "What is our security policy?"
    result = zeus_agent.route_query(query)
    
    assert result["agent"] == "aegis"
    assert "security" in result["reasoning"].lower()

def test_zeus_pentarchy_decision(zeus_agent):
    """Test Pentarchy governance voting."""
    proposal = {
        "action": "purchase",
        "amount": 75.00,
        "description": "Buy API credits"
    }
    
    result = zeus_agent.pentarchy_vote(proposal)
    
    assert "votes" in result
    assert len(result["votes"]) == 3
    assert result["decision"] in ["APPROVED", "REJECTED"]
```

**Run unit tests:**

```bash
pytest tests/unit/ -v
```

### 2. Integration Tests

Test multiple components working together.

**Example: Testing API Endpoints**

```python
# tests/integration/test_api_endpoints.py
import pytest
import httpx
from src.main import app

@pytest.fixture
async def client():
    """Create async HTTP client."""
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def auth_token():
    """Get authentication token for testing."""
    # In real tests, this would authenticate properly
    return "test_token_12345"

@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Test health check endpoint."""
    response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_chat_endpoint(client, auth_token):
    """Test chat endpoint with authentication."""
    response = await client.post(
        "/api/v1/chat/message",
        json={"content": "What is KOSMOS?"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert "conversation_id" in data

@pytest.mark.asyncio
async def test_agent_query(client, auth_token):
    """Test agent query endpoint."""
    response = await client.post(
        "/api/v1/agents/zeus/query",
        json={"query": "Route this to the security agent"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["routed_to"] == "aegis"
```

**Run integration tests:**

```bash
pytest tests/integration/ -v
```

### 3. End-to-End Tests

Test complete user workflows.

**Example: Frontend E2E Test**

```python
# tests/e2e/test_frontend.py
import pytest
from playwright.sync_api import Page, expect

def test_chat_workflow(page: Page):
    """Test complete chat workflow."""
    # Navigate to chat page
    page.goto("http://localhost:3000")
    
    # Verify page loaded
    expect(page.get_by_text("KOSMOS")).to_be_visible()
    
    # Send a message
    message_input = page.get_by_placeholder("Type your message")
    message_input.fill("What is the company policy?")
    page.get_by_role("button", name="Send").click()
    
    # Wait for response
    expect(page.get_by_text("Athena")).to_be_visible()
    
    # Verify message appears in history
    expect(page.get_by_text("What is the company policy?")).to_be_visible()

def test_pentarchy_voting(page: Page):
    """Test Pentarchy voting workflow."""
    page.goto("http://localhost:3000")
    
    # Type vote command
    message_input = page.get_by_placeholder("Type your message")
    message_input.fill("/vote Buy $75 API credits")
    page.get_by_role("button", name="Send").click()
    
    # Wait for voting UI
    expect(page.get_by_text("Pentarchy Vote")).to_be_visible()
    expect(page.get_by_text("Nur PROMETHEUS")).to_be_visible()
    expect(page.get_by_text("Hephaestus")).to_be_visible()
    expect(page.get_by_text("Athena")).to_be_visible()
    
    # Verify vote results
    expect(page.get_by_text(/APPROVED|REJECTED/)).to_be_visible()
```

**Run E2E tests:**

```bash
# Start services first
make dev

# Run tests
pytest tests/e2e/ -v
```

### 4. Performance Tests

Test system performance and scalability.

**Example: Load Test**

```python
# tests/performance/load_test.py
from locust import HttpUser, task, between
import json

class KosmosUser(HttpUser):
    """Simulated user for load testing."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Login before starting tests."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "loadtest@example.com",
                "password": "testpassword"
            }
        )
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(10)  # Weight: 10
    def send_message(self):
        """Test chat endpoint."""
        self.client.post(
            "/api/v1/chat/message",
            json={"content": "What is KOSMOS?"},
            headers=self.headers
        )
    
    @task(5)  # Weight: 5
    def query_agent(self):
        """Test agent query endpoint."""
        self.client.post(
            "/api/v1/agents/zeus/query",
            json={"query": "Route this query"},
            headers=self.headers
        )
    
    @task(1)  # Weight: 1
    def create_proposal(self):
        """Test voting endpoint."""
        self.client.post(
            "/api/v1/votes/proposals",
            json={
                "action": "purchase",
                "amount": 50.00,
                "description": "Test proposal"
            },
            headers=self.headers
        )
```

**Run performance tests:**

```bash
# Using locust
locust -f tests/performance/load_test.py

# Then open http://localhost:8089 in browser
```

---

## Writing Tests

### Best Practices

1. **Follow AAA Pattern** (Arrange, Act, Assert)

```python
def test_example():
    # Arrange: Set up test data
    agent = ZeusAgent()
    query = "test query"
    
    # Act: Perform the action
    result = agent.route_query(query)
    
    # Assert: Verify the outcome
    assert result["agent"] in ["hermes", "athena", "aegis"]
```

1. **Use Descriptive Names**

```python
# Good
def test_zeus_routes_security_queries_to_aegis():
    ...

# Bad
def test_routing():
    ...
```

1. **Test One Thing Per Test**

```python
# Good: Separate tests for different behaviors
def test_authentication_with_valid_credentials():
    ...

def test_authentication_with_invalid_credentials():
    ...

# Bad: Testing multiple things
def test_authentication():
    # Tests both valid and invalid cases
    ...
```

1. **Use Fixtures for Setup**

```python
@pytest.fixture
def authenticated_client():
    """Create authenticated test client."""
    client = TestClient(app)
    token = get_test_token()
    client.headers = {"Authorization": f"Bearer {token}"}
    return client
```

1. **Mock External Dependencies**

```python
@pytest.fixture
def mock_llm_service(monkeypatch):
    """Mock LLM service to avoid API calls."""
    def mock_generate(*args, **kwargs):
        return {"content": "mocked response"}
    
    monkeypatch.setattr("src.services.llm_service.generate", mock_generate)
```

### Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_unit_example():
    ...

@pytest.mark.integration
def test_integration_example():
    ...

@pytest.mark.slow
def test_slow_operation():
    ...

@pytest.mark.skip(reason="Feature not implemented yet")
def test_future_feature():
    ...
```

Run specific markers:

```bash
pytest -m unit          # Run only unit tests
pytest -m "not slow"    # Skip slow tests
```

---

## Test Coverage

### Generate Coverage Report

```bash
# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html
```

### Coverage Targets

| Component | Target | Current |
|-----------|--------|---------|
| Agents | 80%+ | 85% |
| API | 85%+ | 88% |
| Services | 80%+ | 82% |
| Utilities | 75%+ | 79% |
| **Overall** | **80%+** | **83%** |

### Check Coverage

```bash
# Generate coverage badge
coverage-badge -o coverage.svg

# Fail if coverage below threshold
pytest --cov=src --cov-fail-under=80
```

---

## Continuous Integration

### GitHub Actions Workflow

Tests run automatically on every push and pull request.

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### Pre-commit Hooks

Run tests before committing:

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## Troubleshooting

### Common Issues

**Tests failing with database errors:**

```bash
# Reset test database
docker-compose -f config/environments/development/docker-compose.yml down -v
docker-compose -f config/environments/development/docker-compose.yml up -d
```

**Import errors:**

```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=$PWD:$PYTHONPATH

# Or install package in development mode
pip install -e .
```

**Slow tests:**

```bash
# Run tests in parallel
pytest -n auto

# Skip slow tests during development
pytest -m "not slow"
```

---

## Resources

- **Test Configuration:** [tests/conftest.py](../tests/conftest.py)
- **Testing Strategy:** [docs/03-engineering/testing/README.md](03-engineering/testing/README.md)
- **CI/CD Documentation:** [docs/04-operations/infrastructure/deployment.md](04-operations/infrastructure/deployment.md)
- **Coverage Report:** [Test Coverage Assessment](assessments/TEST_COVERAGE.md)

---

**Last Updated:** December 2025  
**Version:** 1.0.0
