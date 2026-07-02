from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api.v1.routes_ingest import router as ingest_router
from app.api.v1.routes_query import router as query_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-warm embedding model after server binds — prevents cold start
    # timeout on Render free tier where model load takes 30-60s
    from app.services.embeddings import get_model
    get_model()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://rag-banking-health-assistant.vercel.app",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest_router, prefix="/api/v1", tags=["Ingestion"])
app.include_router(query_router, prefix="/api/v1", tags=["Query"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }