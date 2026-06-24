#!/bin/bash
# Docker entrypoint for AI Factory API
# Auto-initializes database tables on first start

set -e

echo "AI Factory API starting..."

# Wait for database to be ready
echo "Waiting for database..."
until python -c "
import asyncio, os, sys
sys.path.insert(0, '/app/src')
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def check():
    url = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///ai-factory.db')
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.execute(text('SELECT 1'))
    await engine.dispose()

asyncio.run(check())
" 2>/dev/null; do
    echo "Database not ready, retrying in 2s..."
    sleep 2
done

echo "Database is ready."

# Initialize tables
echo "Initializing database tables..."
python scripts/init-db.py

# Start the API
echo "Starting API server..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers ${API_WORKERS:-4}
