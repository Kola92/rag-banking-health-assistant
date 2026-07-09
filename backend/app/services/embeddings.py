import httpx
from app.core.config import settings

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSIONS = 384
HF_API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL_NAME}/pipeline/feature-extraction"


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings via Hugging Face Inference API.

    Why remote API instead of local model on Render:
        sentence-transformers + PyTorch requires ~500MB RAM.
        Render free tier provides 512MB total — the process OOMs before
        the port binds. HF Inference API runs the same model remotely,
        returning identical 384-dim vectors with zero local memory overhead.
        Tradeoff: network latency per embedding call (~200-500ms) vs
        local inference (~50ms). Acceptable for a portfolio project where
        correctness > latency. Production fix: upgrade instance or use
        a dedicated embedding service.

    Args:
        texts: List of strings to embed.

    Returns:
        List of 384-dimensional float vectors, one per input string.
    """
    if not texts:
        return []

    headers = {"Authorization": f"Bearer {settings.hf_api_key}"}

    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            HF_API_URL,
            headers=headers,
            json={"inputs": texts, "options": {"wait_for_model": True}},
        )
        response.raise_for_status()

    result = response.json()

    # HF returns list of lists for batch input — already the right shape
    # For single input it may return a flat list — normalize it
    if isinstance(result[0], float):
        return [result]

    return result