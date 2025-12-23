#!/usr/bin/env python3
"""Generate a small version compatibility matrix for the docs.

Source of truth:
- Python package metadata: pyproject.toml
- API version: openapi.json (generated from src/main.py)
- Frontend version: frontend/package.json (if present)

Output:
- docs/appendices/version-matrix.md
"""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_pyproject() -> dict:
    import tomllib

    return tomllib.loads(_read_text(REPO_ROOT / "pyproject.toml"))


def _load_openapi() -> dict:
    return json.loads(_read_text(REPO_ROOT / "openapi.json"))


def _load_package_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(_read_text(path))


def main() -> None:
    pyproject = _load_pyproject()
    openapi = _load_openapi()

    project = pyproject.get("project", {})
    python_requires = project.get("requires-python", "")
    pkg_version = project.get("version", "")

    api_version = (openapi.get("info") or {}).get("version", "")

    frontend_pkg = _load_package_json(REPO_ROOT / "frontend" / "package.json")
    frontend_version = (frontend_pkg or {}).get("version", "")
    node_engine = ((frontend_pkg or {}).get("engines") or {}).get("node", "")

    out_path = REPO_ROOT / "docs" / "appendices" / "version-matrix.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    content = """# Version Compatibility Matrix

>This page is auto-generated from repo sources.

| Component | Version / Requirement | Source |
|---|---|---|
| Python package | `{pkg_version}` | `pyproject.toml` |
| Python runtime | `{python_requires}` | `pyproject.toml` |
| API (OpenAPI info.version) | `{api_version}` | `openapi.json` (from `src/main.py`) |
| Frontend | `{frontend_version}` | `frontend/package.json` |
| Node.js (frontend engine) | `{node_engine}` | `frontend/package.json` |

""".format(
        pkg_version=pkg_version or "(unknown)",
        python_requires=python_requires or "(unknown)",
        api_version=api_version or "(unknown)",
        frontend_version=frontend_version or "(not set)",
        node_engine=node_engine or "(not set)",
    )

    out_path.write_text(content, encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
