"""Logging setup."""

import logging
from pathlib import Path


def setup_logger(level: str = "INFO", log_file: str = None) -> None:
    Path("logs").mkdir(exist_ok=True)
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%H:%M:%S",
        handlers=handlers,
    )
