# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

UPAO RAG is a Retrieval-Augmented Generation chatbot for Universidad Privada Antenor Orrego. Users ask questions and get answers grounded in uploaded institutional documents. It has a Flask REST API backend, an Angular 18 SPA frontend, and uses Ollama for LLM/embeddings + Qdrant for vector search.

## Development Setup

Infrastructure (PostgreSQL + Qdrant) runs in Docker. Backend and frontend run locally on the host.

```bash
# 1. Start infrastructure
make up                # docker compose up -d (PostgreSQL on :5433, Qdrant on :6333)

# 2. Start backend (Flask on :5050)
make run-backend       # cd backend && python run.py

# 3. Start frontend (Angular on :4200, proxies /api to :5050)
make run-frontend      # cd frontend && npx ng serve --proxy-config proxy.conf.json
```

### Database Commands
```bash
make migrate                      # flask db upgrade
make migrate-create msg="desc"    # flask db migrate -m "desc"
make seed                         # flask seed run (admin + categories)
make shell-db                     # psql into PostgreSQL
```

### Other Make Targets
```bash
make down          # Stop Docker services
make logs          # Tail Docker logs
make status        # docker compose ps
make clean         # Remove containers, volumes, images
make build-frontend  # ng build (production)
```

## Architecture

### Backend (`backend/`)

Flask app factory in `app/__init__.py`. Entry point: `run.py` (loads `.env` from project root via explicit path).

**API blueprints** under `app/api/` — all prefixed `/api/v1/`:
- `auth/` — register (restricted to @upao.edu.pe), login, token refresh
- `chat/` — send message, SSE streaming, conversation history
- `documents/` — upload (PDF, DOCX, XLSX, TXT, images), list, delete
- `categories/` — CRUD for document categories
- `users/` — user management (admin)
- `analytics/` — usage statistics
- `config_rag/` — RAG parameter tuning
- `health` endpoint at `/api/v1/health`

**Standard response format**: `{ success: bool, message: str, data: any }`

**Auth**: JWT via Flask-JWT-Extended. Bearer token in Authorization header. Access tokens expire in 1h, refresh in 30d. Role-based access via `role_required` decorator.

**RAG pipeline** (`app/rag/`):
1. Documents are processed (`app/document_processing/`) → chunked (1000 chars, 200 overlap)
2. Chunks embedded via `nomic-embed-text` (768 dims) through Ollama
3. Vectors stored in Qdrant collection `upao_documents` (cosine distance)
4. On query: embed question → retrieve top-k similar chunks → build prompt → stream response from `gemma3:4b` via Ollama
5. Streaming uses SSE with `{type, content}` and `{type, sources}` events

**Models** (`app/models/`): All use UUID primary keys. Tables: users, documents, chunks, categories, chat_history, feedback.

**Schemas** (`app/schemas/`): Marshmallow for serialization/validation.

**Extensions** (`app/extensions.py`): db (SQLAlchemy), migrate, jwt, cors, ma (Marshmallow).

**Seeds** (`app/seeds/`): CLI commands — `flask seed run` creates admin user and default categories.

### Frontend (`frontend/`)

Angular 18 with standalone components, signals for state, functional guards and interceptors.

**Routing** (`app.routes.ts`):
- `/login`, `/register` — protected by `noAuthGuard` (redirect if logged in)
- `/chat` — main interface, `authGuard` required
- `/admin` — dashboard, `authGuard` + `roleGuard` (admin only)
- `/profile` — user profile, `authGuard` required
- `/` redirects to `/chat`

**Core** (`core/`):
- `services/auth.service.ts` — login, register, token management
- `services/token.service.ts` — JWT storage in localStorage
- `guards/` — functional guards (auth, no-auth, role)
- `interceptors/` — auth token injection, global error handling

**Chat streaming**: Uses the fetch API with async generators (NOT HttpClient) for SSE streaming from the backend.

**Styling**: Tailwind CSS with UPAO brand colors (primary: `#1E3A5F`, secondary: `#C8102E`) defined in `tailwind.config.js`.

**Proxy**: `proxy.conf.json` forwards `/api` requests to `http://localhost:5050` during development.

### Infrastructure

**Docker Compose** runs only PostgreSQL and Qdrant:
- PostgreSQL 16-alpine on port 5433 (maps to internal 5432)
- Qdrant on ports 6333 (HTTP) and 6334 (gRPC)
- Init script: `docker/postgres/init.sql` (enables uuid-ossp, pgcrypto)
- Qdrant config: `docker/qdrant/config.yaml`

### Environment

`.env` at project root. `run.py` loads it with an explicit path so it works when running from `backend/`. Key variables:
- `DATABASE_URL` — if set, used directly; otherwise built from `POSTGRES_*` vars
- `POSTGRES_HOST=localhost`, `POSTGRES_PORT=5433` — local defaults
- `OLLAMA_BASE_URL=http://localhost:11434`
- `QDRANT_HOST=localhost`, `QDRANT_PORT=6333`

## Conventions

- Backend responses always use `{success, message, data}` shape
- Angular components are standalone (no NgModules)
- State managed via Angular signals, not RxJS BehaviorSubjects
- All database models use UUID primary keys with timestamps
- User registration restricted to `@upao.edu.pe` email domain
- Admin user created via seed, not registration
