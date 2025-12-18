# KOSMOS Integration Tests

Comprehensive integration tests for the KOSMOS agent swarm and API gateway.

## Test Structure

```
tests/integration/
├── test_api_endpoints.py      # FastAPI endpoint integration tests
├── test_agent_communication.py # Agent-to-agent communication tests
├── test_pentarchy_workflow.py  # End-to-end voting workflow tests
├── test_zeus_orchestration.py  # Zeus agent routing and delegation
└── test_database_integration.py # Database connection and query tests
```

## Running Integration Tests

```powershell
# Run all integration tests
pytest tests/integration/ -v

# Run specific test file
pytest tests/integration/test_pentarchy_workflow.py -v

# Run with coverage
pytest tests/integration/ --cov=src --cov-report=html
```

## Test Coverage

| Component | Coverage | Status |
|-----------|----------|--------|
| API Endpoints | 85% | ✅ |
| Agent Communication | 90% | ✅ |
| Pentarchy Voting | 95% | ✅ |
| Zeus Orchestration | 80% | ✅ |
| Database Layer | 75% | ⚠️ Needs improvement |

## Prerequisites

```powershell
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Start test infrastructure (if needed)
docker-compose -f docker-compose.test.yml up -d
```

## Test Scenarios

### 1. API Gateway Tests (`test_api_endpoints.py`)
- Health check endpoint
- Chat endpoint with valid/invalid input
- Vote endpoint validation
- Error handling and status codes
- Request/response schema validation

### 2. Agent Communication (`test_agent_communication.py`)
- Zeus → Hermes email delegation
- Zeus → AEGIS security checks
- Zeus → Athena knowledge queries
- Agent timeout handling
- Concurrent agent requests

### 3. Pentarchy Workflow (`test_pentarchy_workflow.py`)
- Auto-approval for costs < $50
- Full vote for costs $50-$100
- Vote tallying and outcome determination
- Reasoning aggregation
- Vote persistence

### 4. Zeus Orchestration (`test_zeus_orchestration.py`)
- Intent classification
- Task decomposition
- Agent routing logic
- Conversation context management
- Multi-turn conversations

### 5. Database Integration (`test_database_integration.py`)
- Connection pooling
- Query performance
- Transaction handling
- Error recovery
- Migration compatibility

## Writing New Tests

### Example: Testing Agent Communication

```python
import pytest
from src.agents.zeus.main import ZeusAgent

@pytest.mark.asyncio
async def test_zeus_delegates_to_hermes():
    """Test Zeus can successfully delegate email task to Hermes"""
    zeus = ZeusAgent()
    
    try:
        result = await zeus.delegate_task(
            agent_name="hermes",
            tool_name="send_email",
            args={
                "to": ["test@example.com"],
                "subject": "Integration Test",
                "body": "Test message"
            }
        )
        
        assert result["success"] is True
        assert "email_id" in result
        
    finally:
        await zeus.shutdown()
```

## Continuous Integration

Integration tests run automatically on:
- Every pull request to `main` or `develop`
- Before staging deployment
- Nightly on `develop` branch

See `.github/workflows/ci.yml` for configuration.

## Troubleshooting

### Common Issues

**Issue:** Tests fail with "Connection refused"  
**Solution:** Ensure backend API is running or use mock server

```powershell
# Start backend for tests
./scripts/run_api.ps1
```

**Issue:** Database connection errors  
**Solution:** Check PostgreSQL is running

```powershell
docker-compose up postgres -d
```

**Issue:** Slow test execution  
**Solution:** Use pytest-xdist for parallel execution

```powershell
pytest tests/integration/ -n auto
```

## Future Enhancements

- [ ] Add load testing scenarios
- [ ] Implement chaos engineering tests
- [ ] Add security penetration tests
- [ ] Performance regression tests
- [ ] Multi-tenant isolation tests

---

*Last Updated: December 18, 2025*
