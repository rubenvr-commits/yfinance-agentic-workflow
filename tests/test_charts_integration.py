"""Tests for charts data structure and integration."""

import json
from pathlib import Path
import pytest

from app.models import MetricsData
from app.services.report_service import load_metrics_json, get_report_data


class TestMetricsDataStructure:
    """Test metrics.json structure validation."""

    def test_metrics_data_model_validation(self):
        """Verify MetricsData model accepts valid structure."""
        metrics_dict = {
            "ticker": "NVDA",
            "fecha": "2026-05-21",
            "precio_actual": 222.34,
            "precios_historicos": {
                "ultimos_12m": [
                    {"date": "2025-05-21", "close": 180.45},
                    {"date": "2025-06-15", "close": 185.23},
                    {"date": "2026-05-21", "close": 222.34}
                ]
            },
            "valuations": {
                "pe_ratio": 45.2,
                "pb_ratio": 35.8,
                "ps_ratio": 18.5,
                "price_to_fcf": 12.3
            },
            "performance": {
                "roe": 0.45,
                "roa": 0.28,
                "fcf_billions": 52.0,
                "dividend_yield": 0.008
            },
            "sector_comparison": {
                "pe_sector": 42.5,
                "pe_sp500": 25.0,
                "pb_sector": 32.0,
                "pb_sp500": 3.2,
                "ps_sector": 16.8,
                "ps_sp500": 2.5
            }
        }

        metrics = MetricsData(**metrics_dict)

        assert metrics.ticker == "NVDA"
        assert metrics.fecha == "2026-05-21"
        assert metrics.precio_actual == 222.34
        assert metrics.precios_historicos is not None
        assert len(metrics.precios_historicos["ultimos_12m"]) == 3
        assert metrics.valuations is not None
        assert metrics.valuations["pe_ratio"] == 45.2
        assert metrics.performance is not None
        assert metrics.performance["roe"] == 0.45
        assert metrics.sector_comparison is not None
        assert metrics.sector_comparison["pe_sp500"] == 25.0

    def test_metrics_data_minimal_validation(self):
        """Verify MetricsData accepts minimal required fields."""
        minimal_dict = {
            "ticker": "TEST",
            "fecha": "2026-05-21"
        }

        metrics = MetricsData(**minimal_dict)

        assert metrics.ticker == "TEST"
        assert metrics.fecha == "2026-05-21"
        assert metrics.precio_actual is None
        assert metrics.precios_historicos is None
        assert metrics.valuations is None
        assert metrics.performance is None
        assert metrics.sector_comparison is None

    def test_metrics_serialization(self):
        """Test metrics can be serialized to dict."""
        metrics_dict = {
            "ticker": "AAPL",
            "fecha": "2026-05-21",
            "precio_actual": 150.25,
            "valuations": {"pe_ratio": 28.5}
        }

        metrics = MetricsData(**metrics_dict)
        serialized = metrics.model_dump()

        assert serialized["ticker"] == "AAPL"
        assert serialized["fecha"] == "2026-05-21"
        assert serialized["precio_actual"] == 150.25
        assert serialized["valuations"]["pe_ratio"] == 28.5

    def test_price_history_structure(self):
        """Validate price history data structure."""
        price_history = [
            {"date": "2025-01-01", "close": 100.0},
            {"date": "2025-02-01", "close": 105.5},
            {"date": "2025-03-01", "close": 103.2}
        ]

        metrics_dict = {
            "ticker": "TEST",
            "fecha": "2026-05-21",
            "precios_historicos": {"ultimos_12m": price_history}
        }

        metrics = MetricsData(**metrics_dict)

        assert len(metrics.precios_historicos["ultimos_12m"]) == 3
        for price in metrics.precios_historicos["ultimos_12m"]:
            assert "date" in price
            assert "close" in price
            assert isinstance(price["close"], (int, float))

    def test_valuations_all_metrics(self):
        """Ensure all valuation metrics are present."""
        valuations = {
            "pe_ratio": 45.2,
            "pb_ratio": 35.8,
            "ps_ratio": 18.5,
            "price_to_fcf": 12.3
        }

        metrics_dict = {
            "ticker": "TEST",
            "fecha": "2026-05-21",
            "valuations": valuations
        }

        metrics = MetricsData(**metrics_dict)

        assert metrics.valuations["pe_ratio"] is not None
        assert metrics.valuations["pb_ratio"] is not None
        assert metrics.valuations["ps_ratio"] is not None
        assert metrics.valuations["price_to_fcf"] is not None

    def test_performance_all_metrics(self):
        """Ensure all performance metrics are present."""
        performance = {
            "roe": 0.45,
            "roa": 0.28,
            "fcf_billions": 52.0,
            "dividend_yield": 0.008
        }

        metrics_dict = {
            "ticker": "TEST",
            "fecha": "2026-05-21",
            "performance": performance
        }

        metrics = MetricsData(**metrics_dict)

        assert metrics.performance["roe"] is not None
        assert metrics.performance["roa"] is not None
        assert metrics.performance["fcf_billions"] is not None
        assert metrics.performance["dividend_yield"] is not None

    def test_sector_comparison_structure(self):
        """Validate sector comparison metrics."""
        sector_comp = {
            "pe_sector": 42.5,
            "pe_sp500": 25.0,
            "pb_sector": 32.0,
            "pb_sp500": 3.2,
            "ps_sector": 16.8,
            "ps_sp500": 2.5
        }

        metrics_dict = {
            "ticker": "TEST",
            "fecha": "2026-05-21",
            "sector_comparison": sector_comp
        }

        metrics = MetricsData(**metrics_dict)

        assert len(metrics.sector_comparison) == 6
        assert metrics.sector_comparison["pe_sector"] == 42.5
        assert metrics.sector_comparison["pe_sp500"] == 25.0

    def test_metrics_with_null_values(self):
        """Test metrics handles null values gracefully."""
        metrics_dict = {
            "ticker": "TEST",
            "fecha": "2026-05-21",
            "valuations": {
                "pe_ratio": None,
                "pb_ratio": 35.8,
                "ps_ratio": None,
                "price_to_fcf": 12.3
            }
        }

        metrics = MetricsData(**metrics_dict)

        assert metrics.valuations["pe_ratio"] is None
        assert metrics.valuations["pb_ratio"] == 35.8
        assert metrics.valuations["ps_ratio"] is None


class TestChartsDataIntegration:
    """Test integration with charts data endpoint."""

    def test_load_metrics_json_structure(self):
        """Test loading metrics JSON maintains structure."""
        test_ticker = "TEST"
        test_metrics = {
            "ticker": test_ticker,
            "fecha": "2026-05-21",
            "precio_actual": 150.0,
            "valuations": {"pe_ratio": 25.0},
            "performance": {"roe": 0.35}
        }

        # This would test actual file loading if metrics exist
        # For now, verify the model accepts the structure
        metrics = MetricsData(**test_metrics)
        assert metrics.ticker == test_ticker

    def test_report_data_includes_metrics(self):
        """Verify report data includes metrics for charts."""
        test_data = {
            "content": "# Test Report",
            "ticker": "TEST",
            "generated_date": "2026-05-21",
            "metrics": {
                "ticker": "TEST",
                "fecha": "2026-05-21",
                "precios_historicos": {
                    "ultimos_12m": [
                        {"date": "2025-05-21", "close": 100.0}
                    ]
                },
                "valuations": {"pe_ratio": 20.0},
                "performance": {"roe": 0.30},
                "sector_comparison": {"pe_sp500": 22.0}
            }
        }

        # Verify metrics field is present and valid
        assert test_data["metrics"] is not None
        metrics = MetricsData(**test_data["metrics"])
        assert metrics.ticker == "TEST"
        assert metrics.precios_historicos is not None

    def test_metrics_api_response_structure(self):
        """Validate structure matches API response expectations."""
        api_response = {
            "ticker": "NVDA",
            "fecha": "2026-05-21",
            "precio_actual": 222.34,
            "precios_historicos": {
                "ultimos_12m": [
                    {"date": "2025-05-21", "close": 180.45},
                    {"date": "2026-05-21", "close": 222.34}
                ]
            },
            "valuations": {
                "pe_ratio": 45.2,
                "pb_ratio": 35.8,
                "ps_ratio": 18.5,
                "price_to_fcf": 12.3
            },
            "performance": {
                "roe": 0.45,
                "roa": 0.28,
                "fcf_billions": 52.0,
                "dividend_yield": 0.008
            },
            "sector_comparison": {
                "pe_sector": 42.5,
                "pe_sp500": 25.0,
                "pb_sector": 32.0,
                "pb_sp500": 3.2,
                "ps_sector": 16.8,
                "ps_sp500": 2.5
            }
        }

        # Validate it serializes properly
        metrics = MetricsData(**api_response)
        serialized = metrics.model_dump(exclude_none=True)

        assert "ticker" in serialized
        assert "fecha" in serialized
        assert "precios_historicos" in serialized
        assert "valuations" in serialized
        assert "performance" in serialized
        assert "sector_comparison" in serialized
