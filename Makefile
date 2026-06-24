# Makefile — AI Factory
.PHONY: up down test lint clean init-db seed logs

# ═══ Docker ═══
up:
	docker-compose up -d --build
	@echo "✅ AI Factory started"
	@echo "  Neon City API: http://localhost:8000/docs"
	@echo "  Factory API:   http://localhost:8080/docs"
	@echo "  Dashboard:     http://localhost:3000"

down:
	docker-compose down
	@echo "🛑 AI Factory stopped"

restart: down up

# ═══ Database ═══
init-db:
	docker-compose exec neon-city-api alembic upgrade head
	@echo "✅ Database initialized"

seed:
	docker-compose exec neon-city-api python scripts/seed.py
	@echo "✅ Database seeded"

# ═══ Development ═══
test:
	cd neon-city && pytest tests/ -v --tb=short

test-cov:
	cd neon-city && pytest tests/ --cov=src --cov-report=html

lint:
	cd neon-city && ruff check src/ tests/
	cd neon-city && black --check src/ tests/

format:
	cd neon-city && black src/ tests/
	cd neon-city && ruff check --fix src/ tests/

# ═══ Simulation ═══
simulate:
	cd neon-city && python -c "import asyncio; from src.main import run_simulation; asyncio.run(run_simulation())"

simulate-ultra:
	cd neon-city && python scripts/run_simulation.py --ticks 100000 --agents 200

# ═══ Utilities ═══
logs:
	docker-compose logs -f

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache htmlcov
	@echo "🧹 Cleaned"

status:
	docker-compose ps
