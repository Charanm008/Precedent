# pyrefly: ignore [missing-import]
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure backend root is in sys.path when running main.py directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.api.v1.router import api_router

from .database import engine, Base
from .routes import deals as deals_router
from .routes import interactions as interactions_router
from .routes.phase34_router import register_phase34_routes

# Import models so SQLAlchemy registers them before create_all
from .models import db_models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Phase 0 API V1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Phase 1 Deal/Interaction API
app.include_router(deals_router.router)
app.include_router(interactions_router.router)
# Phase 3 & 4 Intelligence + AI Agents API
register_phase34_routes(app)

@app.get("/", summary="Root API Info")
async def root():
    return {
        "title": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.PROJECT_DESCRIPTION,
        "docs": "/docs",
        "api_v1": settings.API_V1_STR,
        "status": "online",
    }


@app.get("/health", summary="Top-level Health Endpoint")
async def top_level_health():
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }