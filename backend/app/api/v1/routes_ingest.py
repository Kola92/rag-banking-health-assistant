from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import tempfile
import shutil

from app.models.schemas import IngestResponse
from app.services.document_loader import load_pdf, DocumentLoadError
from app.services.chunker import chunk_text
from app.services.embeddings import embed_texts
from app.services.vector_store import store_chunks, delete_by_source

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)):
    """
    Upload a PDF document to be ingested into the vector store.

    Pipeline: upload → save to temp file → extract text → chunk →
    embed → delete old chunks for this source → store new chunks.

    Why a temp file instead of reading bytes directly:
        pypdf requires a file path or file-like object. FastAPI's UploadFile
        gives us a stream. Writing to a named temp file is the cleanest way
        to bridge these two interfaces without loading the entire PDF into
        memory as bytes and wrapping it in BytesIO (which works but is less
        readable and harder to debug).
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported. Please upload a .pdf file.",
        )

    # Save upload to a temp file so pypdf can read it
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        text = load_pdf(tmp_path)
    except DocumentLoadError as e:
        tmp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=str(e))
    finally:
        tmp_path.unlink(missing_ok=True)

    chunks = chunk_text(text)
    vectors = embed_texts(chunks)

    # Deduplicate: remove any existing chunks for this source before storing
    delete_by_source(file.filename)
    stored = store_chunks(chunks, vectors, source=file.filename)

    return IngestResponse(
        filename=file.filename,
        chunks_stored=stored,
        message=f"Successfully ingested '{file.filename}' into {stored} chunks.",
    )
