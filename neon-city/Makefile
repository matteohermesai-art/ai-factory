.PHONY: up down init-db migrate seed test test-cov lint replay run

# Start all services
up:
	docker compose up -d

# Stop all services
down:
	docker compose down

# Initialize database and run migrations
init-db: up
	docker compose exec api alembic upgrade head

# Run database migrations
migrate:
	docker compose exec api alembic upgrade head

# Seed the database with initial data
seed:
	docker compose exec api python scripts/seed.py

# Run tests
test:
	python -m pytest tests/ -v

# Run tests with coverage
test-cov:
	python -m pytest tests/ -v --cov=src --cov-report=term-missing

# Lint code
lint:
	python -m ruff check src/ tests/

# Run replay CLI
replay:
	python scripts/replay_cli.py

# Run the API locally (without Docker)
run:
	uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
