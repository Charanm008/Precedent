from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

from .database import engine, Base  # noqa: E402
from .routes import deals as deals_router  # noqa: E402
from .routes import interactions as interactions_router  # noqa: E402

# Import models so SQLAlchemy registers them before create_all
from .models import db_models  # noqa: F401, E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Precedent API", version="0.1.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(deals_router.router)
app.include_router(interactions_router.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "precedent-backend"}
