import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# Note: Testing /chat and /vote requires mocking the ZeusAgent inside the API
# which is complex due to the global state in main.py. 
# For unit tests, we focus on the endpoint structure.
