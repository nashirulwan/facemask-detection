"""FastAPI application entry point.

Loads ML models at startup and mounts all API routers.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import experiments, info, predict
from app.core.config import ALLOWED_ORIGINS
from app.core.model_loader import load_models


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load models once at application startup."""
    load_models()
    yield


app = FastAPI(
    title="Facemask Detector API",
    description="Real-time face mask detection using a custom CNN — reproducing the paper.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(predict.router)
app.include_router(experiments.router)
app.include_router(info.router)
