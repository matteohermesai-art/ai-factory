# Makefile - AI Factory

.PHONY: help up down restart test lint format init-db seed logs status clean simulate simulate-ultra shell

# Default target
help: ## Show this help
	@echo "AI Factory - Available Commands"
	@echo "================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Docker
up: ## Start all services
	docker-compose up -d --build
	@echo "Services started:"
	@echo "  API      -> http://localhost:8000/docs"
	@echo "  Factory  -> http://localhost:8080/docs"

down: ## Stop all services
	docker-compose down

restart: down up ## Restart all services

logs: ## View logs from all services
	docker-compose logs -f --tail=100

status: ## Show service status
	docker-compose ps

# Database
init-db: ## Initialize database and run migrations
	docker-compose exec api alembic upgrade head
	@echo "Database initialized"

seed: ## Seed database with initial data
	docker-compose exec api python scripts/seed.py
	@echo "Database seeded"

shell: ## Open shell in API container
	docker-compose exec api bash

# Development
test: ## Run test suite
	pytest tests/ -v --tb=short

test-cov: ## Run tests with coverage
	pytest tests/ --cov=src --cov-report=html --cov-report=term

lint: ## Lint and check formatting
	ruff check src/ tests/
	black --check src/ tests/
	mypy src/

format: ## Auto-format code
	black src/ tests/
	ruff check --fix src/ tests/

# Simulation
simulate: ## Run simulation (local)
	python -m src.main

simulate-ultra: ## Run 100k tick simulation (background)
	nohup python scripts/run_simulation.py --ticks 100000 --agents 200 > logs/sim_$$(date +%Y%m%d_%H%M%S).log 2>&1 &
	@echo "Simulation started in background. PID: $$!"

# Cleanup
clean: ## Remove build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov .coverage 2>/dev/null || true
	@echo "Cleaned!"

clean-all: ## Remove everything (including volumes)
	docker-compose down -v --rmi all 2>/dev/null || true
	make clean
