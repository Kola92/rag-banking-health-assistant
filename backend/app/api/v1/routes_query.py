from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse, ChunkResult
from app.services.rag_chain import answer

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Ask a question and get an answer grounded in ingested documents.

    Pipeline: embed question → retrieve top-k chunks from Qdrant →
    build prompt with context → generate answer via Llama 3 on Groq →
    return answer + sources + chunks used.
    """
    try:
        result = answer(request.question, top_k=request.top_k)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"RAG chain failed: {str(e)}",
        )

    return QueryResponse(
        answer=result["answer"],
        sources=result["sources"],
        chunks=[ChunkResult(**c) for c in result["chunks"]],
        model=result["model"],
    )
