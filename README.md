# 🏭 AI Factory — Autonomous AI Agent Factory

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Docker](https://img.shields.io/badge/docker-ready-2496ED)]()

> **Multi-agent AI factory for building, deploying, and orchestrating autonomous AI agents.**

AI Factory is a cyberpunk-themed agent simulation framework. It orchestrates autonomous agents (citizens, hackers, police, corporations) in a virtual city with economy, events, skill evolution, and persistent state — all controllable via REST API.

---

## 🏗️ Architecture Overview

```
ai-factory/
├── 📄 README.md                    # You are here
├── 📄 CHANGELOG.md                 # Version history
├── 📄 LICENSE                      # MIT License
├── 📄 .env.example                 # Environment template
├── 📄 pyproject.toml               # Project config & tools
├── 📄 Makefile                     # Build targets
├── 📄 Dockerfile                   # Multi-stage container build
├── 📄 docker-compose.yml           # Full stack orchestration
│
├── 📁 neon-city/                   # 🏙️ City simulation engine
│   └── [see neon-city/*]
│
├── 📁 agents/                      # 🤖 Agent definitions & workers
│   ├── SCITHERON.md                # Expert Python agent config
│   ├── PAVARD.md                   # Full-stack Swift agent config
│   └── ...
│
├── 📁 factory-api/                 # 🌐 Factory REST API
├── 📁 infra/                       # 🔧 Infrastructure
├── 📁 skills/                      # 🎯 Hermes skill definitions
├── 📁 workspace/                     # 🧠 Agent workspaces
└── 📁 workspaces/                  # 📂 Agent state persistence
```

---

## ✨ Core Features

### 🏙️ Neon City — City Simulation

- **200+ autonomous agents** on 80x80 grid
- Full economy (credits, data, black market, corp shares)
- Skill trees (4 tiers) and agent evolution
- Legal system: arrests, bounties, probation
- Environmental events: blackouts, ransomware, riots
- Mission system with dynamic quests

### 🤖 Agent Workers

- **SCITHERON**: Expert Python developer agent
- **PAVARD**: Full-stack Swift developer agent
- **Hermes**: AI assistant with custom skills
- Each agent gets its own workspace, skills, and runtime config

### 🎯 Hermes Skill System

- Procedural memory via `~/.hermes/skills/`
- Markdown-based SKILL.md format
- Cron job scheduling
- Computer use, web search, terminal tools

### 🐳 Docker Infrastructure

- Multi-stage builds for minimal images
- Neon City API + PostgreSQL + Redis
- Health checks per service
- Log rotation e monitoring

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- `gh` CLI (for GitHub operations)

### Installation

```bash
# Clone
git clone https://github.com/matteohermesai-art/ai-factory.git
cd ai-factory

# Setup environment
cp .env.example .env

# Start everything
make up

# Or without Docker
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Docker

```bash
docker-compose up -d
# → API: http://localhost:8000/docs
```

### Available Commands

| Command | Description |
|---------|-------------|
| `make up` | Start all services |
| `make down` | Stop services |
| `make init-db` | Initialize database |
| `make test` | Run test suite |
| `make lint` | Lint code |
| `make clean` | Clean artifacts |

---

## 📊 Neon City Performance

| Metric | Value |
|--------|-------|
| Tick rate | ~126 tick/sec |
| Max agents | 200+ |
| API latency | <10ms p95 |
| Memory | ~500MB |

---

## 🔌 REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/simulation/status` | Current state |
| `POST` | `/api/simulation/start` | Start simulation |
| `POST` | `/api/simulation/stop` | Stop simulation |
| `GET` | `/api/agents/` | List agents |
| `GET` | `/api/economy/market` | Market state |
| `POST` | `/api/replay/start` | Record replay |

---

## 📁 Project Structure

```
ai-factory/
├── neon-city/          # City simulation engine
├── agents/             # Agent worker configs
├── factory-api/        # FastAPI REST API
├── skills/             # Hermes skills
├── workspace/          # Agent workspaces (memory)
├── workspaces/         # Agent state persistence
├── infra/              # Infrastructure (DB, Redis)
└── scripts/            # Utility scripts
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing`
3. Commit: `git commit -m '✨ Add amazing feature'`
4. Push: `git push origin feature/amazing`
5. Open Pull Request

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

<p align="center">
  <b>🤖 AI Factory — Building the future, one agent at a time.</b>
</p>
