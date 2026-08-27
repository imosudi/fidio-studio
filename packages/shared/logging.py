import logging
import sys
import json
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """Structured JSON Log Formatter for Fídíò Platform."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "filename": record.filename,
            "line": record.lineno,
        }

        # Include contextual IDs if attached to record
        for key in ("request_id", "correlation_id", "job_id", "project_id", "provider_name"):
            if hasattr(record, key):
                log_data[key] = getattr(record, key)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure structured logging for Fídíò services."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(console_handler)

    # Mute noisy third-party loggers
    logging.getLogger("uvicorn.access").handlers = [console_handler]
    logging.getLogger("uvicorn.error").handlers = [console_handler]

    return logging.getLogger("fidio")


logger = setup_logging()
