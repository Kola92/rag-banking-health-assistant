# Architecture

## Status: Phase 3 complete — Embeddings + Vector storage, full ingestion pipeline proven

## System overview (target state)
User uploads a document (PDF) → document is chunked → chunks are embedded
→ embeddings stored in Qdrant Cloud → user asks a question → question is
embedded → top-k similar chunks retrieved from Qdrant → chunks + question
sent to Grok API as context → Grok generates a grounded answer → returned
via FastAPI → consumed by Next.js frontend.

## Completed layers

### Phase 1 — Backend scaffold
- FastAPI app with GET /health, typed config via pydantic-settings, Swagger UI

### Phase 2 — Document ingestion
- document_loader.py: PDF text extraction via pypdf, custom DocumentLoadError
- chunker.py: token-based fixed-size chunking with overlap (tiktoken, cl100k_base)
  Default: 500 tokens/chunk, 50 token overlap
- scripts/seed_documents.py: CLI tool for full ingestion pipeline

### Phase 3 — Embeddings + Vector storage
- embeddings.py: local sentence-transformers (all-MiniLM-L6-v2, 384 dims)
  Singleton model load, batch encoding, numpy→list conversion at boundary
- vector_store.py: Qdrant Cloud client wrapper
  - ensure_collection(): idempotent collection creation (COSINE distance, 384 dims)
  - store_chunks(): upsert points with UUID IDs, text+source in payload

## Full ingestion pipeline (proven)
load_pdf() → chunk_text() → embed_texts() → store_chunks() → Qdrant Cloud

## Not yet built
- Retrieval logic (search by query embedding, return top-k chunks)
- Grok API generation chain (rag_chain.py)
- FastAPI routes wrapping ingestion + query
- Next.js frontend
