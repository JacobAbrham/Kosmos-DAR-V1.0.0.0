# Testing Strategy

**Comprehensive Testing for AI-Native Systems**

!!! abstract "Quality Assurance"
    KOSMOS implements a multi-layer testing strategy covering unit, integration, contract, and end-to-end tests with specific considerations for LLM-based components.

---

## Testing Pyramid

```
                    ┌─────────┐
                    │   E2E   │  10%
                    │  Tests  │
                ┌───┴─────────┴───┐
                │   Integration   │  20%
                │     Tests       │
            ┌───┴─────────────────┴───┐
            │      Contract Tests     │  10%
            │      (Agent ↔ MCP)      │
        ┌───┴─────────────────────────┴───┐
        │          Unit Tests             │  60%
        │     (Functions, Classes)        │
        └─────────────────────────────────┘
```

---

## Coverage Targets

| Layer | Target | Current | Tool |
|-------|--------|---------|------|
| Unit | 80% | - | pytest-cov |
| Integration | 60% | - | pytest |
| Contract | 100% MCP | - | pact-python |
| E2E | Critical paths | - | Playwright |

---

## Test Categories

### 1. Unit Tests

Test individual functions and classes in isolation.

```python
# tests/unit/agents/test_zeus_router.py
import pytest
from agents.zeus.router import route_task

class TestZeusRouter:
    def test_routes_calendar_to_chronos(self):
        result = route_task("Schedule meeting for tomorrow")
        assert result.agent == "chronos"
        assert result.confidence > 0.8
    
    def test_routes_email_to_hermes(self):
        result = route_task("Send email to team")
        assert result.agent == "hermes"
    
    def test_handles_ambiguous_input(self):
        result = route_task("do something")
        assert result.requires_clarification is True
```

**Location:** `tests/unit/`  
**Naming:** `test_{module}.py`  
**Run:** `pytest tests/unit/ -v`

---

### 2. Integration Tests

Test component interactions with real dependencies.

```python
# tests/integration/test_agent_mcp_integration.py
import pytest
from agents.chronos import ChronosAgent
from mcp.calendar import CalendarMCP

@pytest.fixture
def chronos_with_mcp(mcp_calendar_server):
    agent = ChronosAgent()
    agent.connect_mcp(mcp_calendar_server)
    return agent

class TestChronosMCPIntegration:
    async def test_creates_calendar_event(self, chronos_with_mcp):
        result = await chronos_with_mcp.execute(
            "Schedule team standup for Monday 9am"
        )
        assert result.success is True
        assert result.event_id is not None
    
    async def test_handles_mcp_timeout(self, chronos_with_mcp):
        with pytest.raises(MCPTimeoutError):
            await chronos_with_mcp.execute(
                "Create event",
                timeout=0.001  # Force timeout
            )
```

**Location:** `tests/integration/`  
**Fixtures:** `tests/conftest.py`  
**Run:** `pytest tests/integration/ -v --tb=short`

---

### 3. Contract Tests

Verify Agent ↔ MCP protocol compliance.

```python
# tests/contract/test_mcp_calendar_contract.py
from pact import Consumer, Provider

class TestCalendarMCPContract:
    @pytest.fixture
    def pact(self):
        return Consumer('ChronosAgent').has_pact_with(
            Provider('CalendarMCP'),
            pact_dir='./pacts'
        )
    
    def test_create_event_contract(self, pact):
        expected = {
            "tool": "create_event",
            "parameters": {
                "title": Like("string"),
                "start_time": Like("2025-12-14T09:00:00Z"),
                "duration_minutes": Like(60)
            }
        }
        
        pact.given("calendar is available") \
            .upon_receiving("create event request") \
            .with_request("POST", "/tools/create_event") \
            .will_respond_with(200, body=expected)
```

**Location:** `tests/contract/`  
**Output:** `pacts/*.json`  
**Run:** `pytest tests/contract/ && pact-verifier`

---

### 4. End-to-End Tests

Test complete user workflows.

```python
# tests/e2e/test_user_workflows.py
from playwright.sync_api import Page, expect

class TestUserWorkflows:
    def test_schedule_meeting_workflow(self, page: Page):
        # Login
        page.goto("/login")
        page.fill("[name=email]", "qa.tester@nuvanta-holding.com")
        page.click("button[type=submit]")
        
        # Issue command
        page.fill("#command-input", "Schedule team meeting tomorrow 2pm")
        page.press("#command-input", "Enter")
        
        # Verify response
        expect(page.locator(".agent-response")).to_contain_text(
            "Meeting scheduled"
        )
        expect(page.locator(".calendar-event")).to_be_visible()
```

**Location:** `tests/e2e/`  
**Run:** `playwright test`

---

## LLM-Specific Testing

### Prompt Regression Tests

```python
# tests/llm/test_prompt_regression.py
from langfuse import Langfuse

class TestPromptRegression:
    @pytest.fixture
    def langfuse(self):
        return Langfuse()
    
    def test_routing_prompt_consistency(self, langfuse):
        test_cases = [
            ("Schedule a meeting", "chronos"),
            ("Send an email", "hermes"),
            ("Find document about Q3", "athena"),
        ]
        
        for input_text, expected_agent in test_cases:
            result = invoke_zeus_routing(input_text)
            
            # Log to Langfuse for tracking
            langfuse.score(
                trace_id=result.trace_id,
                name="routing_accuracy",
                value=1 if result.agent == expected_agent else 0
            )
            
            assert result.agent == expected_agent
```

### Output Quality Tests

```python
# tests/llm/test_output_quality.py
class TestOutputQuality:
    def test_response_contains_no_hallucinations(self):
        response = invoke_athena("What is in document X?")
        
        # Verify all claims are grounded in retrieved context
        for claim in extract_claims(response):
            assert claim.source_document is not None
    
    def test_response_follows_format(self):
        response = invoke_hermes("Draft email to team")
        
        assert "Subject:" in response
        assert "Dear" in response or "Hi" in response
```

---

## Test Fixtures

### Database Fixtures

```python
# tests/conftest.py
import pytest
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg.get_connection_url()

@pytest.fixture
def db_session(postgres):
    engine = create_engine(postgres)
    with Session(engine) as session:
        yield session
        session.rollback()
```

### MCP Server Fixtures

```python
@pytest.fixture
def mcp_calendar_server():
    server = MockMCPServer(spec="mcp-calendar")
    server.start()
    yield server
    server.stop()
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      
      - name: Run unit tests
        run: pytest tests/unit/ -v --cov=src --cov-report=xml
      
      - name: Run integration tests
        run: pytest tests/integration/ -v
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

---

## Test Commands

```bash
# All tests
pytest

# Unit only (fast)
pytest tests/unit/ -v

# Integration only
pytest tests/integration/ -v

# With coverage
pytest --cov=src --cov-report=html

# Specific marker
pytest -m "slow" -v

# Parallel execution
pytest -n auto
```

---

## See Also

- [Testing Fixtures](testing/fixtures.md)
- [LLM Testing Guide](testing/llm-testing.md)
- [API Design](api-design.md)

---

**Last Updated:** December 2025
