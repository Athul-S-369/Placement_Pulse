"""
PlacementPulse - Centralised logging setup.
Call `get_logger(__name__)` in every module.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT, LOGS_DIR


def _ensure_log_dir() -> Path:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    return LOGS_DIR


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(console)

    # File handler (daily log file)
    log_dir = _ensure_log_dir()
    today = datetime.utcnow().strftime("%Y-%m-%d")
    file_handler = logging.FileHandler(log_dir / f"run_{today}.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger
