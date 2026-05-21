"""Unit tests for app configuration."""

import pytest
from pathlib import Path
from app.config import BASE_DIR, EVALUACIONES_DIR, DEBUG, LOG_LEVEL


def test_config_base_directories_exist():
    """Test that configuration directories are properly defined."""
    assert BASE_DIR is not None
    assert isinstance(BASE_DIR, Path)
    assert EVALUACIONES_DIR is not None
    assert isinstance(EVALUACIONES_DIR, Path)


def test_config_debug_and_log_level():
    """Test debug and log level configuration values."""
    assert DEBUG is False
    assert LOG_LEVEL == "INFO"
