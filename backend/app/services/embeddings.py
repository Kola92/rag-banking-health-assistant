from sentence_transformers import SentenceTransformer

# all-MiniLM-L6-v2: lightweight, fast, 384-dimension output vectors.
# First call downloads the model (~90MB) to a local cache.
# Every subsequent call loads from that cache — no network required.
# 384 dimensions is the number Qdrant collection must be configured to match.
MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSIONS = 384

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    """
    Return the embedding model, loading it once and caching in memory.

    Why a module-level singleton with lazy loading:
    - Loading a sentence-transformers model takes ~1-2 seconds and allocates
      memory. Doing it on every embed_texts() call would be a serious
      performance problem — slow on the first request of every batch, and
      wasteful on subsequent ones.
    - Lazy loading (only on first call, not at import time) means the model
      isn't loaded during tests or on startup if embeddings aren't needed yet.
    - The module-level _model variable persists for the lifetime of the process,
      so all subsequent calls reuse the already-loaded model.
    """
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of text strings.

    Args:
        texts: List of text strings to embed. Typically chunk_text() output.

    Returns:
        List of embedding vectors, one per input string.
        Each vector is a list of 384 floats (EMBEDDING_DIMENSIONS).

    Why batch embedding (list input) instead of one string at a time:
        sentence-transformers processes batches significantly faster than
        individual strings due to GPU/CPU vectorisation. Always pass all
        chunks together, not in a loop one by one.
    """
    if not texts:
        return []

    model = get_model()
    embeddings = model.encode(texts, show_progress_bar=True)

    # .encode() returns a numpy ndarray — convert to plain Python list[list[float]]
    # so the output is JSON-serialisable and Qdrant-compatible without
    # importing numpy anywhere outside this file.
    return embeddings.tolist()
