# AI Factory - Startup Guide

Welcome to AI Factory. This guide gets you up and running with the multi-agent worker framework.

## Prerequisites

- Python 3.11+
- Docker & Docker Compose v2
- 4GB+ RAM available

## First Run

```bash
# 1. Clone
git clone https://github.com/matteohermesai-art/ai-factory.git
cd ai-factory

# 2. Environment
cp .env.example .env
# Edit .env with your settings

# 3. Start (auto-initializes database tables)
make up

# 4. Verify
curl http://localhost:8000/health
```

**Database tables are created automatically** on first startup via the Docker entrypoint. No manual migration needed.

## Database Initialization

The Docker entrypoint (`docker-entrypoint.sh`) runs automatically:

1. Waits for PostgreSQL to be healthy
2. Runs `scripts/init-db.py` which creates all tables from SQLAlchemy models
3. Idempotent — safe to run multiple times, won't duplicate tables

### Manual DB init (without Docker)

```bash
python scripts/init-db.py
```

### Reset database

```bash
make down        # Stop and remove containers + volumes
make up          # Recreate with fresh database
```

## Project Layout

```
ai-factory/
├── src/                   # Source code
│   ├── api/               # FastAPI REST API
│   │   ├── routes/        # API endpoints
│   │   ├── schemas.py     # Pydantic models
│   │   └── app.py         # FastAPI app
│   ├── worker/            # Task scheduler
│   │   └── scheduler.py    # Cron & delegation
│   ├── persistence/       # Database models & storage
│   │   ├── models.py      # SQLAlchemy models
│   │   ├── repository.py  # Data access
│   │   └── session.py     # DB session
│   ├── logging/           # Structured logging
│   │   ├── structured.py
│   │   └── analytics.py
│   ├── config.py          # Configuration
│   └── main.py            # Entry point
│
├── agents/                # Worker configurations
│   ├── AGENT_CONFIGS.md   # All worker docs
│   ├── SCITHERON.md       # Python developer
│   ├── PAVARD.md          # Swift developer
│   └── HERMES.md          # AI orchestrator
│
├── skills/                # Hermes skills
│   ├── HERMES_SETUP.md    # Post-install prompt
│   └── SKILL_DEFINITIONS.md
│
├── scripts/
│   ├── init-db.py         # Database table creation
│   └── seed.py            # Seed initial workers
│
├── tests/                 # Test suite
├── infra/                 # Infrastructure docs
│   └── DOCKER.md          # Docker guide
│
├── docker-entrypoint.sh   # Auto-DB init on container start
├── docker-compose.yml     # Full stack
├── Dockerfile             # Multi-stage build
├── Makefile               # Build targets
├── pyproject.toml         # Project config
├── .env.example           # Env template
├── README.md
└── CHANGELOG.md
```

## Workers

| Worker | Role | Workspace |
|--------|------|-----------|
| **Hermes** | AI Assistant & Orchestrator | `workspace/hermes/` |
| **SCITHERON** | Python Developer | `workspace/scitheron/` |
| **PAVARD** | Swift Developer | `workspace/pavard/` |

## Database Tables

| Table | Purpose |
|-------|---------|
| `workers` | Worker configuration and state |
| `tasks` | Task assignments with status tracking |
| `cron_jobs` | Scheduled recurring jobs |
| `workspace_files` | Tracked files in agent workspaces |
| `memory` | Persistent memory entries for workers |

## Environment Variables

See `.env.example` for all options. Key ones:

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `postgresql+asyncpg://neon:neon@db:5432/neoncity` | Database |
| `REDIS_URL` | `redis://redis:6379` | Cache/broker |
| `MAX_WORKERS` | `5` | Concurrent workers |
| `LOG_LEVEL` | `info` | Logging level |
| `ENABLE_CRON` | `true` | Enable scheduler |

## Troubleshooting

**Port conflicts**: Change ports in `.env` or `docker-compose.yml`

**Database errors**: `make down && make up` (resets DB)

**Redis connection**: Ensure Redis container is healthy

**Worker timeout**: Increase `DELEGATION_TIMEOUT` in `.env`

## Next Steps

1. Read `agents/AGENT_CONFIGS.md` for worker configuration details
2. Read `skills/SKILL_DEFINITIONS.md` for skill specifications
3. Read `infra/DOCKER.md` for infrastructure guide
4. Check `src/api/routes/` for available API endpoints

---

The factory is online. Your workers are ready.
