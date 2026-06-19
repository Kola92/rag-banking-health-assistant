# RAG Banking & Health Document Assistant

A Retrieval-Augmented Generation (RAG) system for answering questions over banking/health documents. Built as a portfolio project demonstrating production-grade backend architecture and RAG pipeline design.

## Status
🚧 Phase 1 complete — backend scaffold + health check endpoint live.

## Stack
- **Backend:** FastAPI (Python 3.12)
- **Vector DB:** Qdrant Cloud (free tier)
- **LLM:** Grok API
- **Frontend:** Next.js (not yet built — backend-first approach)

## Why this exists
Portfolio anchor project for senior fintech engineering roles. Built deliberately to gain hands-on Python/FastAPI experience and produce written technical content (see Medium: @Adekola_Olawale).

## Local setup (backend)

```bash
cd backend
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
cp .env.example .env           # then fill in real Qdrant/Grok keys
uvicorn app.main:app --reload
```

Visit:
- http://127.0.0.1:8000/health — health check
- http://127.0.0.1:8000/docs — Swagger UI (interactive API docs)

## Documentation
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — system design, pipeline shape, current status
- [docs/DECISIONS.md](docs/DECISIONS.md) — why each major technical choice was made
- [docs/API.md](docs/API.md) — endpoint contracts (added as routes are built)

## Build order
1. ✅ Backend scaffold + FastAPI hello-world
2. ✅ Document ingestion (PDF/text loading + chunking)
3. ⬜ Embeddings generation
4. ⬜ Qdrant Cloud connection + vector storage
5. ⬜ Retrieval logic
6. ⬜ Grok API generation chain
7. ⬜ FastAPI routes wrapping the above
8. ⬜ Next.js frontend
