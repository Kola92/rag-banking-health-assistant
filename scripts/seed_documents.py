"""
Seed script: load a PDF, chunk it, print summary stats.

Usage (run from backend/ with venv activated):
    python ../scripts/seed_documents.py data/sample_docs/yourfile.pdf

This script currently stops at chunking — Qdrant storage will be added
in the next phase once vector_store.py and embeddings.py exist.
"""

import sys
from pathlib import Path

# Allow running this script from outside backend/ by adding backend/ to
# the import path, since document_loader/chunker live under backend/app/
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.services.document_loader import load_pdf, DocumentLoadError
from app.services.chunker import chunk_text


def seed_document(file_path: str, chunk_size: int = 500, chunk_overlap: int = 50):
    print(f"Loading: {file_path}")

    try:
        text = load_pdf(file_path)
    except DocumentLoadError as e:
        print(f"FAILED to load document: {e}")
        sys.exit(1)

    print(f"  Extracted {len(text)} characters")

    chunks = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    print(f"  Split into {len(chunks)} chunks (chunk_size={chunk_size}, overlap={chunk_overlap})")

    avg_len = sum(len(c) for c in chunks) / len(chunks) if chunks else 0
    print(f"  Average chunk length: {avg_len:.0f} characters")

    print("\n  First chunk preview:")
    print(f"  {chunks[0][:200]}...")

    print("\n  [Next phase: embeddings.py + vector_store.py will store these in Qdrant]")

    return chunks


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/seed_documents.py <path-to-pdf>")
        sys.exit(1)

    seed_document(sys.argv[1])
