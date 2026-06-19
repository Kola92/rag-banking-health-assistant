# Architecture

## Status: Phase 2 complete — Document ingestion (load + chunk)

## System overview (target state)
User uploads a document (PDF/text) → document is chunked → chunks are
embedded → embeddings stored in Qdrant Cloud → user asks a question →
question is embedded → top-k similar chunks retrieved from Qdrant →
chunks + question sent to Grok API as context → Grok generates a grounded
answer → returned to user via FastAPI → consumed by Next.js frontend.

## Current implementation

### Phase 1 — Backend scaffold
- FastAPI app (`backend/app/main.py`) with `GET /health` endpoint
- Config layer (`backend/app/core/config.py`) — typed settings from `.env`
  via pydantic-settings, required fields fail fast on missing config
- Swagger UI auto-generated at `/docs`

### Phase 2 — Document ingestion
- `backend/app/services/document_loader.py` — extracts raw text from PDF
  via pypdf. Raises `DocumentLoadError` (custom exception) on missing
  file, non-PDF input, or scanned/image-only PDFs with no text layer.
- `backend/app/services/chunker.py` — splits text into overlapping,
  token-counted chunks (tiktoken, cl100k_base). Default: 500 tokens/chunk,
  50 token overlap. Guards against invalid overlap >= chunk_size
  (would cause infinite loop).
- `scripts/seed_documents.py` — CLI entrypoint wiring loader + chunker,
  prints chunk stats. Currently stops before storage (next phase).

## Not yet built
- Embeddings generation (services/embeddings.py)
- Qdrant connection + storage (services/vector_store.py)
- Retrieval logic
- Grok generation chain (services/rag_chain.py)
- API routes wrapping ingestion + query
- Next.js frontend

## Why backend-first
The API contract must exist and be proven (via Swagger UI testing) before
any frontend code is written. See docs/DECISIONS.md for full reasoning.
