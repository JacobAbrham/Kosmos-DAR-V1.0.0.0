import logging
import os
import socket
from datetime import datetime
from http.client import HTTPConnection
from typing import Dict, Tuple
from urllib.parse import urlparse
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Import middleware and routers
from src.api.metrics import MetricsMiddleware, metrics_router
from src.core.logging import LoggingMiddleware, setup_logging
from src.api.rate_limit import RateLimitMiddleware


# Setup structured logging
setup_logging()
logger = logging.getLogger("kosmos-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting KOSMOS API...")
    yield
    logger.info("Shutting down KOSMOS API...")


app = FastAPI(
    title="KOSMOS API",
    version="2.0.0",
    description="KOSMOS AI Governance Platform - Multi-agent orchestration with Pentarchy voting.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(
        "CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add observability middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(MetricsMiddleware)

# Add rate limiting middleware (conditionally)
if os.getenv("ENABLE_RATE_LIMIT", "false").lower() == "true":
    app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(metrics_router)

# Import and include API routers
try:
    from src.api.routers.auth import router as auth_router
    app.include_router(auth_router, prefix="/api/v1")
except ImportError as e:
    logger.warning(f"Auth router not available: {e}")

try:
    from src.api.routers.chat import router as chat_router
    app.include_router(chat_router, prefix="/api/v1")
except ImportError as e:
    logger.warning(f"Chat router not available: {e}")

try:
    from src.api.routers.agents import router as agents_router
    app.include_router(agents_router, prefix="/api/v1")
except ImportError as e:
    logger.warning(f"Agents router not available: {e}")

try:
    from src.api.routers.votes import router as votes_router
    app.include_router(votes_router, prefix="/api/v1")
except ImportError as e:
    logger.warning(f"Votes router not available: {e}")

try:
    from src.api.routers.websocket import router as websocket_router
    app.include_router(websocket_router)
except ImportError as e:
    logger.warning(f"WebSocket router not available: {e}")

try:
    from src.api.routers.mcp import router as mcp_router
    app.include_router(mcp_router, prefix="/api/v1")
except ImportError as e:
    logger.warning(f"MCP router not available: {e}")


def service_meta() -> dict:
    """Shared metadata for health/readiness responses."""
    return {
        "service": "kosmos-api",
        "version": app.version,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/health", tags=["system"])
async def health() -> JSONResponse:
    """Liveness endpoint for container health checks."""
    return JSONResponse({"status": "ok", **service_meta()})


@app.get("/ready", tags=["system"])
async def ready() -> JSONResponse:
    """
    Readiness endpoint with optional dependency checks.
    If ENABLE_DEP_CHECKS=true, verifies Postgres, Redis, and MinIO connectivity.
    """
    if not dep_checks_enabled():
        return JSONResponse(
            {
                "status": "ready",
                "dependencies": {
                    "checked": False,
                    "details": "Dependency checks disabled via ENABLE_DEP_CHECKS",
                },
                **service_meta(),
            }
        )

    dep_results = {
        "postgres": check_postgres(),
        "redis": check_redis(),
        "minio": check_minio(),
    }

    all_ok = all(result["ok"] for result in dep_results.values())
    status = "ready" if all_ok else "degraded"
    code = 200 if all_ok else 503

    return JSONResponse(
        {
            "status": status,
            "dependencies": dep_results,
            **service_meta(),
        },
        status_code=code,
    )


@app.get("/", tags=["system"])
async def root() -> dict:
    return {"message": "KOSMOS development API stub", **service_meta()}


# --- Dependency checks (lightweight TCP/HTTP probes) ---


def check_tcp(host: str, port: int, timeout: float = 1.5) -> Tuple[bool, str]:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, "reachable"
    except Exception as exc:  # noqa: BLE001
        return False, f"unreachable: {exc}"


def check_http(host: str, port: int, path: str = "/", timeout: float = 2.0) -> Tuple[bool, str]:
    try:
        conn = HTTPConnection(host, port, timeout=timeout)
        conn.request("GET", path)
        resp = conn.getresponse()
        conn.close()
        return resp.status < 500, f"http {resp.status}"
    except Exception as exc:  # noqa: BLE001
        return False, f"http error: {exc}"


def check_postgres() -> Dict[str, str]:
    url = os.getenv(
        "DATABASE_URL", "postgresql://kosmos:kosmos_dev_password@localhost:5432/kosmos_dev")
    parsed = urlparse(url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432
    ok, detail = check_tcp(host, port)
    return {"ok": ok, "detail": detail, "host": host, "port": port}


def check_redis() -> Dict[str, str]:
    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    parsed = urlparse(url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 6379
    ok, detail = check_tcp(host, port)
    return {"ok": ok, "detail": detail, "host": host, "port": port}


def check_minio() -> Dict[str, str]:
    endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    endpoint_url = endpoint if "://" in endpoint else f"http://{endpoint}"
    parsed = urlparse(endpoint_url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 9000
    ok_tcp, detail_tcp = check_tcp(host, port)
    ok_http, detail_http = check_http(host, port)
    ok = ok_tcp and ok_http
    detail = f"{detail_tcp}; {detail_http}"
    return {"ok": ok, "detail": detail, "host": host, "port": port}


def dep_checks_enabled() -> bool:
    return os.getenv("ENABLE_DEP_CHECKS", "false").lower() == "true"
