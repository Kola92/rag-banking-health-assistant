# Architecture

## Status: Phase 1 complete — Backend scaffold + health check

## System overview (target state)
User uploads a document (PDF/text) → document is chunked → chunks are
embedded → embeddings stored in Qdrant Cloud → user asks a question →
question is embedded → top-k similar chunks retrieved from Qdrant →
chunks + question sent to Grok API as context → Grok generates a grounded
answer → returned to user via FastAPI → consumed by Next.js frontend.

## Current implementation (Phase 1)
- FastAPI app (`backend/app/main.py`) with one endpoint: `GET /health`
- Config layer (`backend/app/core/config.py`) loads typed settings from
  `.env` via pydantic-settings — required fields (Qdrant/Grok keys) fail
  the app fast on startup if missing.
- Swagger UI auto-generated at `/docs` from route docstrings — used as the manual testing surface before any frontend exists.

## Not yet built
- Document ingestion (services/document_loader.py)
- Chunking strategy (services/chunker.py)
- Embeddings generation (services/embeddings.py)
- Qdrant connection + storage (services/vector_store.py)
- Retrieval logic
- Grok generation chain (services/rag_chain.py)
- API routes wrapping ingestion + query
- Next.js frontend

## Why backend-first
The API contract must exist and be proven (via Swagger UI testing) before any frontend code is written. This avoids guessing at response shapes and rebuilding UI components later. See docs/DECISIONS.md for the full reasoning log.
