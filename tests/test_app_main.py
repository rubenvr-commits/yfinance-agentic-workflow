"""Unit tests for FastAPI main application."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_app_initialization():
    """Test that FastAPI app initializes with correct metadata."""
    assert app.title == "Financial Reports API"
    assert app.version == "1.0.0"
    assert "financial reports" in app.description.lower()


def test_app_includes_health_router():
    """Test that app includes health check router."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
