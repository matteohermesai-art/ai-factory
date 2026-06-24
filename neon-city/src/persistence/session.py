"""Database session management for the Neon City Simulation Engine."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .models import Base


def get_engine(database_url: str) -> AsyncEngine:
    """Create and return an async SQLAlchemy engine.

    Args:
        database_url: The database connection URL (e.g., "sqlite+aiosqlite:///neon_city.db").

    Returns:
        An async SQLAlchemy engine instance.
    """
    engine = create_async_engine(database_url, echo=False)
    return engine


def get_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create and return an async session factory.

    Args:
        engine: The async SQLAlchemy engine.

    Returns:
        An async_sessionmaker configured for the given engine.
    """
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    return session_factory


async def init_db(engine: AsyncEngine) -> None:
    """Create all tables defined in the models.

    Args:
        engine: The async SQLAlchemy engine.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def get_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """Async context manager that yields a session and handles commit/rollback.

    Commits on success, rolls back on exception, and always closes the session.

    Args:
        session_factory: The async session factory.

    Yields:
        An active AsyncSession.
    """
    session = session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
