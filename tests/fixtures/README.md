# Test Fixtures

This directory contains shared test data and fixtures used across the test suite.

## Structure

- `sample_data.json` - Sample data for integration tests
- `mock_responses.py` - Mock HTTP responses for external APIs
- `test_models.py` - Test database model instances

## Usage

Import fixtures in your tests:

```python
from tests.fixtures import sample_data

def test_something():
    data = sample_data.load("example.json")
    assert data is not None
```
