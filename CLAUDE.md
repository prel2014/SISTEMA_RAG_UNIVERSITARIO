# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

UPAO RAG is a Retrieval-Augmented Generation chatbot for Universidad Privada Antenor Orrego. Users ask questions and get answers grounded in uploaded institutional documents. Flask REST API backend, Angular 18 SPA frontend, Ollama for LLM/embeddings, Qdrant for vector search.

## Development Commands

```bash
# Infrastructure (PostgreSQL + Qdrant in Docker)
make up                # docker compose up -d (PostgreSQL :5433, Qdrant :6333)
make down              # Stop Docker services
make clean             # Remove containers, volumes, images
make shell-db          # psql into PostgreSQL
make logs              # Tail Docker logs

# Database
make init-db           # python backend/init_db.py (runs tables.sql + procedures.sql)
make seed              # flask seed run (admin + categories)

# Backend (Flask on :5050)
make run-backend       # cd backend && python run.py

# Frontend (Angular on :4200, proxies /api to :5050)
make run-frontend      # cd frontend && npx ng serve --proxy-config proxy.conf.json
make build-frontend    # ng build (production)
```

First-time setup: `make up` → `make init-db` → `make seed` → `make run-backend` + `make run-frontend`

After `make clean`: Docker auto-runs the mounted SQL files on first PostgreSQL init, but `make init-db` can re-run them manually.

## Architecture

### Database Layer — No ORM

All database access uses raw SQL via psycopg2 + PostgreSQL stored functions. There is no SQLAlchemy or any ORM.

- **`postgresql/tables.sql`** — 6 tables (users, categories, documents, document_chunks, chat_history, feedbacks) with indexes, triggers for auto-updating `updated_at`, UUID primary keys as `VARCHAR(36)`
- **`postgresql/procedures.sql`** — ~30 stored functions named `fn_*` (e.g., `fn_create_user`, `fn_list_documents`, `fn_upsert_feedback`, `fn_get_dashboard_stats`)
- **`app/db.py`** — Connection pool and query helpers:
  - `call_fn(fn_name, params, fetch_one/fetch_all, conn)` — calls `SELECT * FROM fn_name(params...)`
  - `execute(query, params, fetch_one/fetch_all, conn)` — raw SQL
  - `get_conn()` — stores connection in Flask `g`, auto-returned on teardown
  - `get_conn_raw()` / `put_conn_raw()` — for background threads that don't have Flask `g`
- **`app/utils/formatters.py`** — Converts row dicts to API response dicts (format_user, format_document, format_category, format_chat_message, format_feedback)

Paginated queries use `COUNT(*) OVER()` in the stored function. If no rows, the list is empty and total=0 (handled in Python: `rows[0]['total_count'] if rows else 0`).

JSONB columns require `psycopg2.extras.Json()` wrapper when passing dicts/lists.

### Backend (`backend/`)

Flask app factory in `app/__init__.py`. Entry point: `run.py` (loads `.env` from project root via explicit path). `strict_slashes=False` on `app.url_map` to prevent 308 redirects.

**API blueprints** under `app/api/` — all prefixed `/api/v1/`:
- `auth/` — register (restricted to @upao.edu.pe), login, refresh, logout, /me
- `chat/` — POST `/message` (non-streaming), POST `/stream` (SSE), conversations CRUD, feedback
- `documents/` — upload (triggers background processing), list/get/update/delete, reprocess
- `categories/` — CRUD with slug generation
- `users/` — admin-only user management
- `analytics/` — dashboard stats, daily usage, popular queries, feedback summary
- `config_rag/` — runtime RAG parameter tuning (in-memory overrides)
- `health` endpoint at `/api/v1/health`

**Response format**: All endpoints return `{ success: bool, message: str, data: any }`. Paginated endpoints add `{ pagination: { total, page, per_page, pages } }`. Helpers in `app/utils/response.py`.

**Auth**: JWT via Flask-JWT-Extended. Bearer token in Authorization header. Access tokens expire in 1h, refresh in 30d. Two decorators: `@auth_required` (any authenticated user), `@role_required('admin')` (admin only).

**Schemas**: Plain `marshmallow.Schema` (not Flask-Marshmallow) for input validation only. No serialization of DB results — formatters handle that.

### RAG Pipeline

Document processing runs in a **background thread** via `threading.Thread` (in `documents/routes.py`). The thread uses `get_conn_raw()`/`put_conn_raw()` since Flask `g` isn't available.

**Processing flow** (`app/rag/pipeline.py`):
1. Extract text — factory pattern in `app/document_processing/processor.py` dispatches to PdfProcessor (pdfplumber + PyPDF2 fallback), DocxProcessor, ExcelProcessor, TxtProcessor, ImageProcessor (pytesseract OCR)
2. Chunk text — `RecursiveCharacterTextSplitter` (1000 chars, 200 overlap) via `app/document_processing/chunker.py`
3. Embed via `nomic-embed-text` (768 dims) through Ollama → store vectors in Qdrant collection `upao_documents` (cosine distance, batch upsert of 100)
4. Save chunks in PostgreSQL via `fn_create_chunk`
5. Update document status and category document count

**Query flow** (`app/rag/chain.py`):
1. Embed question → Qdrant similarity search (top-k, score threshold, optional category filter)
2. Deduplicate sources by document_id + page (`app/rag/retriever.py`)
3. Build prompt with context (`app/rag/prompts.py` — Spanish, strict grounding instructions)
4. Invoke `gemma3:4b` via ChatOllama — either blocking or streaming
5. SSE streaming yields `{type: 'sources'}`, then `{type: 'token'}` chunks, then `{type: 'done'}`

### Frontend (`frontend/`)

Angular 18 with standalone components, signals for state, functional guards and interceptors.

**Routing** (`app.routes.ts`) — all lazy-loaded:
- `/login`, `/register` — `noAuthGuard` (redirect if already logged in)
- `/chat` — main interface, `authGuard`
- `/admin/**` — dashboard, documents, categories, users, RAG config, test chat — `authGuard` + `roleGuard`
- `/profile` — `authGuard`
- `/` redirects to `/chat`

**Chat streaming**: Uses the **fetch API with async generators** (NOT Angular HttpClient) for SSE streaming. See `features/chat/services/chat.service.ts`.

**Auth state**: `core/services/auth.service.ts` uses Angular signals (`currentUser`, `isAuthenticated`, `isAdmin`). Token stored in localStorage via `core/services/token.service.ts`.

**Styling**: Tailwind CSS with UPAO brand colors defined in `tailwind.config.js` (primary: `#1E3A5F`, secondary: `#C8102E`).

**Proxy**: `proxy.conf.json` forwards `/api` → `http://localhost:5050`. Frontend environment uses `/api/v1` as `apiUrl`.

### Infrastructure

**Docker Compose** (`docker-compose.yml`): PostgreSQL 16-alpine on port 5433, Qdrant on ports 6333/6334. SQL files mounted to `/docker-entrypoint-initdb.d/` for auto-initialization. Qdrant config at `docker/qdrant/config.yaml`.

**Environment**: `.env` at project root (see `.env.example`). `run.py` loads it via explicit path. `DATABASE_URL` used directly if set; otherwise built from individual `POSTGRES_*` vars.

## Conventions

- All DB operations use `call_fn()` for stored functions or `execute()` for raw SQL — never raw ORM
- Background threads use `get_conn_raw()`/`put_conn_raw()` with try/finally — never Flask `g`
- JSONB columns require `psycopg2.extras.Json()` wrapper
- Backend responses always follow `{success, message, data}` shape
- Angular components are standalone (no NgModules), state via signals (not BehaviorSubjects)
- All database tables use UUID primary keys (`VARCHAR(36)`) with timestamps
- User registration restricted to `@upao.edu.pe` email domain
- Admin user created via `flask seed run`, not registration
- Adding a new stored function: add to `postgresql/procedures.sql`, re-run `make init-db` (uses `CREATE OR REPLACE`)
- Adding a new table: add to `postgresql/tables.sql` with `CREATE TABLE IF NOT EXISTS`, re-run `make init-db`
