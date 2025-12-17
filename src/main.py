import logging
import os
import socket
from datetime import datetime
from http.client import HTTPConnection
from typing import Dict, Tuple
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.responses import JSONResponse


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("kosmos-api")

app = FastAPI(
    title="KOSMOS Dev API",
    version="0.1.0",
    description="Minimal API stub to support dev automation and health checks.",
)


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
    url = os.getenv("DATABASE_URL", "postgresql://kosmos:kosmos_dev_password@localhost:5432/kosmos_dev")
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
