# Agent Configurations

This document describes all AI agent workers in the AI Factory.

## Overview

AI Factory uses a multi-agent architecture where specialized workers collaborate under the orchestration of Hermes.

```
            HERMES (Orchestrator)
           /         |          \
          v          v          v
    SCITHERON     PAVARD     [Future]
    (Python)      (Swift)    (Agents)
```

## Workers

### SCITHERON — Expert Python Developer

| Field | Value |
|-------|-------|
| **Role** | Simulation Engineer & Python Expert |
| **Model** | claude-sonnet-4-20250514 |
| **Tools** | terminal, file, browser, web_search, delegate_task |
| **Max Tasks** | 3 concurrent |
| **Skills** | python-debug, software-development, github, test-driven-development |

**Responsibilities:**
- Design and implement Neon City simulation engine
- Build REST APIs with FastAPI
- Write comprehensive test suites
- Optimize async patterns and memory management
- Database design with SQLAlchemy + Alembic

**Workspace:** `workspace/scitheron/`

---

### PAVARD — Full-Stack Swift Developer

| Field | Value |
|-------|-------|
| **Role** | Native App Developer (macOS/iOS) |
| **Model** | claude-sonnet-4-20250514 |
| **Tools** | terminal, file, browser, web_search |
| **Max Tasks** | 2 concurrent |
| **Skills** | software-development, github |

**Responsibilities:**
- Build native macOS/iOS admin tools for Neon City
- Create Swift-based monitoring dashboards
- Write Vapor-based API alternatives
- Performance profiling and optimization

**Workspace:** `workspace/pavard/`

---

### HERMES — AI Assistant & Orchestrator

| Field | Value |
|-------|-------|
| **Role** | Primary AI Assistant & Factory Orchestrator |
| **Model** | openrouter/owl-alpha |
| **Tools** | All tools (terminal, file, browser, web_search, computer_use, cronjob, delegate_task) |
| **Max Tasks** | 5 concurrent |
| **Skills** | hermes-agent, github, software-development, research, terminal |

**Responsibilities:**
- Coordinate SCITHERON and PAVARD workers
- Manage GitHub repository (issues, PRs, CI/CD)
- Run simulations and analyze results
- Schedule cron jobs for background tasks
- Computer use for desktop automation
- Memory persistence across sessions

**Workspace:** `workspace/hermes/`

---

## Communication Protocol

1. **Task Assignment**: Hermes delegates via `delegate_task`
2. **State Sharing**: Agents persist state in `workspace/<agent>/memory/`
3. **Results**: Agent reports output in `workspace/<agent>/output/`
4. **Memory**: Hermes stores persistent facts in `~/.hermes/memory/`

## Adding New Agents

1. Create `agents/<NAME>.md` with identity and config
2. Create `workspace/<NAME>/` for workspace
3. Add agent config to `factory-api/agents.py`
4. Update this README with the new agent
5. Add agent-specific skills to `skills/`

---

*Last updated: 2025-06-24*
