.PHONY: up down restart logs clean status shell-db

# Docker (infrastructure only: PostgreSQL + Qdrant)
up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

status:
	docker compose ps

shell-db:
	docker compose exec postgresql psql -U upao_user -d upao_rag

clean:
	docker compose down -v --rmi local
	docker volume prune -f

# Backend (local)
run-backend:
	cd backend && python run.py

migrate:
	cd backend && flask db upgrade

migrate-create:
	cd backend && flask db migrate -m "$(msg)"

seed:
	cd backend && flask seed run

# Frontend (local)
run-frontend:
	cd frontend && npx ng serve --proxy-config proxy.conf.json

build-frontend:
	cd frontend && npx ng build
