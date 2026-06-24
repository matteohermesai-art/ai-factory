#!/bin/bash
# Docker entrypoint for AI Factory API
# Auto-initializes database tables on first start

set -e

echo "AI Factory API starting..."

# Wait for database to be ready
echo "Waiting for database..."
until python scripts/check-db.py 2>/dev/null; do
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
