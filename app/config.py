"""Application configuration."""

from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
EVALUACIONES_DIR = BASE_DIR / "evaluaciones"
REPORTS_DIR = EVALUACIONES_DIR

DEBUG = False
LOG_LEVEL = "INFO"
# Generation timeouts
GENERATION_TIMEOUT_BASE = 60  # seconds default for subprocess runs
GENERATION_TIMEOUT_INCREMENT = 45  # seconds added per generated report
