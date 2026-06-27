from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.core.config import settings
from app.services.embeddings import EMBEDDING_DIMENSIONS
import uuid


COLLECTION_NAME = "documents"

_client: QdrantClient | None = None


def get_client() -> QdrantClient:
    """
    Return the Qdrant client, initialised once and cached in memory.

    Why a singleton: QdrantClient holds an HTTP connection pool internally.
    Creating a new client on every call would open and close connections
    repeatedly — wasteful and slow. One client per process, reused everywhere.
    """
    global _client
    if _client is None:
        _client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
    return _client


def ensure_collection() -> None:
    """
    Create the Qdrant collection if it doesn't already exist.

    Why idempotent (safe to call multiple times):
    Calling this on every app startup or before every ingest operation means
    we never have to separately manage "did I create the collection yet?" state.
    If it exists, we leave it alone. If not, we create it. No manual setup step,
    no silent failure if someone runs the seed script on a fresh cluster.
    """
    client = get_client()
    existing = [c.name for c in client.get_collections().collections]

    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_DIMENSIONS,  # must match all-MiniLM-L6-v2 output: 384
                distance=Distance.COSINE,
            ),
        )
        print(f"Created collection: {COLLECTION_NAME}")
    else:
        print(f"Collection already exists: {COLLECTION_NAME}")


def store_chunks(chunks: list[str], vectors: list[list[float]], source: str) -> int:
    """
    Store text chunks and their embedding vectors in Qdrant.

    Args:
        chunks:  The raw text chunks (from chunker.py).
        vectors: The embedding vectors (from embeddings.py), same order/length.
        source:  The source filename — stored as metadata so retrieval results
                 can tell you which document a chunk came from.

    Returns:
        Number of points successfully stored.

    Why UUID for point IDs:
        Qdrant requires each point to have a unique ID (integer or UUID).
        UUIDs generated here rather than sequential integers because:
        - Sequential integers require tracking "what was the last ID" across
          calls, which means state management we don't need.
        - UUIDs are stateless, collision-resistant, and work correctly even
          if you ingest multiple documents in parallel later.

    Why store chunk text in payload:
        Qdrant stores vectors for similarity search, but during retrieval
        we need the actual text to send to the LLM as context. Storing it
        in the payload alongside the vector means one round-trip to Qdrant
        returns everything needed — no second lookup to a separate store.
    """
    if len(chunks) != len(vectors):
        raise ValueError(
            f"chunks and vectors must have the same length "
            f"(got {len(chunks)} chunks, {len(vectors)} vectors)"
        )

    client = get_client()
    ensure_collection()

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "text": chunk,
                "source": source,
            },
        )
        for chunk, vector in zip(chunks, vectors)
    ]

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    return len(points)
