# Changelog

All notable changes to AI Factory will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- v2.0: Multi-agent AI factory with Neon City simulation
- 200+ autonomous agents (citizens, hackers, police, corporations)
- Full economy with markets, black markets, and multi-currency
- Skill tree evolution system (4 tiers per agent type)
- Faction reputation tracking
- Legal system: arrests, bounties, probation, criminal records
- Environmental events: blackouts, ransomware, riots, network glitches
- Mission system with dynamic quest generation
- Agent workers: SCITHERON (Python), PAVARD (Swift), Hermes (AI assistant)
- Hermes skill system with procedural memory
- REST API with FastAPI
- Docker & Docker Compose infrastructure
- Alembic database migrations (PostgreSQL + asyncpg)
- Structured logging with structlog
- Replay system for simulation playback
- Cron job scheduling for background tasks

### Performance
- 126 tick/sec with 200 agents on 80x80 grid
- Checkpoint save/resume for 100k+ tick simulations
- Memory optimization via periodic GC and market order cleanup

## [1.0.0] - 2025-01-15

### Added
- Initial release
- Single-agent worker system
- Basic neon_city simulation (100x100 grid, 4 agent types)
- Economy with credits and data currencies
- Event system
- REST API
- Test suite with pytest
