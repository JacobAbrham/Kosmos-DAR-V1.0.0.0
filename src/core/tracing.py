"""
OpenTelemetry Tracing Configuration for KOSMOS.
Provides distributed tracing across all services.
"""
import os
import logging
from typing import Optional
from functools import wraps

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat

logger = logging.getLogger(__name__)

# Configuration
OTEL_ENABLED = os.getenv("OTEL_ENABLED", "true").lower() == "true"
OTEL_SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "kosmos-api")
OTEL_SERVICE_VERSION = os.getenv("OTEL_SERVICE_VERSION", "2.0.0")
OTEL_EXPORTER_ENDPOINT = os.getenv(
    "OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
OTEL_EXPORT_CONSOLE = os.getenv(
    "OTEL_EXPORT_CONSOLE", "false").lower() == "true"

# Global tracer
_tracer: Optional[trace.Tracer] = None


def setup_tracing(app=None) -> trace.Tracer:
    """
    Configure OpenTelemetry tracing for the application.

    Args:
        app: FastAPI application to instrument (optional)

    Returns:
        Configured tracer instance
    """
    global _tracer

    if not OTEL_ENABLED:
        logger.info("OpenTelemetry tracing disabled")
        return trace.get_tracer(__name__)

    # Create resource with service info
    resource = Resource.create({
        SERVICE_NAME: OTEL_SERVICE_NAME,
        SERVICE_VERSION: OTEL_SERVICE_VERSION,
        "deployment.environment": os.getenv("ENVIRONMENT", "development"),
    })

    # Create tracer provider
    provider = TracerProvider(resource=resource)

    # Configure exporters
    if OTEL_EXPORT_CONSOLE:
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))
        logger.info("OpenTelemetry console exporter enabled")

    if OTEL_EXPORTER_ENDPOINT:
        try:
            otlp_exporter = OTLPSpanExporter(
                endpoint=OTEL_EXPORTER_ENDPOINT,
                insecure=True,
            )
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            logger.info(
                f"OpenTelemetry OTLP exporter configured: {OTEL_EXPORTER_ENDPOINT}")
        except Exception as e:
            logger.warning(f"Failed to configure OTLP exporter: {e}")

    # Set global tracer provider
    trace.set_tracer_provider(provider)

    # Set up B3 propagation (for compatibility with Jaeger, Zipkin)
    set_global_textmap(B3MultiFormat())

    # Instrument libraries
    _instrument_libraries(app)

    # Get tracer
    _tracer = trace.get_tracer(__name__)

    logger.info("OpenTelemetry tracing configured successfully")
    return _tracer


def _instrument_libraries(app=None):
    """Instrument common libraries for automatic tracing."""

    # FastAPI
    if app:
        try:
            FastAPIInstrumentor.instrument_app(app)
            logger.debug("FastAPI instrumented")
        except Exception as e:
            logger.warning(f"Failed to instrument FastAPI: {e}")

    # HTTPX (for async HTTP calls)
    try:
        HTTPXClientInstrumentor().instrument()
        logger.debug("HTTPX instrumented")
    except Exception as e:
        logger.warning(f"Failed to instrument HTTPX: {e}")

    # Redis
    try:
        RedisInstrumentor().instrument()
        logger.debug("Redis instrumented")
    except Exception as e:
        logger.warning(f"Failed to instrument Redis: {e}")


def instrument_sqlalchemy(engine):
    """Instrument SQLAlchemy engine for tracing."""
    try:
        SQLAlchemyInstrumentor().instrument(engine=engine)
        logger.debug("SQLAlchemy instrumented")
    except Exception as e:
        logger.warning(f"Failed to instrument SQLAlchemy: {e}")


def get_tracer() -> trace.Tracer:
    """Get the configured tracer instance."""
    global _tracer
    if _tracer is None:
        _tracer = trace.get_tracer(__name__)
    return _tracer


def traced(name: str = None, attributes: dict = None):
    """
    Decorator to trace a function.

    Usage:
        @traced("my_operation")
        async def my_function():
            pass
    """
    def decorator(func):
        span_name = name or func.__name__

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.start_as_current_span(span_name) as span:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                try:
                    result = await func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(trace.Status(
                        trace.StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.start_as_current_span(span_name) as span:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                try:
                    result = func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(trace.Status(
                        trace.StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


class SpanContext:
    """Context manager for manual span creation."""

    def __init__(self, name: str, attributes: dict = None):
        self.name = name
        self.attributes = attributes or {}
        self.span = None

    def __enter__(self):
        tracer = get_tracer()
        self.span = tracer.start_span(self.name)
        for key, value in self.attributes.items():
            self.span.set_attribute(key, value)
        return self.span

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.span.set_status(trace.Status(
                trace.StatusCode.ERROR, str(exc_val)))
            self.span.record_exception(exc_val)
        else:
            self.span.set_status(trace.Status(trace.StatusCode.OK))
        self.span.end()
        return False


def add_span_attributes(**attributes):
    """Add attributes to the current span."""
    span = trace.get_current_span()
    if span:
        for key, value in attributes.items():
            span.set_attribute(key, value)


def add_span_event(name: str, attributes: dict = None):
    """Add an event to the current span."""
    span = trace.get_current_span()
    if span:
        span.add_event(name, attributes=attributes or {})


def record_exception(exception: Exception):
    """Record an exception in the current span."""
    span = trace.get_current_span()
    if span:
        span.record_exception(exception)
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(exception)))
