# Changelog

All notable changes to AI Factory will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

### Architecture
- AsyncIO-based task queue
- Worker isolation with separate workspaces
- Skill loading on-demand via SKILL.md format
- RESTful API for all operations

## [1.0.0] - 2025-01-15

### Added
- Initial release
- Single-worker (Hermes) with basic tool access
- File operations and terminal commands
- Basic memory persistence
