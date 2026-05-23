"""Unit tests for FastAPI main application."""

import pytest
from fastapi.testclient import TestClient
from app.main import app, lifespan


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


@pytest.mark.asyncio
async def test_lifespan_starts_and_stops_agent(monkeypatch):
    """Test that the app lifespan starts and stops the agent watcher."""
    events = []

    monkeypatch.setattr("app.main.start_analista_agent", lambda: events.append("start"))
    monkeypatch.setattr("app.main.stop_analista_agent", lambda: events.append("stop"))

    async with lifespan(app):
        assert events == ["start"]

    assert events == ["start", "stop"]
