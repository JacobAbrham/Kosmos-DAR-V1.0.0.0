"""
Prometheus Metrics for KOSMOS API.
Provides /metrics endpoint and request instrumentation.
"""
import time
import logging
from typing import Callable

from fastapi import FastAPI, Request, Response, APIRouter
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Info,
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY,
)

logger = logging.getLogger(__name__)

# Application Info
APP_INFO = Info("kosmos_app", "KOSMOS application information")
APP_INFO.info({
    "version": "1.0.0",
    "name": "kosmos-api",
})

# Request metrics
REQUEST_COUNT = Counter(
    "kosmos_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "kosmos_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

REQUEST_IN_PROGRESS = Gauge(
    "kosmos_http_requests_in_progress",
    "HTTP requests currently in progress",
    ["method", "endpoint"],
)

# Agent metrics
AGENT_REQUESTS = Counter(
    "kosmos_agent_requests_total",
    "Total agent requests",
    ["agent_name", "tool"],
)

AGENT_LATENCY = Histogram(
    "kosmos_agent_request_duration_seconds",
    "Agent request latency in seconds",
    ["agent_name"],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
)

AGENT_ERRORS = Counter(
    "kosmos_agent_errors_total",
    "Total agent errors",
    ["agent_name", "error_type"],
)

# LLM metrics
LLM_REQUESTS = Counter(
    "kosmos_llm_requests_total",
    "Total LLM requests",
    ["provider", "model"],
)

LLM_TOKENS = Counter(
    "kosmos_llm_tokens_total",
    "Total LLM tokens used",
    ["provider", "model", "type"],  # type: prompt or completion
)

LLM_LATENCY = Histogram(
    "kosmos_llm_request_duration_seconds",
    "LLM request latency in seconds",
    ["provider", "model"],
    buckets=[0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
)

LLM_CACHE_HITS = Counter(
    "kosmos_llm_cache_hits_total",
    "LLM cache hits",
    ["provider"],
)

# Vote metrics
VOTE_REQUESTS = Counter(
    "kosmos_pentarchy_votes_total",
    "Total Pentarchy votes",
    ["outcome"],
)

VOTE_LATENCY = Histogram(
    "kosmos_pentarchy_vote_duration_seconds",
    "Pentarchy vote latency in seconds",
    buckets=[1.0, 2.5, 5.0, 10.0, 30.0],
)

# Database metrics
DB_CONNECTIONS = Gauge(
    "kosmos_db_connections_active",
    "Active database connections",
)

DB_QUERIES = Counter(
    "kosmos_db_queries_total",
    "Total database queries",
    ["operation"],  # select, insert, update, delete
)

# Redis metrics
REDIS_OPERATIONS = Counter(
    "kosmos_redis_operations_total",
    "Total Redis operations",
    ["operation"],  # get, set, delete
)

# WebSocket metrics
websocket_connections_total = Gauge(
    "kosmos_websocket_connections_total",
    "Total active WebSocket connections",
    ["conversation_id"],
)

websocket_messages_total = Counter(
    "kosmos_websocket_messages_total",
    "Total WebSocket messages",
    ["direction"],  # inbound, outbound
)


def track_time(metric: Histogram, labels: dict = None):
    """Context manager for tracking time with a histogram metric."""
    class Timer:
        def __init__(self):
            self.start = None

        def __enter__(self):
            self.start = time.time()
            return self

        def __exit__(self, *args):
            duration = time.time() - self.start
            if labels:
                metric.labels(**labels).observe(duration)
            else:
                metric.observe(duration)

    return Timer()


def get_metrics_endpoint():
    """Generate Prometheus metrics endpoint."""
    async def metrics(request: Request) -> Response:
        return Response(
            content=generate_latest(REGISTRY),
            media_type=CONTENT_TYPE_LATEST,
        )
    return metrics


class MetricsMiddleware:
    """Middleware to track request metrics."""

    def __init__(self, app: FastAPI):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        method = request.method

        # Normalize endpoint for metrics (avoid high cardinality)
        path = request.url.path
        endpoint = self._normalize_path(path)

        # Track in-progress requests
        REQUEST_IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()

        start_time = time.time()
        status_code = 500

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            # Record metrics
            duration = time.time() - start_time

            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status=str(status_code),
            ).inc()

            REQUEST_LATENCY.labels(
                method=method,
                endpoint=endpoint,
            ).observe(duration)

            REQUEST_IN_PROGRESS.labels(method=method, endpoint=endpoint).dec()

    def _normalize_path(self, path: str) -> str:
        """Normalize path to avoid high cardinality metrics."""
        # Replace UUIDs and IDs with placeholders
        import re

        # Replace UUIDs
        path = re.sub(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            "{id}",
            path,
        )

        # Replace numeric IDs
        path = re.sub(r"/\d+", "/{id}", path)

        return path


def setup_metrics(app: FastAPI):
    """Setup metrics for FastAPI application."""
    # Add metrics endpoint
    app.add_route("/metrics", get_metrics_endpoint())

    # Add metrics middleware
    app.add_middleware(MetricsMiddleware)

    logger.info("Prometheus metrics configured at /metrics")


# Helper functions for recording metrics

def record_agent_request(agent_name: str, tool: str):
    """Record an agent request."""
    AGENT_REQUESTS.labels(agent_name=agent_name, tool=tool).inc()


def record_agent_latency(agent_name: str, duration: float):
    """Record agent request latency."""
    AGENT_LATENCY.labels(agent_name=agent_name).observe(duration)


def record_agent_error(agent_name: str, error_type: str):
    """Record an agent error."""
    AGENT_ERRORS.labels(agent_name=agent_name, error_type=error_type).inc()


def record_llm_request(provider: str, model: str, prompt_tokens: int, completion_tokens: int, duration: float, cached: bool = False):
    """Record LLM request metrics."""
    LLM_REQUESTS.labels(provider=provider, model=model).inc()
    LLM_TOKENS.labels(provider=provider, model=model,
                      type="prompt").inc(prompt_tokens)
    LLM_TOKENS.labels(provider=provider, model=model,
                      type="completion").inc(completion_tokens)
    LLM_LATENCY.labels(provider=provider, model=model).observe(duration)

    if cached:
        LLM_CACHE_HITS.labels(provider=provider).inc()


def record_vote(outcome: str, duration: float):
    """Record Pentarchy vote metrics."""
    VOTE_REQUESTS.labels(outcome=outcome).inc()
    VOTE_LATENCY.observe(duration)


# Create metrics router
metrics_router = APIRouter(tags=["metrics"])


@metrics_router.get("/metrics", include_in_schema=False)
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)
