"""Application configuration."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
EVALUACIONES_DIR = BASE_DIR / "evaluaciones"
REPORTS_DIR = EVALUACIONES_DIR

DEBUG = False
LOG_LEVEL = "INFO"
RUN_ANALISTA_AGENT = os.environ.get("RUN_ANALISTA_AGENT", "1").strip().lower() not in {"0", "false", "no"}
# Generation timeouts
GENERATION_TIMEOUT_BASE = 60  # seconds default for subprocess runs
GENERATION_TIMEOUT_INCREMENT = 45  # seconds added per generated report
