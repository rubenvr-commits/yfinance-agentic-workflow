"""Unit tests for health check endpoint."""

import pytest
from fastapi.testclient import TestClient
from app.routes.health import router


client = TestClient(__import__('fastapi').FastAPI())
client.app.include_router(router)


def test_health_endpoint_returns_ok():
    """Test GET /health returns 200 with OK status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_health_endpoint_response_structure():
    """Test health endpoint response has correct structure."""
    response = client.get("/health")
    data = response.json()
    assert isinstance(data, dict)
    assert "status" in data
