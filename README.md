![License](https://img.shields.io/badge/license-MIT-blue.svg)
   ![Node](https://img.shields.io/badge/node-20+-green.svg)
   ![Status](https://img.shields.io/badge/status-live-brightgreen.svg)

# RAG Banking & Health Document Assistant

A production-grade Retrieval-Augmented Generation (RAG) system for querying
Nigerian banking regulations and health insurance documents via natural language.

Built as a portfolio anchor project demonstrating senior full-stack engineering
across Python/FastAPI backend, vector database integration, local LLM inference,
and a polished Next.js frontend.

---

## Live demo

**Frontend:** https://rag-banking-health-assistant-c8f7.vercel.app
**Backend:** https://rag-banking-health-assistant.onrender.com
**API docs (Swagger):** https://rag-banking-health-assistant.onrender.com/docs

**Try asking:**
- "What are the consumer protection rights of bank customers in Nigeria?"
- "What are the data localisation requirements for Nigerian payment systems?"
- "What actions should banks take regarding OFAC designations?"

---

## Architecture
User uploads PDF → text extracted → chunked (500 tokens, 50 overlap)

→ embedded (all-MiniLM-L6-v2, 384 dims) → stored in Qdrant Cloud
User asks question → question embedded → top-k chunks retrieved by cosine similarity

→ chunks + question sent to Llama 3.1 (via Groq) → grounded answer returned

→ displayed in Next.js chat UI with expandable source citations

### Stack

| Layer | Technology | Why |
|---|---|---|
| Backend | FastAPI (Python 3.12) | Async-native, auto Swagger docs, Pydantic validation |
| Vector DB | Qdrant Cloud (free tier) | Managed, no Docker dependency, production-grade |
| Embeddings | `all-MiniLM-L6-v2` via HuggingFace Inference API | Local PyTorch OOMs on Render's 512MB free tier — offloading inference to HF API removes the RAM constraint at $0 cost |
| LLM | Llama 3.1 8B via Groq API | Fast inference, free tier, OpenAI-compatible API |
| Frontend | Next.js 16 + Tailwind CSS | App Router, dark/light theme, fully responsive |

---

## Key engineering decisions

**Why local embeddings over OpenAI/Cohere:** $0 cost, no rate limits, no
external dependency on the critical inference path. `all-MiniLM-L6-v2`
delivers competitive retrieval quality at this document scale.

**Why fixed-size chunking with overlap:** Industry-standard RAG baseline.
Token-based sizing (via tiktoken) ensures predictable context budget usage.
50-token overlap prevents meaning loss at chunk boundaries.

**Why Qdrant payload indexing:** Filter-based deletion (for idempotent
re-ingestion) requires a keyword index on the `source` field — Qdrant
refuses unindexed full-collection scans for performance reasons.

**Why `api/` vs `services/` separation:** Routes stay thin (HTTP concerns only).
Services hold domain logic and are independently testable without a running
server. See `docs/DECISIONS.md` for the full ADR log.

---

## Local setup

### Prerequisites
- Python 3.12+
- Node.js 20+
- Qdrant Cloud account (free tier — [cloud.qdrant.io](https://cloud.qdrant.io))
- Groq API key (free tier — [console.groq.com](https://console.groq.com))

### Backend

```bash
cd backend
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
cp .env.example .env
# Fill in QDRANT_URL, QDRANT_API_KEY, GROQ_API_KEY in .env
uvicorn app.main:app --reload
```

Visit **http://localhost:8000/docs** for the interactive Swagger UI.

### Frontend

```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

Visit **http://localhost:3000**

### Seed documents (optional CLI)

```bash
cd backend
source venv/Scripts/activate
python ../scripts/seed_documents.py data/sample_docs/your-document.pdf
```

---

## Project structure
rag-banking-health-assistant/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Thin HTTP route handlers
│   │   ├── services/        # Domain logic (loader, chunker, embeddings,
│   │   │                    #   vector_store, retriever, rag_chain)
│   │   ├── models/          # Pydantic request/response schemas
│   │   └── core/            # Config (pydantic-settings), logging
│   └── requirements.txt
├── frontend/
│   ├── app/                 # Next.js App Router pages + layout
│   ├── components/          # ChatMessage, SourceCard, UploadPanel, ThemeToggle
│   └── lib/                 # API client (typed fetch wrappers)
├── scripts/
│   └── seed_documents.py    # CLI ingestion tool
└── docs/
├── ARCHITECTURE.md      # System design + current status
└── DECISIONS.md         # ADR-style decision log

---

## API reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health check |
| `POST` | `/api/v1/ingest` | Upload PDF for ingestion (multipart/form-data) |
| `POST` | `/api/v1/query` | Ask a question, get grounded answer + sources |

Full interactive docs at `/docs` (Swagger UI).

---

## Author

**Adekola Olawale** — Senior Full-Stack Engineer  
[LinkedIn](https://linkedin.com/in/adekola-olawale) ·
[Medium @Adekola_Olawale](https://medium.com/@Adekola_Olawale) ·
[GitHub @Kola92](https://github.com/Kola92)
