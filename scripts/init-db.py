#!/usr/bin/env python3
"""
Database initialization script.
Creates all tables and indexes on first run.
Safe to run multiple times (idempotent).
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

# Import all models so SQLAlchemy knows about them
from persistence.models import Base


async def init_db(database_url: str = None):
    """Create all tables if they don't exist."""
    database_url = database_url or os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///ai-factory.db"
    )

    engine = create_async_engine(database_url, echo=True)

    async with engine.begin() as conn:
        # Create all tables from models
        await conn.run_sync(Base.metadata.create_all)

        # Verify tables exist
        if "postgresql" in database_url:
            result = await conn.execute(text(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
            ))
            tables = [row[0] for row in result]
        else:
            result = await conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ))
            tables = [row[0] for row in result]

    await engine.dispose()

    print(f"✅ Database initialized: {len(tables)} tables")
    for t in sorted(tables):
        print(f"   - {t}")


if __name__ == "__main__":
    asyncio.run(init_db())
