# 🏙️ Neon City Simulation Engine

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Code style](https://img.shields.io/badge/code%20style-black-important)]()

> A high-performance, cyberpunk-themed multi-agent city simulation engine built with Python, AsyncIO, and FastAPI.

![Neon City Banner](https://img.shields.io/badge/🌃%20CYBERPUNK-SIMULATION%20ENGINE-ff00ff?style=for-the-badge)

## ✨ Highlights

- **200+ autonomous agents** with skill trees, factions, and reputation
- **Full virtual economy** with markets, black markets, and multi-currency
- **Real-time event system** — cyber attacks, riots, blackouts, ransomware
- **Legal system** — arrests, bountes, probation, criminal records
- **Mission system** — dynamic quest generation with rewards
- **REST API** — full control and monitoring via FastAPI
- **Replay system** — record and replay any simulation run
- **Structured logging** — JSON logs with analytics dashboard

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        REST API (FastAPI)                    │
├─────────────────────────────────────────────────────────────┤
│              Simulation Engine (AsyncIO + Tick Loop)         │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│  Agents  │ Economy  │  Events  │ Logging  │  Persistence   │
│ (4 types)│ (market) │ (bus)    │(structlog)│  (SQLAlchemy)  │
├──────────┴──────────┴──────────┴──────────┴────────────────┤
│                    Grid World (configurable)                 │
└─────────────────────────────────────────────────────────────┘
```

### Agent Types

| Type | Behavior | Skill Tree |
|------|----------|------------|
| 👤 **Citizen** | Works, buys/sells, propagandizes | Worker → Freelancer → Entrepreneur → Influencer |
| 💻 **Hacker** | Hacks, black market, steals data | Script Kiddie → Net Runner → Elite → Ghost |
| 🚔 **Police** | Patrols, arrests, raids | Patrol → Detective → SWAT → Commissioner |
| 🏢 **Corporation** | Market manipulation, takeovers | Startup → MegaCorp → Syndicate → AI Overseer |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 16 (or use Docker)
- pip or uv

### Installation

```bash
# Clone the repository
git clone https://github.com/matteohermesai-art/neon-city-simulation.git
cd neon-city

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Docker (Recommended)

```bash
# Start everything
make up

# Initialize database
make init-db

# Seed initial data
make seed
```

### Local Development

```bash
# Copy environment config
cp .env.example .env

# Run the API
make run
# → http://localhost:8000/docs
```

## 📊 Simulation Features

### Economy

| Feature | Description |
|---------|-------------|
| **Credits (₡)** | Primary currency |
| **Data (💾)** | Produced by workers, traded on market |
| **Black Market (◈)** | Illicit goods: neurotox, hack toolkits, fake IDs |
| **Corp Shares (📈)** | Ownership tokens for corporations |

### Events

| Event | Effect | Duration |
|-------|--------|----------|
| 🌑 **Blackout** | Energy prices x3 | 50 ticks |
| 🦠 **Ransomware** | Hacker success rate x2 | 30 ticks |
| 📋 **Corp Audit** | Corporations frozen | 40 ticks |
| 🔥 **Street Riot** | Crime rate boosted | 60 ticks |
| ⚡ **Network Glitch** | Trading paused | 20 ticks |

### Metrics & Analytics

- **Gini Coefficient** — wealth inequality tracking
- **Faction Reputation** — inter-faction relationship scores
- **Agent Evolution** — skill progression tracking
- **Market Health** — order book depth, trade volume

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/simulation/status` | Current simulation state |
| `POST` | `/api/simulation/start` | Start simulation |
| `POST` | `/api/simulation/stop` | Stop simulation |
| `GET` | `/api/agents/` | List all agents |
| `GET` | `/api/agents/{id}` | Agent details |
| `GET` | `/api/economy/market` | Market state |
| `GET` | `/api/economy/stats` | Economy statistics |
| `GET` | `/api/events/` | Recent events |
| `POST` | `/api/replay/start` | Start replay recording |
| `GET` | `/api/replay/{id}` | Get replay data |

## 🧪 Testing

```bash
# Run all tests
make test

# With coverage
make test-cov

# Specific test file
pytest tests/test_engine/test_tick.py -v
```

## 📁 Project Structure

```
neon-city/
├── 📄 README.md              # You are here
├── 📄 CHANGELOG.md           # Version history
├── 📄 requirements.txt        # Python dependencies
├── 📄 pyproject.toml          # Project config & tools
├── 📄 Makefile                # Build targets
├── 📄 Dockerfile              # Container build
├── 📄 docker-compose.yml      # Full stack orchestration
├── 📄 .env.example            # Environment template
│
├── 📁 src/
│   ├── 📄 main.py             # Application entry point
│   ├── 📄 config.py           # Configuration management
│   │
│   ├── 📁 engine/             # Simulation core
│   │   ├── 📄 grid.py         # Grid world
│   │   ├── 📄 world.py        # World state
│   │   ├── 📄 tick.py         # Tick engine
│   │   └── 📄 replay.py       # Replay system
│   │
│   ├── 📁 agents/             # Agent implementations
│   │   ├── 📄 base.py         # Base agent class
│   │   ├── 📄 citizen.py      # Citizen agent
│   │   ├── 📄 hacker.py       # Hacker agent
│   │   ├── 📄 police.py       # Police agent
│   │   └── 📄 corporation.py  # Corporation agent
│   │
│   ├── 📁 economy/            # Economy system
│   │   ├── 📄 market.py       # Order book & matching
│   │   ├── 📄 currency.py     # Currency definitions
│   │   └── 📄 transactions.py # Transaction log
│   │
│   ├── 📁 events/             # Event system
│   │   ├── 📄 bus.py          # Event bus (pub/sub)
│   │   ├── 📄 types.py        # Event type definitions
│   │   └── 📄 generators.py   # Event generation
│   │
│   ├── 📁 api/                # REST API
│   │   ├── 📄 app.py          # FastAPI app
│   │   ├── 📄 schemas.py      # Pydantic schemas
│   │   └── 📁 routes/         # API routes
│   │
│   ├── 📁 persistence/        # Data layer
│   │   ├── 📄 models.py       # SQLAlchemy models
│   │   ├── 📄 repository.py   # Data access
│   │   └── 📄 session.py      # DB session
│   │
│   ├── 📁 logging/            # Logging
│   │   ├── 📄 structured.py   # structlog setup
│   │   └── 📄 analytics.py    # Analytics pipeline
│   │
│   └── 📁 worker/             # Background tasks
│       └── 📄 scheduler.py    # Tick scheduler
│
├── 📁 tests/                  # Test suite
│   ├── 📁 test_engine/
│   ├── 📁 test_agents/
│   ├── 📁 test_economy/
│   ├── 📁 test_events/
│   ├── 📁 test_api/
│   └── 📁 test_persistence/
│
├── 📁 scripts/                # Utility scripts
│   ├── 📄 seed.py             # Database seeding
│   └── 📄 replay_cli.py       # Replay CLI
│
└── 📁 alembic/                # Database migrations
```

## 🛠️ Configuration

All configuration via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://neon:neon@db:5432/neoncity` | PostgreSQL connection |
| `GRID_WIDTH` | `100` | City grid width |
| `GRID_HEIGHT` | `100` | City grid height |
| `TICK_INTERVAL_SECONDS` | `1.0` | Time between ticks |
| `LOG_LEVEL` | `info` | Logging level |
| `SEED` | `42` | Random seed |
| `TOTAL_TICKS` | `10000` | Max simulation ticks |
| `ENABLE_METRICS` | `true` | Enable metrics collection |

## 📈 Performance

| Metric | Value |
|--------|-------|
| **Tick rate** | ~126 tick/sec |
| **Agents supported** | 200+ |
| **Memory** | ~500MB for 200 agents |
| **API latency** | <10ms p95 |

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Inspired by cyberpunk fiction: *Neuromancer*, *Snow Crash*, *Blade Runner*
- Built with ❤️ by Matteo erPigro

---

<p align="center">
  <b>🌃 Welcome to Neon City. The future is now. 🌃</b>
</p>
