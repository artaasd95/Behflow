"""
Centralized logger configuration for Behflow
"""
import logging
import os
from logging import Logger
from typing import Optional

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def configure_logging():
    """Configure the root logger if not already configured."""
    level = getattr(logging, LOG_LEVEL, logging.INFO)
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler()
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        handler.setFormatter(logging.Formatter(fmt))
        root.addHandler(handler)
    root.setLevel(level)


def get_logger(name: Optional[str] = None) -> Logger:
    """Return a configured logger instance for `name`."""
    configure_logging()
    return logging.getLogger(name or "behflow")