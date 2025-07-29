.PHONY: build up down restart logs lint test

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

lint:
	black app/ tests/
	isort app/ tests/

test:
	pytest tests/

enter:
	docker-compose run --rm scene_splitter bash