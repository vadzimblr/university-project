.PHONY: build up down restart logs lint test install migrate upgrade downgrade migration-create db-current

build:
	docker-compose build

update:
	docker-compose build --no-cache
	docker-compose up -d

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose down && docker-compose up -d

logs:
	docker-compose logs -f

enter:
	docker-compose run --rm scene_splitter bash

install: build migrate
	@echo "Installation complete! Services are starting..."
	cp .env.example .env
	docker-compose up -d

migrate:
	@echo "Running database migrations..."
	docker-compose run --rm -e PYTHONPATH=/app scene_splitter alembic upgrade head

upgrade: migrate

downgrade:
	@echo "Rolling back database migration..."
	docker-compose run --rm scene_splitter alembic downgrade -1

migration-create:
	@read -p "Enter migration name: " name; \
	docker-compose run --rm scene_splitter alembic revision --autogenerate -m "$$name"

db-current:
	docker-compose run --rm scene_splitter alembic current

db-history:
	docker-compose run --rm scene_splitter alembic history

db-reset: down
	@echo "Resetting database..."
	docker-compose up -d postgres_db
	@echo "Waiting for database to be ready..."
	sleep 5
	docker-compose run --rm scene_splitter alembic upgrade head
