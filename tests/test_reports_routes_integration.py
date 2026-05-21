"""Integration tests for reports API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_report_status_endpoint():
    """Test GET /api/reports/{ticker}/status endpoint."""
    response = client.get("/api/reports/NVDA/status")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "exists" in data


def test_get_report_status_invalid_ticker():
    """Test status endpoint with invalid ticker."""
    response = client.get("/api/reports/INVALID@#$/status")
    assert response.status_code == 400


def test_get_report_endpoint():
    """Test GET /api/reports/{ticker} endpoint."""
    response = client.get("/api/reports/NVDA")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "ticker" in data
        assert data["ticker"] == "NVDA"


def test_get_charts_data_endpoint():
    """Test GET /api/reports/{ticker}/charts-data endpoint."""
    response = client.get("/api/reports/NVDA/charts-data")
    assert response.status_code in [200, 404]


def test_export_prices_csv_endpoint():
    """Test GET /api/reports/{ticker}/precios.csv endpoint."""
    response = client.get("/api/reports/NVDA/precios.csv")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert "text/csv" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_generate_report_endpoint():
    """Test POST /api/reports/{ticker}/generate endpoint."""
    response = client.post("/api/reports/NVDA/generate")
    assert response.status_code in [200, 201, 202, 400]
    if response.status_code in [200, 201, 202]:
        data = response.json()
        assert "status" in data


@pytest.mark.asyncio
async def test_get_generation_progress_endpoint():
    """Test GET /api/reports/{ticker}/generate/progress endpoint."""
    response = client.get("/api/reports/NVDA/generate/progress")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "status" in data
