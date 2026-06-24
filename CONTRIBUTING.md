# Contributing to AI Factory

Welcome! Thank you for your interest in contributing to AI Factory.

## Code of Conduct

- Be respectful and inclusive in all interactions
- Welcome newcomers and help them get started
- Provide constructive and specific feedback
- Focus on what is best for the community and the project

## How to Contribute

### Quick Start

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/ai-factory.git
cd ai-factory

# 2. Set up development environment
python -m venv venv
source venv/bin/activate
pip install -r neon-city/requirements.txt
pip install -e ".[dev]"

# 3. Create feature branch
git checkout -b feature/your-feature-name

# 4. Make changes, test, and submit PR
make test
make lint
git push origin feature/your-feature-name
# Then open a Pull Request on GitHub
```

### Branch Naming

| Prefix | Use For |
|--------|---------|
| `feature/` | New features |
| `fix/` | Bug fixes |
| `docs/` | Documentation only |
| `refactor/` | Code refactoring |
| `test/` | Test additions/improvements |
| `infra/` | Infrastructure/CI changes |
| `changelog/` | Changelog updates |

### Commit Messages

Follow conventional commits:

```
feat(agents): add black market trading for citizens
fix(engine): resolve memory leak in tick loop
docs(readme): update API examples
refactor(economy): extract order matching into separate module
test(events): add integration tests for riot events
```

### Code Standards

We enforce consistent code style:

| Tool | Purpose | Config |
|------|---------|--------|
| `black` | Code formatting | `pyproject.toml` |
| `ruff` | Linting | `pyproject.toml` |
| `mypy` | Type checking | `pyproject.toml` |
| `pytest` | Testing | `pyproject.toml` |

```bash
# Run all checks
make lint
make test

# Auto-format code
black neon-city/src/ neon-city/tests/
```

### Pull Request Process

1. **Test**: Ensure `make test` passes
2. **Lint**: Ensure `make lint` passes
3. **Document**: Update relevant documentation
4. **Changelog**: Add entry to `CHANGELOG.md`
5. **PR Description**: Describe what and why, reference issues
6. **Review**: Request review from maintainers
7. **CI**: Ensure all CI checks pass

## Areas for Contribution

### Simulation
- New agent types and behaviors
- Environmental events
- Economic mechanics
- Skill tree expansions

### Performance
- Async optimization
- Caching strategies
- Memory efficiency
- Tick engine improvements

### API
- New endpoints
- Middleware
- WebSocket real-time events
- Rate limiting

### Infrastructure
- CI/CD pipelines
- Monitoring and alerting
- Deployment scripts
- Docker improvements

### Documentation
- README improvements
- Tutorials and examples
- API documentation
- Architecture diagrams

## Questions?

- Open an issue with the `question` label
- Contact: matteohermesai@gmail.com

---

Your contributions are valued. Thank you for helping build AI Factory!
