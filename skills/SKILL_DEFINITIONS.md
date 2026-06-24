# Hermes Skill Definitions

This document describes all skills available to Hermes via the `~/.hermes/skills/` directory and the SKILL.md format.

## Skill Format

Each skill is a directory containing `SKILL.md`:

```
~/.hermes/skills/
  └── skill_name/
      ├── SKILL.md           # Required: skill definition
      ├── templates/          # Optional: templates
      ├── scripts/            # Optional: helper scripts
      └── references/         # Optional: reference docs
```

## SKILL.md Template

```yaml
---
name: skill_name
description: Short description of when to trigger this skill
triggers:
  - keyword1
  - keyword2
---

# Skill Name

## When to Use
Describe when this skill should be activated.

## Steps
1. First step
2. Second step
3. Third step

## Pitfalls
- Watch out for X
- Avoid Y

## Verification
- How to confirm the skill executed correctly
```

---

## Skill: hermes-agent

**Purpose**: Configure and extend Hermes Agent itself.

```yaml
---
name: hermes-agent
description: Configure, extend, or troubleshoot Hermes Agent
triggers:
  - "hermes config"
  - "setup hermes"
  - "hermes skills"
  - "hermes plugins"
  - "hermes cron"
---

# Hermes Agent Configuration

## When to Use
- User asks about Hermes features, tools, or capabilities
- Need to configure Hermes CLI, config, models, providers
- Managing Hermes cron jobs
- Troubleshooting Hermes behavior

## Configuration Commands
```bash
hermes config set <key> <value>
hermes config get <key>
hermes tools
hermes skills list
hermes cron list
```

## Key Configuration Areas
- Model selection and provider setup
- Toolset configuration
- Skill management
- Cron job scheduling
- Gateway and plugin settings

## Pitfalls
- Always verify provider API keys are set
- Check model compatibility with selected tools
- Cron jobs run in fresh context - prompts must be self-contained
```

---

## Skill: github

**Purpose**: GitHub operations via `gh` CLI.

```yaml
---
name: github
description: GitHub operations - issues, PRs, repos, CI/CD
triggers:
  - "github"
  - "commit"
  - "push"
  - "pull request"
  - "PR"
  - "issue"
---

# GitHub Operations

## When to Use
- User asks about git/GitHub operations
- Creating/updating repositories
- Managing pull requests
- Creating and triaging issues

## Common Commands
```bash
# Repository
gh repo create <name> --public --source=. --push
gh repo view

# Commits
git add -A
git commit -m "feat: description"
git push

# Pull Requests
gh pr create --title "Feature: X" --body "Description"
gh pr list
gh pr merge <number>

# Issues
gh issue create --title "Bug: X" --label bug
gh issue list --state open

# CI
gh run list
gh run view <id>
```

## Pitfalls
- Always verify git user.name and user.email are set
- Use `GITHUB_TOKEN` env var or `gh auth login`
- Never commit secrets or .env files
- Follow conventional commit messages
```

---

## Skill: software-development

**Purpose**: Code quality, testing, and development workflows.

```yaml
---
name: software-development
description: Software development best practices - testing, linting, code review
triggers:
  - "test"
  - "lint"
  - "code review"
  - "pytest"
  - "black"
  - "ruff"
---

# Software Development Workflow

## When to Use
- Writing or reviewing code
- Setting up CI/CD
- Running test suites
- Code quality checks

## Testing
```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific test
pytest tests/test_engine/test_tick.py -v
```

## Linting & Formatting
```bash
# Format with black
black src/ tests/

# Lint with ruff
ruff check src/ tests/

# Type check with mypy
mypy src/
```

## Code Review Checklist
- [ ] Tests pass
- [ ] Code follows project conventions
- [ ] Type hints present
- [ ] No hardcoded secrets
- [ ] Documentation updated
```

---

## Skill: python-debug

**Purpose**: Debug Python applications.

```yaml
---
name: python-debug
description: Debug Python with pdb REPL and debugpy remote
triggers:
  - "debug"
  - "traceback"
  - "pdb"
  - "breakpoint"
  - "error"
---

# Python Debugging

## When to Use
- Tracking down bugs
- Understanding complex code flow
- Inspecting state at runtime

## Quick Debug
```python
# Insert breakpoint in code
breakpoint()  # Python 3.7+
```

## Remote Debug (DAP)
```bash
# Terminal 1: Start debugger
python -m debugpy --listen 5678 src/main.py

# Terminal 2: Attach
python -c "import debugpy; debugpy.connect(5678)"
```

## PDB
```bash
python -m pdb src/main.py
# Commands: n (next), s (step), c (continue), p (print), q (quit)
```
```

---

## Skill: systematic-debugging

**Purpose**: 4-phase root cause debugging methodology.

```yaml
---
name: systematic-debugging
description: 4-phase root cause debugging - understand bugs before fixing
triggers:
  - "bug"
  - "unexpected behavior"
  - "fix"
  - "broken"
---

# Systematic Debugging (4 Phases)

## Phase 1: Understand
- Reproduce the bug reliably
- Identify expected vs actual behavior
- Check recent git changes

## Phase 2: Locate
- Narrow down to the smallest failing unit
- Use logs and debug output
- Binary search through changes

## Phase 3: Fix
- Fix the root cause, not symptoms
- Write a test that reproduces the bug first
- Apply minimal fix

## Phase 4: Verify
- Confirm fix resolves the issue
- Run full test suite
- Add regression test
```

---

## Skill: research

**Purpose**: Web search and information gathering.

```yaml
---
name: research
description: Academic research, web search, domain reconnaissance
triggers:
  - "search"
  - "research"
  - "find"
  - "look up"
  - "what is"
---

# Research Workflow

## Web Search
Use web_search for quick lookups:
```python
web_search(query="asyncio best practices", limit=5)
```

## Deep Research
Use web_fetch for full page content:
```python
web_extract(urls=["https://docs.python.org/3/library/asyncio.html"])
```

## Academic Research
Use arxiv skill for paper searches.

## Blog Monitoring
Use blogwatcher for RSS feeds.
```
```

---

*Last updated: 2025-06-24*
