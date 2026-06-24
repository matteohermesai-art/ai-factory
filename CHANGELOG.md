# Changelog

All notable changes to AI Factory will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-06-24

### Added
- Auto database initialization via Docker entrypoint
- SQLAlchemy models: Worker, Task, CronJob, WorkspaceFile, Memory
- `scripts/init-db.py` — idempotent table creation
- `docker-entrypoint.sh` — waits for DB, creates tables, starts API
- Database section in README and STARTUP guides
- Database table documentation

### Changed
- Docker entrypoint now auto-creates tables (no manual `make init-db` needed)
- Makefile: removed `init-db` and `seed` targets (now automatic)
- Updated docker-compose with longer start period for DB init

## [2.0.0] - 2025-06-24

### Added
- Multi-agent orchestration framework with 3 specialized workers
- Worker delegation system with `delegate_task`
- Cron job scheduling for recurring tasks
- REST API with FastAPI for task management and monitoring
- Hermes skill system with 7 markdown-based skills
- Docker infrastructure with API, PostgreSQL, and Redis
- Structured logging with structlog
- Worker persistence layer (workspace, memory, state)
- Full E2E test suite
- Professional documentation: README, CHANGELOG, CONTRIBUTING, LICENSE
- Worker configuration files (SCITHERON, PAVARD, HERMES)
- Multi-stage Dockerfile with healthcheck
- pyproject.toml with complete tool configuration

## [1.0.0] - 2025-01-15

### Added
- Initial release
- Single-worker (Hermes) with basic tool access
- File operations and terminal commands
- Basic memory persistence
