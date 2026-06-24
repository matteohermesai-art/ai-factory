# Roadmap - AI Factory

Planned features and development direction.

## Current Version: 2.1.0

## v2.2.0 (Next)

### Planned
- [ ] Worker health monitoring dashboard
- [ ] Task retry mechanism with exponential backoff
- [ ] WebSocket real-time worker status updates
- [ ] Worker resource limits (CPU, memory)
- [ ] Task priority queue with preemption
- [ ] Workspace versioning (git integration per worker)

### Under Consideration
- [ ] Plugin system for custom worker types
- [ ] Worker pool auto-scaling
- [ ] Distributed worker execution (multi-host)

## v3.0.0 (Future)

### Goals
- [ ] Multi-protocol support (gRPC, WebSocket, HTTP/2)
- [ ] Worker authentication and authorization (OAuth2)
- [ ] Audit trail for all worker actions
- [ ] Multi-tenant support
- [ ] Worker marketplace (share/reuse worker configs)
- [ ] Visual workflow builder

### Breaking Changes (planned)
- [ ] New API versioning scheme (v2 endpoints)
- [ ] Config file format migration (YAML -> TOML)
- [ ] Database schema migration (Alembic)

## Completed

### v2.1.0 (2025-06-24)
- Auto database initialization
- SQLAlchemy models
- Docker entrypoint with health checks

### v2.0.0 (2025-06-24)
- Multi-agent orchestration
- Worker delegation system
- Cron job scheduling
- REST API
- Hermes skill system
- Docker infrastructure
- Professional documentation

### v1.0.0 (2025-01-15)
- Initial release
- Single-worker (Hermes)
- Basic tool access
- Memory persistence

---

## How to Contribute

1. Pick an item from "Planned" or "Under Consideration"
2. Open an issue to discuss approach
3. Submit PR referencing the issue
4. Update this roadmap when completed

## Decision Log

See [DECISIONS.md](DECISIONS.md) for architectural decision records (ADR).

---

*Last updated: 2025-06-24*
