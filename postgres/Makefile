.PHONY: up down restart logs ps connect createdb dropdb backup restore

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart postgres

logs:
	docker-compose logs -f postgres

ps:
	docker-compose ps

connect:
	docker-compose exec postgres psql -U $(shell grep POSTGRES_USER .env | cut -d '=' -f2) -d $(shell grep POSTGRES_DB .env | cut -d '=' -f2)

connect-admin:
	docker-compose exec postgres psql -U postgres

createdb:
	@read -p "Enter database name: " dbname; \
	docker-compose exec postgres createdb -U $(shell grep POSTGRES_USER .env | cut -d '=' -f2) $$dbname

dropdb:
	@read -p "Enter database name to drop: " dbname; \
	docker-compose exec postgres dropdb -U $(shell grep POSTGRES_USER .env | cut -d '=' -f2) $$dbname

listdb:
	docker-compose exec postgres psql -U $(shell grep POSTGRES_USER .env | cut -d '=' -f2) -c "\l"

dbsize:
	docker-compose exec postgres psql -U $(shell grep POSTGRES_USER .env | cut -d '=' -f2) -d $(shell grep POSTGRES_DB .env | cut -d '=' -f2) -c "SELECT pg_size_pretty(pg_database_size('$(shell grep POSTGRES_DB .env | cut -d '=' -f2)'));"

backup:
	@read -p "Enter backup filename (without extension): " filename; \
	docker-compose exec postgres pg_dump -U $(shell grep POSTGRES_USER .env | cut -d '=' -f2) $(shell grep POSTGRES_DB .env | cut -d '=' -f2) > $$filename.sql

restore:
	@read -p "Enter backup filename: " filename; \
	docker-compose exec -T postgres psql -U $(shell grep POSTGRES_USER .env | cut -d '=' -f2) $(shell grep POSTGRES_DB .env | cut -d '=' -f2) < $$filename

processes:
	docker-compose exec postgres psql -U $(shell grep POSTGRES_USER .env | cut -d '=' -f2) -d $(shell grep POSTGRES_DB .env | cut -d '=' -f2) -c "SELECT * FROM pg_stat_activity;"

stats:
	docker-compose exec postgres psql -U $(shell grep POSTGRES_USER .env | cut -d '=' -f2) -d $(shell grep POSTGRES_DB .env | cut -d '=' -f2) -c "SELECT schemaname,tablename,n_tup_ins,n_tup_upd,n_tup_del FROM pg_stat_user_tables;" 