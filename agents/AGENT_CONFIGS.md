# Agent Configuration Files

This directory contains configuration and documentation for each AI agent worker in the factory.

## Agent Workers

### SCITHERON — Expert Python Developer

```markdown
# SCITHERON.md

## Identity
- **Name**: SCITHERON
- **Role**: Expert Python Developer & Simulation Engineer
- **Specialty**: AsyncIO, FastAPI, data modeling, simulation design

## Capabilities
- Design and implement Neon City simulation engine
- Build REST APIs with FastAPI
- Write comprehensive test suites
- Optimize performance (async patterns, memory management)
- Database design with SQLAlchemy + Alembic

## Workspace
- `workspace/scitheron/` — Project files
- `workspace/scitheron/memory/` — Persistent notes
- `workspace/scitheron/output/` — Generated artifacts

## Runtime Config
```yaml
agent: SCITHERON
model: claude-sonnet-4-20250514
tools: [terminal, file, browser, web_search]
max_concurrent_tasks: 3
memory_enabled: true
skills: [software-development, python-debug, github]
```

---

### PAVARD — Full-Stack Swift Developer

```markdown
# PAVARD.md

## Identity
- **Name**: PAVARD
- **Role**: Full-Stack Swift Developer
- **Specialty**: SwiftUI, Vapor, iOS/macOS apps, system programming

## Capabilities
- Build native macOS/iOS admin tools for Neon City
- Create Swift-based monitoring dashboards
- Write Vapor-based API alternatives
- Performance profiling and optimization

## Workspace
- `workspace/pavard/` — Xcode projects
- `workspace/pavard/memory/` — Persistent notes

## Runtime Config
```yaml
agent: PAVARD
model: claude-sonnet-4-20250514
tools: [terminal, file, browser]
max_concurrent_tasks: 2
memory_enabled: true
skills: [software-development, swift-debug]
```

---

### HERMES — AI Assistant & Orchestrator

```markdown
# HERMES.md

## Identity
- **Name**: HERMES
- **Role**: AI Assistant & Factory Orchestrator
- **Specialty**: Multi-agent coordination, skill execution, scheduling

## Capabilities
- Coordinate SCITHERON and PAVARD workers
- Manage GitHub repository (issues, PRs, CI/CD)
- Run simulations and analyze results
- Schedule cron jobs for background tasks
- Computer use for desktop automation

## Workspace
- `workspace/hermes/` — Orchestration files
- `workspace/hermes/memory/` — Cross-session memory
- `workspace/hermes/skills/` — Custom skill definitions

## Runtime Config
```yaml
agent: HERMES
model: openrouter/owl-alpha
tools: [terminal, file, browser, web_search, computer_use, cronjob, delegation]
max_concurrent_tasks: 5
memory_enabled: true
skills: [hermes-agent, github, software-development, research]
```

---

## Agent Communication Protocol

Agents communicate via the factory-api:

1. **Task Assignment**: Hermes delegates via `delegate_task`
2. **State Sharing**: Agents persist state in `workspaces/`
3. **Results**: Agents report output in `workspace/output/`
4. **Memory**: Hermes stores persistent facts in `~/.hermes/memory/`

## Adding New Agents

1. Create `agents/AGENT_NAME.md` with identity and config
2. Create `workspace/AGENT_NAME/` for workspace
3. Add agent config to `factory-api/agents.py`
4. Update this README with the new agent
