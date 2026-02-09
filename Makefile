.PHONY: up down restart logs clean status shell-db init-db

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

# Database
init-db:
	cd backend && python init_db.py

# Backend (local)
run-backend:
	cd backend && python run.py

seed:
	cd backend && flask seed run

# Frontend (local)
run-frontend:
	cd frontend && npx ng serve --proxy-config proxy.conf.json

build-frontend:
	cd frontend && npx ng build
