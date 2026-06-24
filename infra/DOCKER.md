# Docker Setup Guide

## Quick Start

```bash
# Build and start all services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Neon City API | 8000 | Simulation REST API |
| Factory API | 8080 | Orchestrator API |
| Dashboard | 3000 | Analytics UI |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache |

## Build

```bash
# Build all images
docker-compose build

# Build single service
docker-compose build neon-city-api
```

## Environment

Create `.env` from `.env.example`:

```bash
cp .env.example .env
```

## Volumes

Data is persisted in Docker volumes:

| Volume | Purpose |
|--------|---------|
| postgres-data | Database files |
| redis-data | Cache data |
| neon-city-data | Simulation artifacts |

## Troubleshooting

```bash
# Reset everything
docker-compose down -v
docker-compose up -d --build

# Shell into container
docker-compose exec neon-city-api bash

# Database shell
docker-compose exec db psql -U neon -d neoncity

# Redis CLI
docker-compose exec redis redis-cli
```

## Production

For production deployment:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Cleanup

```bash
# Stop services
docker-compose down

# Remove volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all
```
