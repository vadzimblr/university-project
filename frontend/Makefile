.PHONY: build up down restart logs ps shell clean net dev-up dev-down dev-logs dev-shell

COMPOSE ?= docker compose
SERVICE ?= frontend

build:
	$(COMPOSE) -f docker-compose.yaml build

up:
	$(COMPOSE) -f docker-compose.yaml up -d

down:
	$(COMPOSE) -f docker-compose.yaml down

restart:
	$(COMPOSE) -f docker-compose.yaml down
	$(COMPOSE) -f docker-compose.yaml up -d --build

logs:
	$(COMPOSE) -f docker-compose.yaml logs -f --tail=200 $(SERVICE)

ps:
	$(COMPOSE) -f docker-compose.yaml ps

shell:
	$(COMPOSE) -f docker-compose.yaml exec $(SERVICE) /bin/sh

clean:
	$(COMPOSE) -f docker-compose.yaml down --rmi local --remove-orphans

net:
	docker network create app-net || true

dev-up:
	$(COMPOSE) -f docker-compose.dev.yaml up -d

dev-down:
	$(COMPOSE) -f docker-compose.dev.yaml down

dev-logs:
	$(COMPOSE) -f docker-compose.dev.yaml logs -f --tail=200 frontend-dev

dev-shell:
	$(COMPOSE) -f docker-compose.dev.yaml exec frontend-dev /bin/sh
