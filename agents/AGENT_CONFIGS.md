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
| **Role** | Backend Developer & Python Expert |
| **Model** | claude-sonnet-4-20250514 |
| **Tools** | terminal, file, browser, web_search, delegate_task |
| **Max Tasks** | 3 concurrent |
| **Skills** | python-debug, software-development, github, test-driven-development |

**Responsibilities:**
- Build backend services and REST APIs
- Write comprehensive test suites with pytest
- Code review and refactoring
- Async Python optimization
- Database design with SQLAlchemy

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
- Build native macOS/iOS applications with SwiftUI
- Write server-side Swift with Vapor
- Performance profiling and optimization
- Cross-platform CLI tools

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
- Coordinate SCITHERON and PAVARD workers via delegation
- Manage GitHub repository (issues, PRs, CI/CD)
- Schedule cron jobs for background tasks
- Computer use for desktop automation
- Research and information gathering
- Memory persistence across sessions

**Workspace:** `workspace/hermes/`

---

## Communication Protocol

1. **Task Assignment**: Hermes delegates via `delegate_task`
2. **State Sharing**: Workers persist state in `workspace/<agent>/memory/`
3. **Results**: Worker reports output in `workspace/<agent>/output/`
4. **Memory**: Hermes stores persistent facts in memory store

## Adding New Workers

1. Create `agents/<NAME>.md` with identity and config
2. Create `workspace/<NAME>/` for workspace
3. Add worker class in `src/worker/`
4. Register routes in `src/api/routes/`
5. Update this README with the new worker
6. Add worker-specific skills to `skills/`

---

*Last updated: 2025-06-24*
