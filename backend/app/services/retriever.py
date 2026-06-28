from qdrant_client.models import ScoredPoint
from app.services.embeddings import embed_texts
from app.services.vector_store import get_client, COLLECTION_NAME


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """
    Find the most semantically similar chunks to a query string.

    Pipeline:
        1. Embed the query using the same model used during ingestion.
        2. Search Qdrant for the top_k closest vectors by cosine similarity.
        3. Return the matching chunks with their text, source, and score.

    Args:
        query:  The user's question in plain text.
        top_k:  Number of chunks to retrieve. Default 5.
                Why 5: enough context for the LLM to synthesise a good answer
                without exceeding the prompt context budget. Tunable later.

    Returns:
        List of dicts, each containing:
            - text:   The raw chunk text (goes into the LLM prompt as context)
            - source: The filename the chunk came from (for citations)
            - score:  Cosine similarity score 0.0–1.0 (higher = more similar)

    Why we embed the query with the SAME model used at ingestion:
        Vector similarity only makes sense when both vectors live in the same
        embedding space. Using a different model for queries vs ingestion would
        be like measuring distance in miles on one side and kilometres on the
        other — the numbers are incompatible and retrieval would return
        meaningless results with no error to tell you why.
    """
    if not query.strip():
        return []

    # Embed the query — embed_texts() takes a list, we pass one item
    query_vector = embed_texts([query])[0]

    client = get_client()

    results: list[ScoredPoint] = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True,   # return text + source from payload, not just IDs
    )

    return [
        {
            "text": hit.payload.get("text", ""),
            "source": hit.payload.get("source", "unknown"),
            "score": round(hit.score, 4),
        }
        for hit in results
    ]
