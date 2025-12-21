"""
Structured Logging Configuration for KOSMOS.
Provides JSON logging with correlation IDs and context.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import os
import sys
import uuid
import logging
import json
from datetime import datetime, timezone
from typing import Optional, Any, Dict
from contextvars import ContextVar

# Context variable for request correlation
correlation_id_var: ContextVar[Optional[str]] = ContextVar(
    "correlation_id", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


def get_correlation_id() -> str:
    """Get current correlation ID or generate new one."""
    cid = correlation_id_var.get()
    if cid is None:
        cid = str(uuid.uuid4())
        correlation_id_var.set(cid)
    return cid


def set_correlation_id(cid: str):
    """Set correlation ID for current context."""
    correlation_id_var.set(cid)


def set_user_id(uid: str):
    """Set user ID for current context."""
    user_id_var.set(uid)


class JSONFormatter(logging.Formatter):
    """JSON log formatter with structured fields."""

    def __init__(self, include_extra: bool = True):
        super().__init__()
        self.include_extra = include_extra
        self.service_name = os.getenv("SERVICE_NAME", "kosmos-api")
        self.environment = os.getenv("ENVIRONMENT", "development")

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self.service_name,
            "environment": self.environment,
        }

        # Add correlation ID
        cid = correlation_id_var.get()
        if cid:
            log_data["correlation_id"] = cid

        # Add user ID
        uid = user_id_var.get()
        if uid:
            log_data["user_id"] = uid

        # Add source location
        log_data["source"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }

        # Add exception info
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }

        # Add extra fields
        if self.include_extra and hasattr(record, "__dict__"):
            extra = {}
            for key, value in record.__dict__.items():
                if key not in {
                    "name", "msg", "args", "created", "filename", "funcName",
                    "levelname", "levelno", "lineno", "module", "msecs",
                    "pathname", "process", "processName", "relativeCreated",
                    "stack_info", "exc_info", "exc_text", "thread", "threadName",
                    "message", "asctime",
                }:
                    try:
                        json.dumps(value)  # Check if serializable
                        extra[key] = value
                    except (TypeError, ValueError):
                        extra[key] = str(value)

            if extra:
                log_data["extra"] = extra

        return json.dumps(log_data)


class StructuredLogger(logging.Logger):
    """Logger with structured context support."""

    def _log_with_context(
        self,
        level: int,
        msg: str,
        args=None,
        exc_info=None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        if extra is None:
            extra = {}

        # Add context
        extra.update(kwargs)

        super()._log(level, msg, args or (), exc_info=exc_info, extra=extra)

    def info(self, msg, *args, **kwargs):
        self._log_with_context(logging.INFO, msg, args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self._log_with_context(logging.DEBUG, msg, args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._log_with_context(logging.WARNING, msg, args, **kwargs)

    def error(self, msg, *args, exc_info=None, **kwargs):
        self._log_with_context(logging.ERROR, msg, args,
                               exc_info=exc_info, **kwargs)

    def critical(self, msg, *args, exc_info=None, **kwargs):
        self._log_with_context(logging.CRITICAL, msg,
                               args, exc_info=exc_info, **kwargs)


def setup_logging(
    level: str = None,
    json_format: bool = None,
):
    """
    Configure structured logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        json_format: Whether to use JSON format (auto-detected in production)
    """
    level = level or os.getenv("LOG_LEVEL", "INFO")

    # Auto-detect JSON format in production
    if json_format is None:
        environment = os.getenv("ENVIRONMENT", "development")
        json_format = environment in ("production", "staging")

    # Set custom logger class
    logging.setLoggerClass(StructuredLogger)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))

    # Set formatter
    if json_format:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ))

    root_logger.addHandler(handler)

    # Configure third-party loggers
    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.addHandler(handler)

    # Suppress noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    root_logger.info(
        "Logging configured",
        extra={"level": level, "json_format": json_format},
    )


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return logging.getLogger(name)


# Request logging middleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to add correlation IDs and log requests."""

    async def dispatch(self, request: Request, call_next):
        # Get or generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        set_correlation_id(correlation_id)

        # Extract user ID from auth if available
        # (Would need to decode JWT here in real implementation)

        logger = get_logger("kosmos.request")

        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            method=request.method,
            path=request.url.path,
            query=str(request.query_params),
            client_ip=request.client.host if request.client else None,
        )

        import time
        start_time = time.time()

        try:
            response = await call_next(request)

            duration_ms = int((time.time() - start_time) * 1000)

            logger.info(
                f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

            # Add correlation ID to response
            response.headers["X-Correlation-ID"] = correlation_id

            return response

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)

            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                exc_info=True,
                method=request.method,
                path=request.url.path,
                duration_ms=duration_ms,
                error=str(e),
            )
            raise
