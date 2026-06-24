# AI Factory

A framework for building, deploying, and orchestrating autonomous AI agent workers.

## Highlights

- **Multi-agent orchestration** — coordinate specialized AI workers under a central orchestrator
- **Skill system** — procedural memory via markdown-based SKILL.md definitions
- **Worker delegation** — spawn sub-agents for parallel task execution
- **Cron scheduling** — background jobs with recurring schedules
- **REST API** — full control and monitoring via FastAPI
- **Docker infrastructure** — production-ready containerized deployment
- **Structured logging** — JSON logs with analytics pipeline

## Architecture

```
                       REST API (FastAPI)
                            |
                  +---------+---------+
                  |                   |
          Task Router          Cron Scheduler
                  |                   |
          +-------+-------+   +------+------+
          |       |       |   |             |
       HERMES  SCITHERON  PAVARD   Background Jobs
       (Orch)  (Python)  (Swift)   (Scheduled)
          |       |       |
          +-------+-------+
                  |
          Workspaces (persistent state)
                  |
          +-------+-------+
          |       |       |
        Files   Memory   Skills
```

### Workers

| Worker | Role | Specialty |
|--------|------|-----------|
| **HERMES** | Orchestrator & AI Assistant | Coordination, delegation, scheduling, research |
| **SCITHERON** | Python Developer | Backend, async Python, FastAPI, testing, code review |
| **PAVARD** | Swift Developer | iOS/macOS apps, SwiftUI, Vapor, system programming |

### Core Modules

| Module | Description |
|--------|-------------|
| `api/` | FastAPI REST endpoints for task management and monitoring |
| `worker/` | Background scheduler and task queue |
| `skills/` | Hermes skill definitions (procedural memory) |
| `agents/` | Worker configuration files and runtime specs |
| `persistence/` | State storage for workspaces and agent memory |
| `logging/` | Structured logging with structlog |

## Quick Start

```bash
# Clone
git clone https://github.com/matteohermesai-art/ai-factory.git
cd ai-factory

# Start with Docker
make up

# Or local
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

## Available Commands

| Command | Description |
|---------|-------------|
| `make up` | Start all Docker services |
| `make down` | Stop all services |
| `make test` | Run full test suite |
| `make lint` | Lint and format code |
| `make logs` | View Docker logs |
| `make status` | Check service health |
| `make clean` | Remove build artifacts |
| `make shell` | Open shell in container |

## Configuration

All configuration via environment variables. Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///ai-factory.db` | Database connection |
| `REDIS_URL` | `redis://redis:6379` | Redis cache URL |
| `LOG_LEVEL` | `info` | Logging level |
| `API_PORT` | `8000` | API server port |
| `ENABLE_CRON` | `true` | Enable cron scheduler |
| `MAX_WORKERS` | `5` | Max concurrent workers |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/api/workers/` | List all workers |
| `POST` | `/api/workers/delegate` | Delegate task to a worker |
| `GET` | `/api/workers/{id}/status` | Worker status |
| `GET` | `/api/tasks/` | List all tasks |
| `POST` | `/api/tasks/` | Create new task |
| `GET` | `/api/tasks/{id}` | Task details |
| `GET` | `/api/cron/` | List cron jobs |
| `POST` | `/api/cron/` | Create cron job |
| `DELETE` | `/api/cron/{id}` | Delete cron job |
| `GET` | `/api/skills/` | List available skills |
| `GET` | `/api/workspace/{worker}` | List worker workspace files |

Interactive API docs at `http://localhost:8000/docs`.

## Tech Stack

- **Python 3.11+** with AsyncIO
- **FastAPI** REST framework
- **SQLAlchemy 2.0** + aiosqlite (dev) / asyncpg (prod)
- **Redis** cache and message broker
- **Alembic** database migrations
- **structlog** structured logging
- **Docker** containerization
- **pytest** testing framework

## Project Structure

```
ai-factory/
├── src/                   # Source code
│   ├── api/               # FastAPI app and routes
│   │   ├── routes/
│   │   ├── schemas.py
│   │   └── app.py
│   ├── worker/            # Task scheduler and queue
│   │   └── scheduler.py
│   ├── persistence/       # State storage
│   │   ├── models.py
│   │   ├── repository.py
│   │   └── session.py
│   ├── logging/           # Structured logging
│   │   ├── structured.py
│   │   └── analytics.py
│   ├── config.py          # Configuration management
│   └── main.py            # Application entry point
├── agents/                # Worker configurations
│   ├── SCITHERON.md       # Python developer worker
│   ├── PAVARD.md          # Swift developer worker
│   ├── HERMES.md          # AI orchestrator worker
│   └── AGENT_CONFIGS.md   # All worker docs
├── skills/                # Hermes skill definitions
│   ├── HERMES_SETUP.md    # Post-install setup prompt
│   └── SKILL_DEFINITIONS.md
├── tests/                 # Test suite (pytest)
├── scripts/               # Utility scripts
├── infra/                 # Infrastructure docs
│   └── DOCKER.md
├── docker-compose.yml     # Full stack
├── Dockerfile             # Multi-stage build
├── Makefile               # Build targets
├── pyproject.toml         # Project configuration
├── .env.example           # Environment template
├── README.md              # This file
├── CHANGELOG.md           # Version history
├── CONTRIBUTING.md        # Contribution guidelines
└── LICENSE                # MIT License
```

## Workers

### HERMES — Orchestrator

Coordinates other workers, manages schedules, and handles task delegation. Has full tool access including `delegate_task`, `cronjob`, and `computer_use`.

### SCITHERON — Python Developer

Specializes in Python development: backend APIs, async code, testing, code reviews, and documentation. Uses `terminal`, `file`, `browser`, and `web_search` tools.

### PAVARD — Swift Developer

Specializes in Swift development: iOS/macOS apps, SwiftUI, Vapor server-side, and system programming. Uses `terminal`, `file`, and `browser` tools.

## Skills

Skills are markdown-based procedural memory. Each skill is a `SKILL.md` file that Hermes loads on-demand.

| Skill | Purpose |
|-------|---------|
| `hermes-agent` | Self-management and configuration |
| `github` | GitHub operations (issues, PRs, repos) |
| `software-development` | Code quality, testing, review |
| `research` | Web search and analysis |
| `python-debug` | Python debugging with pdb |
| `systematic-debugging` | 4-phase root cause analysis |
| `test-driven-development` | TDD workflow |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT License — see [LICENSE](LICENSE) for details.
