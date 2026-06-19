from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)


@app.get("/health")
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
