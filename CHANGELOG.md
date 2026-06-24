# Changelog

All notable changes to AI Factory will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Database models and auto-initialization system
- Docker entrypoint with health checks
- Multi-agent worker delegation system

---

## [2.1.0] - 2025-06-24

### Added
- Auto database initialization via Docker entrypoint (`docker-entrypoint.sh`)
- SQLAlchemy models: `Worker`, `Task`, `CronJob`, `WorkspaceFile`, `Memory`
- `scripts/init-db.py` — idempotent table creation with `Base.metadata.create_all`
- Database section in README and STARTUP guides
- Database table documentation

### Changed
- Docker entrypoint now auto-creates tables on startup (no manual `make init-db` needed)
- Makefile: removed `init-db` and `seed` targets (now automatic on `make up`)
- Updated docker-compose with longer start period for DB init
- Dockerfile: multi-stage build with entrypoint script

### Removed
- Manual `make init-db` target (replaced by automatic entrypoint)
- Manual `make seed` target (replaced by automatic on startup)

---

## [2.0.0] - 2025-06-24

### Added
- Multi-agent orchestration framework with 3 specialized workers
- Worker delegation system via `delegate_task` tool
- Cron job scheduling via `cronjob` tool
- REST API with FastAPI for task management and monitoring
- Hermes skill system with 7 markdown-based skills
- Docker and Docker Compose infrastructure (API + PostgreSQL + Redis)
- Structured logging with structlog
- Worker persistence layer (workspace, memory, state)
- Full E2E test suite with pytest
- Professional documentation: README, CHANGELOG, CONTRIBUTING, LICENSE
- Worker configuration files: SCITHERON.md, PAVARD.md, HERMES.md
- Multi-stage Dockerfile with healthcheck
- `pyproject.toml` with complete tool configuration (black, ruff, mypy, pytest, coverage)

### Changed
- Rewrote documentation to reflect multi-agent worker purpose (removed neon-city references)
- Restructured README to focus on workers, delegation, and API

### Fixed
- Repository documentation now accurately represents the project scope

---

## [1.0.0] - 2025-01-15

### Added
- Initial release
- Single-worker (Hermes) with basic tool access (terminal, file, web search)
- File operations and terminal commands
- Basic memory persistence via `~/.hermes/memory/`
- Core tool system (web_search, web_extract, read_file, write_file, delegate_task, cronjob)
- Skill loading system (SKILL.md format)
- Computer use capability
- Session search across conversation history

---

## Release Process

### Versioning

This project uses [Semantic Versioning](https://semver.org/):

| Version | Meaning |
|---------|---------|
| `MAJOR.MINOR.PATCH` | e.g., `2.1.0` |
| MAJOR | Breaking changes |
| MINOR | New features (backward compatible) |
| PATCH | Bug fixes only |

### Creating a Release

```bash
# 1. Update CHANGELOG: move Unreleased to new version
# 2. Commit with version bump
git add -A
git commit -m "chore: release v2.1.0"

# 3. Create annotated tag
git tag -a v2.1.0 -m "Release v2.1.0: Auto database initialization"

# 4. Push
git push origin main --tags

# 5. Create GitHub Release (see .github/workflows/release.yml)
gh release create v2.1.0 \
  --title "v2.1.0 - Auto Database Init" \
  --notes-file CHANGELOG.md \
  --latest
```

### GitHub Releases

Each version has a GitHub Release with:
- Release notes from CHANGELOG
- Source code (zip/tgz)
- Docker images (optional)

### Breaking Changes Policy

- Breaking changes are documented in CHANGELOG with migration guide
- Deprecated features are maintained for 1 major version before removal
- Security patches may be released as minor versions with clear communication

---

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features.

---

## Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

| Type | Description | Version Impact |
|------|-------------|----------------|
| `feat:` | New feature | MINOR |
| `fix:` | Bug fix | PATCH |
| `docs:` | Documentation only | none |
| `refactor:` | Code refactoring | none |
| `test:` | Test additions | none |
| `perf:` | Performance improvement | PATCH |
| `chore:` | Build/tooling | none |
| `Breaking:` | Breaking change | MAJOR |

Example:
```
feat(workers): add delegation timeout option

Implements configurable timeout for sub-agent delegation to prevent
orphaned tasks when workers are unresponsive.

Refs: #42
Closes: #38
```
