# Architecture Decision Records (ADR)

This document records important architectural decisions made for AI Factory.

## ADR-001: Use SQLAlchemy with AsyncIO for Persistence

**Date**: 2025-06-24
**Status**: Accepted
**Context**: Need persistent storage for worker state, tasks, and memory. Must support both SQLite (dev) and PostgreSQL (prod).

**Decision**: Use SQLAlchemy 2.0 with AsyncIO support. Use aiosqlite for development and asyncpg for production.

**Consequences**:
- Single ORM for both databases
- Async-native throughout
- Alembic for migrations
- Type-safe models with mapped_column

---

## ADR-002: Auto-Initialize Database via Docker Entrypoint

**Date**: 2025-06-24
**Status**: Accepted
**Context**: Users cloning the repo need tables created automatically. Manual `make init-db` is error-prone.

**Decision**: Docker entrypoint (`docker-entrypoint.sh`) waits for PostgreSQL health check, then runs `scripts/init-db.py` before starting the API.

**Consequences**:
- Zero-config setup for users
- Idempotent — safe to run multiple times
- No manual migration steps needed
- Container restart recreates if schema changes

**Alternatives Considered**:
- Alembic migrations only — too complex for initial setup
- Init container — adds complexity to docker-compose
- Manual script — requires user action

---

## ADR-003: Markdown-Based Skill System (SKILL.md)

**Date**: 2025-01-15
**Status**: Accepted
**Context**: Hermes needs procedural memory that persists across sessions and can be version-controlled.

**Decision**: Skills are markdown files in `~/.hermes/skills/` or project `skills/` directory. Each skill has a `SKILL.md` with YAML frontmatter.

**Consequences**:
- Human-readable skill definitions
- Version controllable via git
- Easy to create and modify
- No database required for skill storage

---

## ADR-004: Multi-Agent Orchestration via Delegate_Task

**Date**: 2025-06-24
**Status**: Accepted
**Context**: Need to coordinate multiple specialized workers (Python dev, Swift dev) under a central orchestrator (Hermes).

**Decision**: Hermes uses `delegate_task` tool to spawn sub-agents with isolated contexts. Each worker gets its own workspace, model configuration, and tool set.

**Consequences**:
- Workers are isolated — no shared state
- Each worker can have different model and tools
- Hermes handles coordination and result aggregation
- Sub-agents cannot delegate further (max depth 1)

---

## ADR-005: PostgreSQL as Primary Database

**Date**: 2025-06-24
**Status**: Accepted
**Context**: Need a production-grade database that supports async operations and scales well.

**Decision**: PostgreSQL 16 as primary database. SQLite for development only. Alembic for schema migrations.

**Consequences**:
- Production-grade reliability
- JSON column support for metadata
- Full-text search capability
- Requires Docker for local dev (or external DB)

---

## ADR-006: Redis for Caching and Message Broker

**Date**: 2025-06-24
**Status**: Accepted
**Context**: Need caching for worker state, task queue, and session management.

**Decision**: Redis 7 as cache and message broker. Used for task queue, worker state cache, and rate limiting.

**Consequences**:
- Fast in-memory operations
- Pub/sub for real-time events
- Atomic operations for task queue
- Additional infrastructure component to maintain

---

## ADR-007: FastAPI for REST API

**Date**: 2025-06-24
**Status**: Accepted
**Context**: Need a modern, async-native REST API framework with automatic OpenAPI documentation.

**Decision**: FastAPI with Pydantic models for validation. Uvicorn as ASGI server.

**Consequences**:
- Automatic OpenAPI docs at /docs
- Async-native
- Type-safe request/response validation
- High performance

---

## ADR-008: Structured Logging with structlog

**Date**: 2025-06-24
**Status**: Accepted
**Context**: Need machine-readable logs for monitoring and debugging in production.

**Decision**: structlog for structured JSON logging. Different formats for development (colored) and production (JSON).

**Consequences**:
- Machine-parseable logs
- Correlation IDs for request tracing
- Easy integration with ELK/Loki

---

## How to Add an ADR

1. Create a new ADR with sequential number (ADR-NNN)
2. Include: Date, Status, Context, Decision, Consequences
3. Record rejected alternatives if applicable
4. Update this index

---

*Last updated: 2025-06-24*
