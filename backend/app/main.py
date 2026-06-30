from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.routes_ingest import router as ingest_router
from app.api.v1.routes_query import router as query_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
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
    """
    Health check endpoint.
    Returns app status and version.
    Used by load balancers and monitoring tools to verify the service is alive.
    """
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }
