# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

UPAO RAG is a Retrieval-Augmented Generation chatbot for Universidad Privada Antenor Orrego. Users ask questions and get answers grounded in uploaded institutional documents. Flask REST API backend, Angular 18 SPA frontend, Ollama for LLM/embeddings, Qdrant for vector search.

## Development Commands

```bash
# Infrastructure (PostgreSQL + Qdrant in Docker)
make up                # docker compose up -d (PostgreSQL :5433, Qdrant :6333)
make down              # Stop Docker services
make restart           # down + up
make clean             # Remove containers, volumes, images
make shell-db          # psql into PostgreSQL
make logs              # Tail Docker logs
make status            # docker compose ps

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

Seed subcommands: `flask seed run` (all), `flask seed admin`, `flask seed categories`.

Production entry point: `backend/wsgi.py`. Three config environments in `backend/config.py`: development (default), production, test.

## Architecture

### Database Layer — No ORM

All database access uses raw SQL via psycopg2 + PostgreSQL stored functions. There is no SQLAlchemy or any ORM.

- **`postgresql/tables.sql`** — 7 tables (users, categories, documents, document_chunks, chat_history, feedbacks, thesis_checks) with indexes, triggers for auto-updating `updated_at`, UUID primary keys as `VARCHAR(36)`
- **`postgresql/procedures.sql`** — ~35 stored functions named `fn_*` (e.g., `fn_create_user`, `fn_list_documents`, `fn_upsert_feedback`, `fn_get_dashboard_stats`, `fn_create_thesis_check`, `fn_update_thesis_check_status`)
- **`app/db.py`** — ThreadedConnectionPool (min=2, max=10) with RealDictCursor. Query helpers:
  - `call_fn(fn_name, params, fetch_one/fetch_all, conn)` — calls `SELECT * FROM fn_name(params...)`
  - `execute(query, params, fetch_one/fetch_all, conn)` — raw SQL
  - `get_conn()` — stores connection in Flask `g`, auto-returned on teardown; connections use `autocommit=False` with explicit `conn.commit()`
  - `get_conn_raw()` / `put_conn_raw()` — for background threads that don't have Flask `g`
- **`app/utils/formatters.py`** — Converts row dicts to API response dicts (format_user, format_document, format_category, format_chat_message, format_feedback, format_thesis_check)

Paginated queries use `COUNT(*) OVER()` in the stored function. If no rows, the list is empty and total=0 (handled in Python: `rows[0]['total_count'] if rows else 0`). Pagination hard cap: `per_page` max 100.

JSONB columns require `psycopg2.extras.Json()` wrapper when passing dicts/lists.

### Backend (`backend/`)

Flask app factory in `app/__init__.py`. Entry point: `run.py` (loads `.env` from project root via explicit path). `strict_slashes=False` on `app.url_map` to prevent 308 redirects.

**API blueprints** under `app/api/` — all prefixed `/api/v1/`:
- `auth/` — register (restricted to @upao.edu.pe), login, refresh, logout, /me
- `chat/` — POST `/message` (non-streaming), POST `/stream` (SSE), conversations CRUD, feedback
- `documents/` — upload single + batch (`POST /upload`, `POST /upload-batch`, triggers background processing), list/get/update/delete, reprocess
- `categories/` — CRUD with slug generation
- `users/` — admin-only user management
- `analytics/` — dashboard stats, daily usage, popular queries, feedback summary
- `config_rag/` — runtime RAG parameter tuning (in-memory overrides); URL prefix `/api/v1/config/rag`
- `originality/` — admin-only thesis originality check: submit file, list/get/delete checks
- `health` endpoint at `/api/v1/health`

**Response format**: Success responses return `{ success: bool, message: str, data: any }`. Error responses return `{ success: false, message: str, error: str }`. Paginated endpoints add `{ pagination: { total, page, per_page, pages } }`. Helpers in `app/utils/response.py`. All user-facing messages are in Spanish.

**Auth**: JWT via Flask-JWT-Extended. Bearer token in Authorization header. Access tokens expire in 1h, refresh in 30d. Two decorators in `app/middleware/`:
- `@auth_required` — validates JWT, fetches user from DB via `fn_get_user_by_id`, checks `is_active` flag
- `@role_required('admin')` — same checks plus role verification; inactive accounts get 403

**Schemas**: Plain `marshmallow.Schema` (not Flask-Marshmallow) for input validation only. No serialization of DB results — formatters handle that.

### RAG Pipeline

Document processing runs in a **background thread** via `threading.Thread` (in `documents/routes.py`). The thread:
- Captures `current_app._get_current_object()` before spawning to preserve app context
- Uses `get_conn_raw()`/`put_conn_raw()` with try/finally since Flask `g` isn't available

**Processing flow** (`app/rag/pipeline.py`):
1. Extract text — factory pattern in `app/document_processing/processor.py` dispatches to PdfProcessor (pdfplumber + PyPDF2 fallback), DocxProcessor, ExcelProcessor, TxtProcessor, ImageProcessor (pytesseract OCR)
2. Auto-categorize if no category supplied — `app/rag/categorizer.py` calls `gemma3:4b` (temp=0.0) to classify the document into an existing category; returns `None` silently on failure
3. Chunk text — `RecursiveCharacterTextSplitter` (1000 chars, 200 overlap) via `app/document_processing/chunker.py`
4. Embed via `nomic-embed-text` (768 dims) through Ollama → store vectors in Qdrant collection `upao_documents` (cosine distance, batch upsert of 100)
5. Save chunks in PostgreSQL via `fn_create_chunk`
6. Update document status (`processing` → `completed` or `failed`) and category document count

**Query flow** (`app/rag/chain.py`):
1. Embed question → **two-stage retrieval** via `app/rag/reranker.py` (`two_stage_retrieve`):
   - Stage 1: wide candidate generation — `candidate_k = min(top_k * RAG_CANDIDATE_MULTIPLIER, 40)` with a lowered threshold (`score_threshold * RAG_CANDIDATE_THRESHOLD_FACTOR`, floor 0.20)
   - Stage 2: diversity-aware selection — iterate candidates (sorted by score DESC), accept a chunk only if `doc_counts[document_id] < RAG_MAX_CHUNKS_PER_DOC`; stop when `len(final) == top_k`
2. Deduplicate sources by `{document_id}_{page}` key (`app/rag/retriever.py`) — each source includes score (3 decimals) and 150-char preview. Last 6 conversation messages fetched from DB and included as history context.
3. **Optional Self-RAG reflection** (when `RAG_ENABLE_REFLECTION=true`): `_check_relevance()` uses `reflection_prompt` to classify context as `SUFICIENTE`/`PARCIAL`/`INSUFICIENTE`. If `INSUFICIENTE`, or if no context was retrieved at all, `_generate_suggestions()` responds with suggested questions instead.
4. Build prompt with context (`app/rag/prompts.py` — Spanish, strict grounding instructions, cites sources only)
5. Invoke `gemma3:4b` via ChatOllama — either blocking or streaming
6. SSE streaming yields `{type: 'sources'}` first, then `{type: 'token'}` chunks, then `{type: 'done', conversation_id, message_id}`. Full response is accumulated in-memory before the final DB save.

**Embeddings**: Singleton pattern — `_embeddings_instance` caches OllamaEmbeddings globally. `ensure_collection()` creates the Qdrant collection if missing.

**Originality check flow** (`app/rag/originality.py`):
1. Extract text and chunk the uploaded thesis file (reuses the same processor/chunker as document ingestion; min chunk length 50 chars)
2. Embed all chunks in batches of 32 via `nomic-embed-text`
3. For each chunk, query Qdrant (`fn_search_similar`) with `top_k_per_chunk=3` and a fixed `0.35` baseline threshold
4. A chunk is "flagged" if its top result score ≥ the user-supplied `score_threshold` (default `0.70`)
5. Compute `originality_score = 100 - (flagged_chunks / total_chunks * 100)`; derive `plagiarism_level` (low/moderate/high/very_high)
6. Aggregate per-document stats (max/avg score, pages hit, similarity %) keeping top-20 matched documents
7. Run LLM analysis (`gemma3:4b`, temp=0.1) on the top-5 high-similarity documents to identify common themes, methods, and overlap — result stored in `matches_summary` JSONB column
8. Update `thesis_checks` record via `fn_update_thesis_check_status`; runs in a background thread using `get_conn_raw()`/`put_conn_raw()`

### Frontend (`frontend/`)

Angular 18 with standalone components, signals for state, functional guards and interceptors.

**Routing** (`app.routes.ts`) — all lazy-loaded:
- `/login`, `/register` — `noAuthGuard` (redirect if already logged in)
- `/chat` — main interface, `authGuard`
- `/admin/**` — dashboard, documents, categories, users, RAG config, test chat, originality — `authGuard` + `roleGuard`
- `/profile` — `authGuard`
- `/` redirects to `/chat`

**Chat streaming**: Uses the **fetch API with async generators** (NOT Angular HttpClient) for SSE streaming. See `features/chat/services/chat.service.ts`. Parses `data: {json}\n\n` SSE format manually.

**Auth state**: `core/services/auth.service.ts` uses Angular signals (`currentUser`, computed `isAuthenticated`, `isAdmin`). `authService.ready` is a `Promise<void>` awaited by guards before checking auth state. Token stored in localStorage via `core/services/token.service.ts`.

**Error interceptor** (`core/interceptors/error.interceptor.ts`): Handles global 401s with BehaviorSubject-based token refresh queuing to prevent duplicate refresh calls. Skip URLs: `/auth/login`, `/auth/register`, `/auth/refresh`, `/auth/logout`.

**Styling**: Tailwind CSS with UPAO brand colors defined in `tailwind.config.js` (primary: `#1E3A5F`, secondary: `#C8102E`).

**Originality**: `features/admin/services/originality.service.ts` uses standard `HttpClient` (not fetch/SSE). The `ThesisCheck` model is defined in `core/models/document.model.ts`. Accepted file types: PDF, DOCX, TXT (subset of document upload types).

**Proxy**: `proxy.conf.json` forwards `/api` → `http://localhost:5050`. Frontend environment uses `/api/v1` as `apiUrl`.

### Infrastructure

**Docker Compose** (`docker-compose.yml`): `timescale/timescaledb-ha:pg16` on port 5433, Qdrant on ports 6333/6334. SQL files mounted to `/docker-entrypoint-initdb.d/` for auto-initialization. Qdrant config at `docker/qdrant/config.yaml`.

**Environment**: `.env` at project root (see `.env.example`). `run.py` loads it via explicit path. `DATABASE_URL` used directly if set; otherwise built from individual `POSTGRES_*` vars.

**RAG defaults** (overridable via `.env` and `config_rag/` API at runtime): `top_k=5`, `score_threshold=0.35`, `temperature=0.3`, `num_ctx=4096`, `chunk_size=1000`, `chunk_overlap=200`. Two-stage reranker vars (`.env` only): `RAG_CANDIDATE_MULTIPLIER=4`, `RAG_CANDIDATE_THRESHOLD_FACTOR=0.70`, `RAG_MAX_CHUNKS_PER_DOC=2`. Self-RAG flag: `RAG_ENABLE_REFLECTION=false`. Runtime overrides via `config_rag/` are stored **in-memory only** and lost on process restart.

**Originality defaults** (`.env` only, no runtime API): `ORIGINALITY_PLAGIARISM_THRESHOLD=0.70`, `ORIGINALITY_TOP_K_PER_CHUNK=3`, `ORIGINALITY_MAX_LLM_DOCS=5`, `ORIGINALITY_MIN_SIM_FOR_LLM=5.0`.

**`postgresql/vectorizer.sql`**: Placeholder only — `ai.create_vectorizer` is not available in the current `timescale/timescaledb-ha:pg16` image. Embeddings are generated in Python via OllamaEmbeddings and stored directly in `document_chunks`.

**No test infrastructure** exists in this project (no pytest, no Angular test specs active).

### Debugging Utilities

**`scripts/query_db.py`** — CLI tool to run SQL directly against PostgreSQL (reads credentials from `.env`):
```bash
python scripts/query_db.py -q "SELECT * FROM users LIMIT 5"
python scripts/query_db.py -q "SELECT * FROM fn_list_documents(NULL,NULL,1,10)"
python scripts/query_db.py -f scripts/my_query.sql
python scripts/query_db.py -q "SELECT * FROM users WHERE role = %s" -p admin
```

**`scripts/reset_documents.py`** — Wipes all documents and associated data (chunks, vectors, DB records) and resets category document counts to 0. Also deletes physical files. Use to reset to a clean state during development.

## Conventions

- All DB operations use `call_fn()` for stored functions or `execute()` for raw SQL — never raw ORM
- Background threads use `get_conn_raw()`/`put_conn_raw()` with try/finally and capture `current_app._get_current_object()` before spawning
- JSONB columns require `psycopg2.extras.Json()` wrapper
- Backend success responses: `{success, message, data}`; error responses: `{success, message, error}`
- Angular components are standalone (no NgModules), state via signals (not BehaviorSubjects)
- All database tables use UUID primary keys (`VARCHAR(36)`) with timestamps
- User registration restricted to `@upao.edu.pe` email domain
- Admin user created via `flask seed run`, not registration
- File uploads stored with UUID-based filenames; `ALLOWED_EXTENSIONS = {pdf, docx, xlsx, xls}` (defined in `config.py`); max size controlled by `MAX_UPLOAD_SIZE_MB` env var (default 80MB)
- Originality check uploads accept only {pdf, docx, txt}; use the same `save_upload` utility
- Adding a new stored function: add to `postgresql/procedures.sql`, re-run `make init-db` (uses `CREATE OR REPLACE`)
- Adding a new table: add to `postgresql/tables.sql` with `CREATE TABLE IF NOT EXISTS`, re-run `make init-db`
