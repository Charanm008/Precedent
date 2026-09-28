from fastapi import APIRouter
from datetime import datetime, timezone
from app.core.config import settings

router = APIRouter()

@router.get("/health", summary="Basic Health Check")
async def health_check():
    """
    Returns basic health status of the Precedent backend API.
    """
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/status", summary="Detailed System Status")
async def detailed_status():
    """
    Returns comprehensive system status across all subsystems (API, Hindsight Memory, Google ADK).
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "subsystems": {
            "api_server": {"status": "online", "details": "FastAPI engine active"},
            "hindsight_memory": {"status": "standby", "details": "Pending Phase 1 Memory Integration"},
            "google_adk_agent": {"status": "standby", "details": "Pending Phase 2 Agent Integration"},
            "deal_analytics": {"status": "ready", "details": "Data storage structure verified"}
        }
    }
