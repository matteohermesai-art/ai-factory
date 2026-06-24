"""FastAPI application factory for the Neon City Simulation Engine."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import simulation, agents, economy, replay
from src.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Handles startup (DB initialization) and shutdown (cleanup).
    """
    # Startup: initialize DB connection
    try:
        from src.persistence import get_engine, get_session_factory, init_db

        engine = get_engine(settings.DATABASE_URL)
        session_factory = get_session_factory(engine)
        await init_db(engine)
        app.state._db_engine = engine
        app.state._session_factory = session_factory
    except Exception:
        # DB may not be available in all environments (e.g. tests)
        app.state._db_engine = None
        app.state._session_factory = None

    yield

    # Shutdown: close DB connection
    engine = getattr(app.state, "_db_engine", None)
    if engine is not None:
        await engine.dispose()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Neon City Simulation Engine",
        description="A cyberpunk-themed city simulation engine with agents, economy, and real-time analytics",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers (prefixes are already set on each router)
    app.include_router(simulation.router)
    app.include_router(agents.router)
    app.include_router(economy.router)
    app.include_router(replay.router)

    @app.get("/health")
    async def health_check() -> dict:
        """Health check endpoint."""
        return {"status": "ok", "service": "neon-city-simulation-engine"}

    return app
