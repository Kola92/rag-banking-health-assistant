# Architecture Decisions Log

Format: Decision — Why — Date

---

## Python env tool: venv (not Poetry)
**Why:** venv is built into Python, zero extra install, well-documented for
Windows/Git Bash. Poetry is arguably more "production-grade" for dependency
resolution, but adds a second new tool on top of learning Python/FastAPI
simultaneously. Deliberate scope control — solve one new-tool problem at a
time. Can migrate later as a documented follow-up.
**Date:** 2026-06-18

## Vector DB: Qdrant Cloud free tier (not self-hosted Docker)
**Why:** $0 budget constraint. Free tier requires no card. Removes Docker
as a dependency/failure point while still learning core Python/FastAPI —
fewer moving parts during the learning phase. Documented as a deliberate
tradeoff: self-hosted Qdrant via Docker would give more control and is a
valid future iteration once core pipeline is proven.
**Date:** 2026-06-18

## Folder structure: api/ vs services/ split
**Why:** Routes (api/v1/) stay thin — HTTP concerns only (request parsing,
response shaping, status codes). Business logic (services/) is independently
unit-testable without a running server. This is a deliberate separation of
concerns, not boilerplate — makes the RAG pipeline logic testable in
isolation from the web framework.
**Date:** 2026-06-18

## Config: pydantic-settings over scattered os.environ calls
**Why:** Centralizes all environment-derived config into one typed object
(app/core/config.py). Required fields with no default (e.g. qdrant_api_key)
cause the app to fail fast and loudly on startup if missing, rather than
failing silently later mid-request. Fintech-adjacent project — security
and predictability over convenience.
**Date:** 2026-06-18

## First endpoint: /health, not a root "hello world"
**Why:** /health is what load balancers, container orchestrators, and
uptime monitors actually check in production. Building this habit from
commit #1 means the project reflects real deployment patterns, not
tutorial patterns.
**Date:** 2026-06-18
