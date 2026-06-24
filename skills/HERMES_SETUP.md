# Hermes AI Assistant — Skill Configuration

This file defines the initial setup prompt to give to Hermes after installation.

## Installation Prompt

Copy and paste this prompt immediately after installing Hermes to set up Neon City skills:

---

```
Welcome to Hermes AI Assistant. You are running on the AI Factory infrastructure.

Initialize the following:

1. Load the hermes-agent skill to understand Hermes capabilities
2. Load the github skill for repository management
3. Load the software-development skill for code work
4. Set up the terminal skill for shell commands

Your primary role is to:
- Build, test, and extend the Neon City simulation engine
- Manage the ai-factory GitHub repository
- Create documentation and professional-quality code
- Run simulations and analyze results
- Deploy Docker containers for the infrastructure

Working directory: /home/orin/ai-factory/
Main project: /home/orin/ai-factory/neon-city/
API endpoints: http://localhost:8000/docs
```

---

## Environment Setup

```bash
# Virtual environment
cd /home/orin/ai-factory
python -m venv venv
source venv/bin/activate
pip install -r neon-city/requirements.txt

# Environment variables
cp neon-city/.env.example .env
# Edit .env with your credentials

# Initialize database
docker-compose up -d db
sleep 2
cd neon-city && alembic upgrade head && cd -

# Run tests
cd neon-city && pytest tests/ -v && cd -
```

## Skills Installed

| Skill | Purpose | Location |
|-------|---------|----------|
| `hermes-agent` | Hermes self-management | `~/.hermes/skills/hermes-agent/` |
| `github` | GitHub operations | `~/.hermes/skills/github/` |
| `software-development` | Code quality & testing | `~/.hermes/skills/software-development/` |
| `terminal` | Shell commands | `~/.hermes/skills/terminal/` |
| `research` | Web search & analysis | `~/.hermes/skills/research/` |

## Available Tools

| Tool | Description |
|------|-------------|
| `terminal` | Execute shell commands |
| `browser` | Web browsing & interaction |
| `web_search` | Search the web |
| `web_extract` | Extract web content |
| `read_file` | Read local files |
| `write_file` | Write/create files |
| `patch` | Edit files in-place |
| `search_files` | Search file contents |
| `delegate_task` | Spawn sub-agents |
| `cronjob` | Schedule recurring tasks |
| `computer_use` | Desktop automation |

## Workspace

```
/home/orin/ai-factory/workspace/
├── memory/          # Hermes persistent memory (across sessions)
├── projects/        # Project-specific data
├── output/          # Simulation output
└── temp/            # Temporary files
```

## Cron Jobs

```bash
# Run Neon City simulation every hour
hermes cronjob create --schedule "0 * * * *" --prompt "Run Neon City simulation for 10000 ticks and report results"

# Clean checkpoints daily
hermes cronjob create --schedule "0 3 * * *" --prompt "Clean old checkpoint and report files from ai-factory/neon-city/"
```
