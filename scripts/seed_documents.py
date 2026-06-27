"""
Seed script: load a PDF, chunk it, embed it, store in Qdrant.

Usage (run from backend/ with venv activated):
    python ../scripts/seed_documents.py data/sample_docs/yourfile.pdf
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.services.document_loader import load_pdf, DocumentLoadError
from app.services.chunker import chunk_text
from app.services.embeddings import embed_texts
from app.services.vector_store import store_chunks


def seed_document(file_path: str, chunk_size: int = 500, chunk_overlap: int = 50):
    path = Path(file_path)
    print(f"\nSeeding: {path.name}")
    print("-" * 40)

    # 1. Load
    try:
        text = load_pdf(file_path)
    except DocumentLoadError as e:
        print(f"FAILED: {e}")
        sys.exit(1)
    print(f"Extracted {len(text)} characters")

    # 2. Chunk
    chunks = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    print(f"Split into {len(chunks)} chunks (size={chunk_size}, overlap={chunk_overlap})")

    # 3. Embed
    print("Generating embeddings...")
    vectors = embed_texts(chunks)
    print(f"Generated {len(vectors)} vectors ({len(vectors[0])} dims each)")

    # 4. Store
    print("Storing in Qdrant...")
    stored = store_chunks(chunks, vectors, source=path.name)
    print(f"Stored {stored} points in Qdrant collection 'documents'")

    print("\nDone.")
    return stored


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/seed_documents.py <path-to-pdf>")
        sys.exit(1)

    seed_document(sys.argv[1])
