import logging
from logging.handlers import RotatingFileHandler

from paths import LOGS_DIR


def configure_logging():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("smart_mirror")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(
        LOGS_DIR / "smart_mirror.log",
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    ))
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def get_logger(component):
    configure_logging()
    return logging.getLogger(f"smart_mirror.{component}")
