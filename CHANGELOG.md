# Changelog

All notable changes to AI Factory will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-06-24

### Added
- Multi-agent factory with 200+ agents on 80x80 grid
- Full economy: credits, data, black market, corporation shares
- Skill tree evolution (4 tiers per agent type)
- Faction reputation tracking system
- Legal system: arrests, bounties, probation, criminal records
- Environmental events: blackouts, ransomware, riots, network glitches, pandemonium
- Mission system with dynamic quest generation and rewards
- Propaganda mechanics for corporations and influencers
- Agent workers: SCITHERON (Python), PAVARD (Swift), Hermes (AI orchestrator)
- Hermes skill system with procedural memory
- REST API with FastAPI (OpenAPI docs at /docs)
- Docker and Docker Compose infrastructure
- PostgreSQL with Alembic migrations
- Redis caching layer
- Structured logging with structlog
- Replay system for simulation playback
- Cron job scheduling for background tasks
- Checkpoint system for long simulations (100k+ ticks)
- Garbage collection for memory optimization
- Full E2E test suite with >80% coverage
- Professional documentation: README, CHANGELOG, CONTRIBUTING, LICENSE
- Agent configuration files with runtime configs
- Hermes skill definitions (9 skills)
- Multi-stage Dockerfile with healthcheck
- docker-compose with 5 services

### Performance
- 126 tick/sec with 200 agents
- Checkpoint save/resume for 100k+ tick simulations
- Memory optimization via periodic GC and market order cleanup

## [1.0.0] - 2025-01-15

### Added
- Initial release
- Single-agent worker system
- Basic simulation engine (100x100 grid, 4 agent types)
- Economy with credits and data currencies
- Event system
- REST API
- Test suite with pytest
