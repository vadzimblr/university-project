run:
	docker compose up -d --remove-orphans

run-attached:
	docker compose up --remove-orphans

down:
	docker compose down

rebuild:
	docker compose down
	docker compose rm -f
	docker image rm comfyui:latest || true
	docker builder prune -af
	docker compose build --no-cache
	docker compose up -d
