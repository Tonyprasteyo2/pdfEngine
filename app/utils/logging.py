import logging
import sys
from typing import Any, Dict, Optional

from app.config import get_settings


class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        extra = getattr(record, "extra_data", None)
        if isinstance(extra, dict):
            base.update(extra)
        return " | ".join(f"{k}={v}" for k, v in base.items())


def setup_logging() -> logging.Logger:
    settings = get_settings()
    logger = logging.getLogger("simrs-pdf")
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    logger.addHandler(handler)

    log_dir = settings.pdf_log_dir
    try:
        file_handler = logging.FileHandler(f"{log_dir}/service.log")
        file_handler.setFormatter(StructuredFormatter())
        logger.addHandler(file_handler)
    except Exception:
        pass

    return logger


logger = setup_logging()


def log_job(
    job_id: str,
    operation: str,
    status: str,
    engine: Optional[str] = None,
    attempt: Optional[int] = None,
    duration: Optional[float] = None,
    **kwargs: Any,
) -> None:
    data: Dict[str, Any] = {
        "job_id": job_id,
        "operation": operation,
        "status": status,
    }
    if engine:
        data["engine"] = engine
    if attempt is not None:
        data["attempt"] = attempt
    if duration is not None:
        data["duration"] = f"{duration:.2f}s"
    data.update(kwargs)
    logger.info("job_event", extra={"extra_data": data})
