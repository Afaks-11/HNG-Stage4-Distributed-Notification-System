import structlog
import logging
import sys
from typing import Any, Dict


def configure_logging(debug: bool = False) -> None:
    """Configure structured logging"""
    
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if debug else structlog.processors.JSONRenderer()
        ],
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
        "notification_id": notification_id,
        **kwargs
    }
    
    if correlation_id:
        log_data["correlation_id"] = correlation_id
    
    logger.info(event, **log_data)