# Architecture

## Status: Phase 6 complete — Full backend API proven end-to-end

## System overview (target state)
User uploads a document (PDF) → document is chunked → chunks are embedded
→ embeddings stored in Qdrant Cloud → user asks a question → question is
embedded → top-k similar chunks retrieved from Qdrant → chunks + question
sent to Groq/Llama API as context → Llama generates a grounded answer →
returned via FastAPI → consumed by Next.js frontend.

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
  - delete_by_source(): payload-indexed filter delete for idempotent re-ingestion

### Phase 4 — Retrieval
- retriever.py: embeds query with same model used at ingestion, searches Qdrant
  by cosine similarity, returns top-k chunks with text, source, and score

### Phase 5 — Generation chain
- rag_chain.py: Groq SDK (llama-3.1-8b-instant), temperature=0.1
  System prompt enforces answer-only-from-context constraint (anti-hallucination)
  Returns answer + sources + raw chunks for frontend citation display

### Phase 6 — FastAPI route layer
- POST /api/v1/ingest: multipart PDF upload → full ingestion pipeline
  Deduplicates by source before storing (delete_by_source → store_chunks)
- POST /api/v1/query: JSON question → RAG chain → grounded answer + sources
- Pydantic schemas: QueryRequest, QueryResponse, IngestResponse, ChunkResult

## Full pipeline (proven end-to-end)
### Ingestion
POST /ingest → load_pdf() → chunk_text() → embed_texts() → delete_by_source()
→ store_chunks() → Qdrant Cloud

### Query
POST /query → embed query → Qdrant search → build prompt → Groq/Llama
→ grounded answer + sources

## Ingested documents (current)
- CONSUMER PROTECTION FAQs.pdf (CBN) — 9 chunks
- CIRCULAR ON INTRODUCTION OF MARKET STRUCTURE REQUIREMENTS... (CBN) — 2 chunks
- CIRCULAR TO BANKS AND OFIs ON NIGSAC AND OFAC DESIGNATIONS... (CBN) — 2 chunks

## Not yet built
- Next.js frontend