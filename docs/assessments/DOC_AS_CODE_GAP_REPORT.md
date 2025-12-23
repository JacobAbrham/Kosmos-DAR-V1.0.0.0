# Doc-as-Code Gap & Error Report (Kosmos)

**Scope:** This repository’s documentation and the code artifacts that should drive it (`docs/`, `src/`, `openapi.json`, schemas, workflows).

## Executive Summary

The repo has strong building blocks for doc-as-code (MkDocs configs, OpenAPI snapshot, a validation script, and an auto-doc workflow), but several *accuracy* and *automation wiring* issues prevent reliable “docs generated from code” behavior.

### Most impactful gaps found

1. **Workflows not reliably running**
   - Multiple GitHub Actions workflows are wired to `main`, while this repo’s default branch is `master`.
   - Several jobs ran `mkdocs build --strict` without pointing at the actual config location (`docs/mkdocs*.yml`).

2. **API docs drifted from implementation**
   - The API reference page contained legacy / non-existent endpoints (e.g., `GET /models`, `POST /models/{model_id}/invoke`).
   - Engineering API design doc referenced incorrect OpenAPI/Swagger paths (`/api/v1/openapi.json`, `/api/v1/docs`, `/api/v1/redoc`) while the FastAPI app serves `GET /openapi.json`, `GET /docs`, `GET /redoc`.

3. **OpenAPI not consumable by MkDocs**
   - `openapi.json` was committed at repo root only; MkDocs builds from `docs/`, so it could not embed Swagger UI reliably.

4. **Version traceability inconsistency**
   - Python package version in `pyproject.toml` is `1.0.0`.
   - FastAPI app in `src/main.py` advertises API version `2.0.0` (and OpenAPI snapshot matches that).
   - This may be intentional (package version ≠ API version), but it needs to be documented explicitly and enforced with checks.

## Doc-as-Code Improvements Implemented

These changes were made to move toward automated, validated docs:

- **Automation**
  - `scripts/generate_openapi.py` now writes both `openapi.json` (repo root) **and** `docs/openapi.json` for MkDocs embedding.
  - Added `scripts/generate_version_matrix.py` to generate `docs/appendices/version-matrix.md` from `pyproject.toml`, `openapi.json`, and `frontend/package.json`.

- **Validation**
  - `scripts/validate_all.py` now checks:
    - `openapi.json` exists and is valid JSON
    - `openapi.json` matches `src.main:app.openapi()` (freshness)
    - `docs/openapi.json` exists and matches the root OpenAPI snapshot
    - Key API documentation files do not mention endpoints missing from the OpenAPI spec

- **Dynamic Content**
  - The generated version matrix is linked in MkDocs navigation.

- **Docs Site Integration**
  - Enabled the `swagger-ui-tag` plugin in MkDocs config and added an embedded OpenAPI page:
    - `docs/developer-guide/api-reference/openapi.md`

- **CI/CD**
  - Updated doc workflows to:
    - Trigger on `master` as well as `main`
    - Build using `docs/mkdocs-complete.yml`

## Remaining Gaps (Recommended Next Steps)

### Completeness
- Add executable end-to-end examples for common flows:
  - auth register/login/refresh
  - send chat message and fetch conversation history
  - list agents
  - submit/inspect votes
- Document error recovery steps explicitly (especially for `/ready` dependency failures and rate-limiting behavior).

### Consistency
- Standardize “Prerequisites / Configuration / Troubleshooting / Security Notes” sections across:
  - deployment guides
  - developer guide pages
  - engineering standards

### Traceability
- For critical pages, add a small “Source” block that links to the authoritative code/module (e.g., API middleware docs → `src/api/*`, rate limiting → `src/api/rate_limit.py`).
- Optionally add a lightweight `docs/traceability.yml` mapping (doc → code paths) and validate it in CI.

### Cross-repo accuracy (Kosmos-API / CosmOS)
- Those codebases are not present in this workspace, so cross-repo validation cannot be performed automatically here.
- Recommended pattern: add them as git submodules or CI checkouts and extend validation to compare their OpenAPI / Docker workflows too.
