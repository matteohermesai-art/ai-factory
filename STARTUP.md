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

# 3. Start
make up

# 4. Initialize database
make init-db

# 5. Verify
curl http://localhost:8000/health
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
│   ├── persistence/       # State storage
│   │   ├── models.py      # Database models
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
├── tests/                 # Test suite
├── scripts/               # Utility scripts
├── infra/                 # Infrastructure docs
│   └── DOCKER.md          # Docker guide
│
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

## Hermes Skills

After installing Hermes, load these skills:

```bash
hermes skills install hermes-agent
hermes skills install github
hermes skills install software-development
hermes skills install terminal
hermes skills install research
```

Or paste the prompt from `skills/HERMES_SETUP.md`.

## Common Commands

```bash
# Run the API
python -m src.main

# Run tests
make test

# Lint code
make lint

# Run lint and tests
make lint && make test

# Delegate a task to SCITHERON
curl -X POST http://localhost:8000/api/workers/delegate \
  -H "Content-Type: application/json" \
  -d '{"worker":"scitheron","goal":"Implement auth endpoint","context":"FastAPI + JWT"}'

# List workers
curl http://localhost:8000/api/workers/
```

## Environment Variables

See `.env.example` for all options. Key ones:

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `sqlite+aiosqlite:///ai-factory.db` | Database |
| `REDIS_URL` | `redis://redis:6379` | Cache/broker |
| `MAX_WORKERS` | `5` | Concurrent workers |
| `LOG_LEVEL` | `info` | Logging level |
| `ENABLE_CRON` | `true` | Enable scheduler |

## Troubleshooting

**Port conflicts**: Change ports in `.env` or `docker-compose.yml`

**Database errors**: `make init-db`

**Redis connection**: Ensure Redis container is healthy

**Worker timeout**: Increase timeout in config

## Next Steps

1. Read `agents/AGENT_CONFIGS.md` for worker configuration details
2. Read `skills/SKILL_DEFINITIONS.md` for skill specifications
3. Read `infra/DOCKER.md` for infrastructure guide
4. Check `src/api/routes/` for available API endpoints

---

The factory is online. Your workers are ready.
