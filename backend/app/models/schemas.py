from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="The question to answer from the ingested documents.",
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of document chunks to retrieve before generation.",
    )


class ChunkResult(BaseModel):
    text: str
    source: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    chunks: list[ChunkResult]
    model: str


class IngestResponse(BaseModel):
    filename: str
    chunks_stored: int
    message: str
