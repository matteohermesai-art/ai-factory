#!/usr/bin/env python3
"""
Database initialization script.
Creates all tables if they don't exist.
Safe to run multiple times (idempotent).

Priority:
1. Run Alembic migrations (if alembic.ini exists)
2. Fallback: create_all from models
"""
import asyncio
import importlib
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


async def run_alembic():
    """Try to run Alembic migrations."""
    try:
        alembic_config = importlib.import_module("alembic.config")
        alembic_command = importlib.import_module("alembic")
        cfg = alembic_config.Config("alembic.ini")
        alembic_command.command.upgrade(cfg, "head")
        print("  Alembic migrations applied successfully")
        return True
    except Exception as e:
        print(f"  Alembic not available ({e})")
        return False


async def init_db():
    """Initialize database tables."""
    database_url = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///ai-factory.db"
    )

    # Try Alembic first
    alembic_ok = await run_alembic()

    if not alembic_ok:
        # Fallback: create_all from models
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        from persistence.models import Base

        echo = os.getenv("DB_ECHO", "false").lower() == "true"
        engine = create_async_engine(database_url, echo=echo)

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        await engine.dispose()
        print("  Tables created via create_all")

    print("Database initialized successfully")


if __name__ == "__main__":
    asyncio.run(init_db())
