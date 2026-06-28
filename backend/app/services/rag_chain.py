from groq import Groq
from app.core.config import settings
from app.services.retriever import retrieve

# Model choice: llama-3.1-8b-instant
# Why: free on Groq, fast inference, capable enough for RAG-style Q&A where
# the answer is grounded in retrieved context. The LLM's job here isn't to
# "know" things from training — it's to synthesise chunks we provide into a
# coherent answer. A smaller model does this well when retrieval is solid.
MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """You are a precise document assistant for banking and health documents.

Your rules:
1. Answer ONLY using the context chunks provided in the user message.
2. If the answer is not in the context, say exactly: "I could not find that information in the provided documents."
3. Never use your training knowledge to fill gaps — only what is explicitly in the context.
4. Always cite which document your answer came from (the source field).
5. Be concise and factual. No speculation.

These rules exist because this is a fintech-adjacent system — accuracy and
grounding matter more than appearing helpful when information is missing."""


def build_prompt(query: str, context_chunks: list[dict]) -> str:
    """
    Format retrieved chunks into a structured prompt for the LLM.

    Why bundle context + question in the user message (not system):
    The system message sets persistent behaviour rules. The user message
    carries the actual data for this specific request. Putting context
    in the user message means each request is self-contained — the model
    gets fresh context per query, not stale context from a previous turn.
    """
    if not context_chunks:
        context_text = "No relevant context found in the documents."
    else:
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            context_parts.append(
                f"[Chunk {i} | Source: {chunk['source']} | Score: {chunk['score']}]\n{chunk['text']}"
            )
        context_text = "\n\n---\n\n".join(context_parts)

    return f"""Context from documents:

{context_text}

---

Question: {query}

Answer based strictly on the context above:"""


def answer(query: str, top_k: int = 5) -> dict:
    """
    Full RAG chain: retrieve relevant chunks then generate a grounded answer.

    Args:
        query:  The user's question in plain text.
        top_k:  Number of chunks to retrieve from Qdrant before generation.

    Returns:
        Dict containing:
            - answer:   The LLM-generated response, grounded in retrieved chunks
            - sources:  List of source filenames the answer drew from
            - chunks:   The raw retrieved chunks (text, source, score)
            - model:    The model used for generation

    Why return chunks alongside the answer:
        Transparency. The frontend can show users exactly what context the
        answer was based on — a standard pattern in production RAG systems
        called "citations" or "grounding evidence". Without this, users have
        no way to verify the answer or know which document to look at.
    """
    # Step 1: Retrieve
    chunks = retrieve(query, top_k=top_k)

    # Step 2: Build prompt
    prompt = build_prompt(query, chunks)

    # Step 3: Generate
    client = Groq(api_key=settings.groq_api_key)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        temperature=0.1,  # low temperature = more deterministic, less creative
                          # for factual Q&A over documents you want consistency,
                          # not variety. 0.0 is fully deterministic, 0.1 gives
                          # tiny wiggle room without being unpredictable.
        max_tokens=1024,
    )

    answer_text = response.choices[0].message.content
    sources = list({chunk["source"] for chunk in chunks})  # deduplicated

    return {
        "answer": answer_text,
        "sources": sources,
        "chunks": chunks,
        "model": MODEL,
    }
