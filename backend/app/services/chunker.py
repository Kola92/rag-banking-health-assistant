import tiktoken


# cl100k_base is the tokenizer used by GPT-4 / GPT-3.5 family.
# We use it as a reasonably accurate token-count approximation even though
# generation uses Grok, not OpenAI — exact tokenizer parity isn't critical
# here; what matters is consistent, predictable chunk sizing.
_ENCODING = tiktoken.get_encoding("cl100k_base")


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[str]:
    """
    Split text into overlapping chunks, sized by token count (not characters).

    Args:
        text: The raw text to split.
        chunk_size: Target number of tokens per chunk.
        chunk_overlap: Number of tokens shared between consecutive chunks,
            to preserve context across chunk boundaries.

    Returns:
        A list of text chunks, in original order.

    Raises:
        ValueError: If chunk_overlap >= chunk_size (would cause an
            infinite loop or zero/negative forward progress).
    """
    if chunk_overlap >= chunk_size:
        raise ValueError(
            f"chunk_overlap ({chunk_overlap}) must be smaller than "
            f"chunk_size ({chunk_size})"
        )

    tokens = _ENCODING.encode(text)
    total_tokens = len(tokens)

    if total_tokens == 0:
        return []

    chunks = []
    start = 0

    while start < total_tokens:
        end = min(start + chunk_size, total_tokens)
        chunk_tokens = tokens[start:end]
        chunk_str = _ENCODING.decode(chunk_tokens)
        chunks.append(chunk_str)

        if end == total_tokens:
            break

        start += chunk_size - chunk_overlap

    return chunks
