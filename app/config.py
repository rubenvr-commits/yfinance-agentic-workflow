"""Application configuration."""

from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
EVALUACIONES_DIR = BASE_DIR / "evaluaciones"
REPORTS_DIR = EVALUACIONES_DIR

DEBUG = False
LOG_LEVEL = "INFO"
