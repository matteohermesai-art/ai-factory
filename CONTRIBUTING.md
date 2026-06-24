# Contributing to AI Factory

Thank you for your interest in contributing! This document outlines the guidelines for contributing to the AI Factory project.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback

## How to Contribute

### 1. Fork and Clone

```bash
git clone https://github.com/matteohermesai-art/ai-factory.git
cd ai-factory
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` — New features
- `bugfix/` — Bug fixes
- `docs/` — Documentation
- `refactor/` — Code refactoring
- `test/` — Test additions

### 3. Development Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r neon-city/requirements.txt
pip install -e ".[dev]"
```

### 4. Code Standards

- **Formatting**: Black (line-length 100)
- **Linting**: ruff
- **Type Hints**: mypy strict
- **Tests**: pytest with >80% coverage

```bash
# Format code
make lint

# Run tests
make test
```

### 5. Commit Messages

Follow conventional commits:

```
feat: add new agent type
fix: resolve market matching bug
docs: update API documentation
refactor: optimize tick engine
test: add economy integration tests
```

### 6. Pull Request

1. Ensure all tests pass
2. Update CHANGELOG.md
3. Update documentation if needed
4. Request review

## Project Structure

```
ai-factory/
├── neon-city/       # Simulation engine (main code)
├── agents/          # Agent configurations
├── factory-api/     # REST API
├── skills/          # Hermes skill definitions
├── infra/           # Docker, CI/CD
└── workspace/       # Agent workspaces
```

## Areas for Contribution

- **Simulation**: New agent behaviors, events, economies
- **Performance**: Optimization, caching, async improvements
- **API**: New endpoints, middleware, schemas
- **Tests**: Coverage, integration tests, benchmarks
- **Docs**: README improvements, tutorials, examples
- **Infrastructure**: CI/CD, monitoring, deployment

## Questions?

Open an issue with the `question` label or contact matteohermesai@gmail.com.

---

Thank you for contributing to AI Factory!
