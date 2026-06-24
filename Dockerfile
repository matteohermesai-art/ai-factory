# Dockerfile — Neon City Simulation
FROM python:3.11-slim AS base

# Build dependencies
FROM base AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY neon-city/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Production image
FROM base AS production
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

WORKDIR /app
COPY neon-city/src/ ./src/
COPY neon-city/alembic/ ./alembic/
COPY alembic.ini .
COPY neon-city/scripts/ ./scripts/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
