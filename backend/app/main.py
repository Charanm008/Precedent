# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import sys
import os

# Ensure backend root is in sys.path when running main.py directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API V1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", summary="Root API Info")
async def root():
    return {
        "title": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.PROJECT_DESCRIPTION,
        "docs": "/docs",
        "api_v1": settings.API_V1_STR,
        "status": "online"
    }

@app.get("/health", summary="Top-level Health Endpoint")
async def top_level_health():
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
