# Changelog

All notable changes to Neon City Simulation will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- v2.0: Enhanced simulation with 200+ agents on 80x80 grid
- Skill tree evolution system (4 tiers per agent type)
- Faction reputation tracking
- Black market with illicit items (neurotox, hack toolkits, fake IDs)
- Legal system: arrests, bounties, probation, criminal records
- Environmental events: blackouts, ransomware attacks, riots, network glitches
- Mission system with dynamic quest generation
- Propaganda/influence mechanics for corporations and influencers
- Checkpoint system for long simulations
- Garbage collection for memory optimization
- Full E2E test suite
- REST API with FastAPI
- Structured logging with structlog
- Docker & Docker Compose support
- Alembic database migrations
- Replay system for simulation playback

### Performance
- 126 tick/sec with 200 agents
- Checkpoint save/resume for 100k+ tick simulations
- Memory optimization via periodic GC and market order cleanup

## [1.0.0] - 2025-01-15

### Added
- Initial release
- Grid-based city simulation (100x100)
- 4 agent types: citizen, hacker, corporation, police
- Virtual economy with credits and data currencies
- Event system with cyber attacks and police raids
- REST API for simulation control
- Basic persistence layer with SQLite
- Test suite with pytest
