# AI Factory

A multi-agent simulation framework for building, deploying, and orchestrating autonomous AI workers.

## Highlights

Orchestrate 200+ autonomous agents in a cyberpunk city simulation with full economy, skill trees, events, legal system, and REST API — all containerized with Docker.

## Architecture

```
                       REST API (FastAPI)
                            |
            +---------------+---------------+
            |                               |
    Neon City API                   Factory API
    (Simulation Engine)             (Orchestrator)
            |                               |
    +-------+-------+               +-------+-------+
    |       |       |               |       |       |
  Grid   Events  Economy        Workers  Tasks  Cron
  World   Bus     Market          |              |
    |       |       |           SCITHERON      Scheduler
  Agents  Logging  Market        PAVARD
  (200+)  structlog HERMES
```

### Agent Types

| Agent | Role | Skill Tree |
|-------|------|------------|
| Citizen | Works, trades, influencers | Worker -> Freelancer -> Entrepreneur -> Influencer |
| Hacker | Hacks, black market | Script Kiddie -> Net Runner -> Elite -> Ghost |
| Police | Patrols, arrests | Patrol -> Detective -> SWAT -> Commissioner |
| Corporation | Market manipulation | Startup -> MegaCorp -> Syndicate -> AI Overseer |

### Core Modules

| Module | Description |
|--------|-------------|
| `engine/` | Simulation core: grid world, tick engine, replay |
| `agents/` | Agent implementations with behaviors |
| `economy/` | Market, currency, transactions, black market |
| `events/` | Event bus, generators, environmental events |
| `api/` | FastAPI REST endpoints |
| `persistence/` | SQLAlchemy models, repositories |
| `logging/` | Structured logging with structlog |
| `worker/` | Background scheduler |

## Quick Start

```bash
# Clone
git clone https://github.com/matteohermesai-art/ai-factory.git
cd ai-factory

# Start with Docker
make up

# Or local
source venv/bin/activate
pip install -r neon-city/requirements.txt
cd neon-city && python -m src.main
```

## Available Commands

| Command | Description |
|---------|-------------|
| `make up` | Start all Docker services |
| `make down` | Stop all services |
| `make init-db` | Initialize database and run migrations |
| `make test` | Run full test suite |
| `make lint` | Lint and format code |
| `make simulate` | Run simulation locally |
| `make simulate-ultra` | Run 100k tick simulation |
| `make logs` | View Docker logs |
| `make status` | Check service health |
| `make clean` | Remove build artifacts |

## Configuration

All configuration via environment variables. Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

See `.env.example` for all available options.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/simulation/start` | Start simulation |
| `POST` | `/api/simulation/stop` | Stop simulation |
| `GET` | `/api/simulation/status` | Current state |
| `GET` | `/api/agents/` | List all agents |
| `GET` | `/api/agents/{id}` | Agent details |
| `GET` | `/api/economy/market` | Market state |
| `GET` | `/api/economy/stats` | Economy statistics |
| `GET` | `/api/events/` | Recent events |
| `POST` | `/api/replay/start` | Start replay recording |
| `GET` | `/api/replay/{id}` | Get replay data |

Interactive API docs at `http://localhost:8000/docs`.

## Tech Stack

- **Python 3.11+** with AsyncIO
- **FastAPI** REST framework
- **SQLAlchemy 2.0** + asyncpg ORM
- **PostgreSQL 16** database
- **Redis** cache and message broker
- **Alembic** database migrations
- **structlog** structured logging
- **Docker** containerization
- **pytest** testing framework

## Project Structure

```
ai-factory/
├── neon-city/           # Simulation engine (78 Python files)
│   ├── src/             # Source code
│   │   ├── engine/      # Grid, world, tick, replay
│   │   ├── agents/      # Citizen, hacker, police, corporation
│   │   ├── economy/     # Market, currency, transactions
│   │   ├── events/      # Event bus, generators
│   │   ├── api/         # FastAPI app and routes
│   │   ├── persistence/ # Database models
│   │   ├── logging/     # Structured logging
│   │   └── worker/      # Background scheduler
│   ├── tests/           # Test suite (pytest)
│   ├── alembic/         # Database migrations
│   └── scripts/         # Utility scripts
├── agents/              # Agent configuration files
│   ├── SCITHERON.md     # Python developer
│   ├── PAVARD.md        # Swift developer
│   ├── HERMES.md        # AI orchestrator
│   └── AGENT_CONFIGS.md # All agent docs
├── skills/              # Hermes skills
├── infra/               # Infrastructure docs
├── docker-compose.yml   # Full stack
├── Dockerfile           # Multi-stage build
├── Makefile             # Build targets
├── pyproject.toml       # Project configuration
├── requirements.txt     # Dependencies
├── .env.example         # Environment template
├── README.md            # This file
├── CHANGELOG.md         # Version history
├── CONTRIBUTING.md      # Contribution guidelines
└── LICENSE              # MIT License
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT License — see [LICENSE](LICENSE) for details.

## Acknowledgments

Inspired by cyberpunk fiction and multi-agent simulation research.
