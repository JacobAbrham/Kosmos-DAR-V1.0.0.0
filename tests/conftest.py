"""
Pytest configuration for KOSMOS tests.
"""

import os
import pytest
import sys
from pathlib import Path

# Set test environment defaults BEFORE importing any modules
os.environ.setdefault("REQUIRE_AUTH", "false")
os.environ.setdefault("ENABLE_DEP_CHECKS", "false")
os.environ.setdefault("ENABLE_RATE_LIMIT", "false")

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture providing path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def sample_config():
    """Fixture providing sample configuration for tests."""
    return {
        "environment": "test",
        "database_url": "postgresql://test:test@localhost:5432/kosmos_test",
        "redis_url": "redis://localhost:6379/1",
    }
