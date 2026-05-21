"""Test for automatic metrics generation in generation_service."""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.generation_service import generate_metrics, trigger_generation
from app.services.report_service import generate_metrics_if_missing


@pytest.fixture
def test_ticker():
    return "TEST"


@pytest.fixture
def evaluaciones_dir(tmp_path):
    """Create a temporary evaluaciones directory structure."""
    eval_dir = tmp_path / "evaluaciones"
    test_dir = eval_dir / "TEST" / "raw-search"
    test_dir.mkdir(parents=True, exist_ok=True)
    return eval_dir


def test_generate_metrics_script_exists():
    """Verify that the metrics generation script exists."""
    script_path = (
        Path(__file__).parent.parent / ".github" / "skills" / 
        "yfinance-report" / "scripts" / "generate_metrics_from_yfinance.py"
    )
    assert script_path.exists(), f"Script not found at {script_path}"


def test_generate_metrics_function_exists():
    """Verify that generate_metrics function is callable."""
    assert callable(generate_metrics), "generate_metrics is not callable"


def test_generate_metrics_invalid_ticker():
    """Test that generate_metrics handles invalid tickers gracefully."""
    result = generate_metrics("")
    assert isinstance(result, bool)


@patch('subprocess.run')
def test_generate_metrics_subprocess_call(mock_subprocess, test_ticker):
    """Test that generate_metrics calls subprocess with correct arguments."""
    mock_subprocess.return_value = MagicMock(returncode=0, stdout="", stderr="")
    
    result = generate_metrics(test_ticker)
    
    # Verify subprocess.run was called
    assert mock_subprocess.called
    
    # Verify the ticker was passed as argument
    call_args = mock_subprocess.call_args[0][0]
    assert test_ticker in call_args


@patch('app.services.generation_service.generate_metrics')
async def test_trigger_generation_calls_metrics(mock_generate, test_ticker):
    """Test that trigger_generation calls generate_metrics when reports exist."""
    mock_generate.return_value = True
    
    # Mock the existence of the final report
    with patch('pathlib.Path.exists') as mock_exists:
        mock_exists.return_value = True
        
        result = await trigger_generation(test_ticker)
        
        # Should indicate metrics generation
        assert result["status"] in ["metrics_generated", "awaiting_reports"]


def test_generate_metrics_if_missing_already_exists():
    """Test that generate_metrics_if_missing returns True if metrics already exist."""
    with patch('pathlib.Path.exists') as mock_exists:
        # Mock metrics file exists
        mock_exists.side_effect = [True]  # metrics.json exists
        
        result = generate_metrics_if_missing("TEST")
        assert result is True


def test_generate_metrics_if_missing_no_metrics_or_report():
    """Test that generate_metrics_if_missing returns False if neither exist."""
    with patch('pathlib.Path.exists') as mock_exists:
        # Mock neither metrics nor report exist
        mock_exists.return_value = False
        
        result = generate_metrics_if_missing("TEST")
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
