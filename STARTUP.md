# 🏭 AI Factory — Startup Guide

Welcome to AI Factory. This guide gets you up and running.

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
curl http://localhost:8080/health
```

## Project Layout

```
ai-factory/
├── neon-city/           # 🏙️ Simulation engine
│   ├── src/             # Source code
│   ├── tests/           # Test suite
│   ├── scripts/         # Utility scripts
│   ├── alembic/         # DB migrations
│   └── Dockerfile
│
├── agents/              # 🤖 Agent configs
│   ├── AGENT_CONFIGS.md # All agent docs
│   ├── SCITHERON.md     # Python expert
│   └── PAVARD.md        # Swift expert
│
├── factory-api/         # 🌐 Orchestrator API
├── skills/              # 🎯 Hermes skills
│   └── HERMES_SETUP.md  # Post-install prompt
│
├── infra/               # 🔧 Infrastructure
│   └── DOCKER.md        # Docker guide
│
├── workspace/           # 🧠 Agent workspaces
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── pyproject.toml
├── README.md
└── CHANGELOG.md
```

## Agents

| Agent | Role | Workspace |
|-------|------|-----------|
| **Hermes** | AI Assistant & Orchestrator | `workspace/hermes/` |
| **SCITHERON** | Python Simulation Engineer | `workspace/scitheron/` |
| **PAVARD** | Full-Stack Swift Developer | `workspace/pavard/` |

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
# Run simulation
make simulate

# Run 100k tick simulation
make simulate-ultra

# View logs
make logs

# Run tests
make test

# Lint code
make lint

# Clean build artifacts
make clean
```

## Environment Variables

See `.env.example` for all options. Key ones:

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `postgresql+asyncpg://neon:neon@db:5432/neoncity` | Database |
| `GRID_WIDTH` | `80` | City grid width |
| `GRID_HEIGHT` | `80` | City grid height |
| `TOTAL_TICKS` | `10000` | Simulation length |
| `LOG_LEVEL` | `info` | Logging level |

## Troubleshooting

**Port conflicts**: Change ports in `docker-compose.yml`

**Database errors**: `make init-db`

**Memory issues**: Reduce `GRID_WIDTH`/`GRID_HEIGHT` in `.env`

**Permission denied**: Ensure Docker user has access to `data/` directory

## Next Steps

1. Read `neon-city/README.md` for simulation details
2. Read `agents/AGENT_CONFIGS.md` for agent configuration
3. Read `infra/DOCKER.md` for infrastructure guide
4. Check `skills/HERMES_SETUP.md` for Hermes setup

---

🌃 **Welcome to the future. The factory is online.**
