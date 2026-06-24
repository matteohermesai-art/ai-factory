#!/usr/bin/env python3
"""Check if database is reachable. Exit 0 if OK, 1 if not."""
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


async def check():
    url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///ai-factory.db")
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(check())
        sys.exit(0)
    except Exception:
        sys.exit(1)
