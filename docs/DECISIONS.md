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

## Chunking strategy: fixed-size with overlap, token-based
**Why:** Industry-standard baseline for RAG. Chunking by token count (via
tiktoken, cl100k_base encoding) rather than characters or words ensures
predictable sizing relative to what embedding models and LLMs actually
consume — character/word counts don't map consistently to tokens.
Overlap (50 tokens default) ensures content split across a chunk boundary
remains findable in at least one adjacent chunk during retrieval, rather
than being silently lost. Alternative considered: semantic chunking
(splitting on meaning boundaries) — rejected for now as it requires LLM
calls just to determine chunk boundaries, adding cost/complexity before
the core pipeline is proven. Documented as a legitimate future iteration.
**Date:** 2026-06-19

## Document type support: PDF only (initial)
**Why:** Banking/health documents arrive as PDFs in practice — .txt and
.docx support would add parsing code paths for formats the target domain
doesn't actually use. Scope discipline: build PDF ingestion robustly
(multi-page, scanned-PDF detection) rather than three formats shallowly.

## Sample/test documents excluded from git
**Why:** Test PDFs may contain personal/sensitive data (e.g. resume with
real contact info). data/sample_docs/ folder structure is preserved via
.gitkeep, but actual PDF contents are gitignored — prevents accidental
permanent exposure in git history on a public portfolio repo.
**Date:** 2026-06-19

## Embedding model: sentence-transformers all-MiniLM-L6-v2 (local, not API) — SUPERSEDED, see below
**Why:** $0 budget constraint — hosted embedding APIs (OpenAI, Cohere) are
metered and would add a second paid dependency on top of Groq. Local model
runs entirely on-machine after one-time ~90MB download, no network required
at inference time, no rate limits, no API key. all-MiniLM-L6-v2 is the
standard lightweight sentence-transformers model: fast, well-tested,
384-dimension output, competitive retrieval quality for this scale.
Tradeoff: slightly lower quality ceiling than large hosted models; acceptable
for a portfolio project at this document scale.
**Date:** 2026-06-19
**Status:** Superseded on Render deployment — see "Embedding model: HuggingFace
Inference API" entry below. Kept here rather than deleted so the reasoning
trail (and why it changed) stays visible.

## Vector storage: text in Qdrant payload alongside vector
**Why:** During retrieval, the LLM needs the actual chunk text, not just a
vector ID. Storing text in payload means one Qdrant query returns both the
similar vectors and the text needed to build the LLM prompt — no second
lookup to a separate store. Tradeoff: payload storage increases per-point
size in Qdrant; negligible at portfolio scale, revisit if document volume
scales to millions of chunks.
**Date:** 2026-06-19

## Point IDs: UUID (not sequential integers)
**Why:** UUIDs are stateless and collision-resistant — no need to track
"last used ID" across ingestion runs or coordinate between parallel ingest
operations. Sequential integers would require either a counter persisted
somewhere or a database sequence, both adding state management complexity
for no benefit at this scale.
**Date:** 2026-06-19

## Embedding model: HuggingFace Inference API (supersedes local sentence-transformers)
**Why:** The local `all-MiniLM-L6-v2` decision (2026-06-19, above) held up in
development but failed in production. Render's free tier caps RAM at 512MB;
loading `sentence-transformers` + PyTorch into memory OOM-crashed the service
on deploy. Rather than upgrade to a paid Render tier (violates $0 budget rule),
swapped to calling the same model via HuggingFace's Inference API over HTTP
(httpx), removing PyTorch and sentence-transformers from requirements.txt
entirely.
**Tradeoff:** Query latency now includes a network round-trip to HF's servers,
and embedding availability depends on HF API uptime — the original decision's
"no external dependency on the inference path" reasoning no longer holds and
is explicitly retired by this entry.
**What breaks if you change it back:** Reverting to local inference on Render's
free tier reproduces the OOM crash on deploy. A local-inference revert would
require either upgrading Render's plan (breaks $0 budget rule) or moving to a
host with more RAM.
**Date:** 2026-07-02
**Supersedes:** "Embedding model: sentence-transformers all-MiniLM-L6-v2 (local, not API)" above