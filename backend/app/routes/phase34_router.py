"""
Phase 3 & 4 Router Registration

This module provides a single include function so that main.py
can register Phase 3 (intelligence) and Phase 4 (agents) routes
with a single import — without requiring main.py to be rewritten.

Usage in main.py (Phase 1 version):
    from app.routes.phase34_router import register_phase34_routes
    register_phase34_routes(app)
"""

from fastapi import FastAPI

from .intelligence import router as intelligence_router
from .agents import router as agents_router


def register_phase34_routes(app: FastAPI) -> None:
    """Register Phase 3 and Phase 4 routers onto an existing FastAPI app."""
    app.include_router(intelligence_router)
    app.include_router(agents_router)
