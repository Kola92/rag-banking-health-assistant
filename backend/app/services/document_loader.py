from pathlib import Path
from pypdf import PdfReader


class DocumentLoadError(Exception):
    """Raised when a document cannot be loaded or contains no extractable text."""
    pass


def load_pdf(file_path: str | Path) -> str:
    """
    Extract raw text from a PDF file.

    Args:
        file_path: Path to the PDF file.

    Returns:
        The concatenated text content of all pages, separated by newlines.

    Raises:
        DocumentLoadError: If the file doesn't exist, isn't a valid PDF,
            or contains no extractable text (e.g. a scanned image PDF
            with no OCR layer).
    """
    path = Path(file_path)

    if not path.exists():
        raise DocumentLoadError(f"File not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise DocumentLoadError(f"Not a PDF file: {path}")

    try:
        reader = PdfReader(path)
    except Exception as e:
        raise DocumentLoadError(f"Failed to open PDF {path}: {e}") from e

    pages_text = []
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if text:
            pages_text.append(text)

    full_text = "\n".join(pages_text)

    if not full_text.strip():
        raise DocumentLoadError(
            f"No extractable text found in {path}. "
            "This may be a scanned/image-only PDF requiring OCR, "
            "which this loader does not currently support."
        )

    return full_text
