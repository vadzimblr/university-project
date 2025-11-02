.PHONY: help install run dev test clean docker-build docker-up docker-down migration-create migration-up migration-down migration-history migration-current inbox-stats inbox-errors inbox-dlq inbox-consumer-logs worker-logs beat-logs

help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  run         - Run the application"
	@echo "  dev         - Run in development mode"
	@echo "  test        - Run tests"
	@echo "  clean       - Clean up"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-up   - Start with Docker Compose"
	@echo "  docker-down - Stop Docker Compose"
	@echo "  migration-create - Create new migration"
	@echo "  migration-up - Apply migrations"
	@echo "  migration-down - Rollback migration"
	@echo "  migration-history - Show migration history"
	@echo "  migration-current - Show current migration"
	@echo ""
	@echo "Inbox Pattern commands:"
	@echo "  inbox-stats         - Show inbox events statistics"
	@echo "  inbox-errors        - Show recent events with errors"
	@echo "  inbox-dlq           - Show dead letter queue events"
	@echo "  inbox-consumer-logs - Show inbox consumer logs"
	@echo "  worker-logs         - Show celery worker logs"
	@echo "  beat-logs           - Show celery beat logs"

install:
	docker-compose run --rm image-generator pip install -r requirements.txt

run:
	docker-compose run --rm image-generator uvicorn app.main:app --host 0.0.0.0 --port 7003

dev:
	docker-compose up

test:
	docker-compose run --rm image-generator python -m pytest tests/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

build:
	docker-compose build

up:
	docker-compose up --remove-orphans -d

down:
	docker-compose down

# Migration commands
migration-create:
	docker-compose run --rm image-generator alembic revision --autogenerate -m "$(msg)"

migration-up:
	docker-compose run --rm image-generator alembic upgrade head

migration-down:
	docker-compose run --rm image-generator alembic downgrade -1

migration-history:
	docker-compose run --rm image-generator alembic history

migration-current:
	docker-compose run --rm image-generator alembic current

shell:
	docker-compose run --rm image-generator /bin/bash

# Inbox Pattern monitoring commands
inbox-stats:
	@echo "=== Inbox Events Statistics ==="
	@docker-compose exec -T image-generator psql $(DATABASE_URL) -c "\
		SELECT \
			COUNT(*) FILTER (WHERE processed = false) as unprocessed, \
			COUNT(*) FILTER (WHERE processed = true) as processed, \
			COUNT(*) FILTER (WHERE retry_count > 0 AND processed = false) as with_errors, \
			COUNT(*) FILTER (WHERE processed = true AND last_error LIKE 'FAILED after%') as dlq, \
			COUNT(*) as total \
		FROM inbox_events;"

inbox-errors:
	@echo "=== Recent Events with Errors ==="
	@docker-compose exec -T image-generator psql $(DATABASE_URL) -c "\
		SELECT id, event_type, retry_count, last_error, updated_at \
		FROM inbox_events \
		WHERE retry_count > 0 AND processed = false \
		ORDER BY updated_at DESC \
		LIMIT 10;"

inbox-dlq:
	@echo "=== Dead Letter Queue Events ==="
	@docker-compose exec -T image-generator psql $(DATABASE_URL) -c "\
		SELECT id, event_type, retry_count, last_error, created_at \
		FROM inbox_events \
		WHERE processed = true AND last_error LIKE 'FAILED after%' \
		ORDER BY created_at DESC \
		LIMIT 10;"

inbox-consumer-logs:
	docker-compose logs -f inbox-consumer

worker-logs:
	docker-compose logs -f worker

beat-logs:
	docker-compose logs -f beat

run-inbox-consumer:
	python run_inbox_consumer.py
