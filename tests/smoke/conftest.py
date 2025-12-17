import pytest
import requests


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--url",
        action="store",
        default="http://localhost:8000",
        help="Base URL for smoke tests (e.g., https://staging.kosmos.internal)",
    )


@pytest.fixture(scope="session")
def base_url(pytestconfig: pytest.Config) -> str:
    return pytestconfig.getoption("--url")


@pytest.fixture(scope="session")
def session() -> requests.Session:
    return requests.Session()
