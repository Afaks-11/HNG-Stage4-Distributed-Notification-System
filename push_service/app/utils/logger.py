import structlog
import logging
import sys
from typing import Any, Dict


def configure_logging(debug: bool = False) -> None:
    """Configure structured logging"""
    
    level = logging.DEBUG if debug else logging.INFO
    
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if debug else structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.WriteLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)


def log_notification_event(
    logger: structlog.BoundLogger,
    event: str,
    notification_id: str,
    correlation_id: str = None,
    **kwargs: Any
) -> None:
    """Log notification-related events with consistent structure"""
    
    log_data: Dict[str, Any] = {
        "event": event,
        "notification_id": notification_id,
        **kwargs
    }
    
    if correlation_id:
        log_data["correlation_id"] = correlation_id
    
    logger.info("notification_event", **log_data)