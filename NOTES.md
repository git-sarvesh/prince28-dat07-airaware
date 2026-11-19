## Day 3 — Postgres Storage, Migrations, and Idempotent Ingestion

### Architecture & Schema Decisions
- **Async Driver & Pooling:** Normalized `DATABASE_URL` to `postgresql+asyncpg://` via `airaware.db.url.to_asyncpg_url` and enabled `pool_pre_ping=True` for Neon Postgres connection resilience.
- **ORM & Naming Conventions:** Configured a shared SQLAlchemy `Base` with deterministic index, unique, check, foreign key, and primary key naming conventions (`ix_`, `uq_`, `ck_`, `fk_`, `pk_`).
- **Tables & Migrations:**
  - `cc17e2451ac1`: Initial schema defining `documents` (with `external_id`, `metadata_` JSONB, `content_hash`, and timestamps) and `pages` (with `ON DELETE CASCADE` foreign key to `documents.id` and unique `(document_id, page_no)`).
  - `069afa2de3a0`: Added GIN index `ix_documents_metadata_gin` on `documents.metadata_` to accelerate JSONB lookups.
  - Verified full `alembic upgrade head`, `alembic downgrade -1`, `alembic downgrade base`, and re-upgrade cycles.
- **Idempotent Loader (`scripts/load_db.py`):** Computes a canonical SHA-256 `content_hash` per record to insert new rows, update changed rows, and skip unchanged rows across repeated runs.
- **FastAPI Integration:** Wired an async `lifespan` context manager in `create_app` to initialize `app.state.engine` and `app.state.sessionmaker`, injected `AsyncSession` via `get_session`, and preserved all Day 1/Day 2 API contracts and error shapes.

### Verification Summary
- **Idempotent Ingestion:** Ran `uv run python scripts/load_db.py` multiple times (`5 inserted` on first run; `5 skipped` on subsequent runs).
- **Live Endpoints:** Verified `200 OK` on `/health`, `/ready` (`{"status":"ready","records":5}`), `/v1/documents`, and `404 Not Found` with `X-Request-Id` on missing IDs.
- **Automated Tests:** Updated `tests/conftest.py` and `tests/test_api.py` (`9 passed`).

## D04 Docker, Compose and tests

### The image
- Image: `airaware-api:latest` (ID `06f604ec93ea`), disk usage `300MB` (content size `70MB`, target under `400MB`)
- User check: `uid=999(app) gid=999(app) groups=999(app)` (non-root `app` user)
- Build caching: multi-stage `Dockerfile` with `uv` caches `uv sync --locked --no-install-project --no-dev` until `pyproject.toml` or `uv.lock` changes; source/app sync layers rebuild quickly on code edits.

### The stack
- Compose services: `airaware-db-1` (`pgvector/pgvector:pg17`, healthy on `5433:5432`), `airaware-redis-1` (`redis:7-alpine`, healthy on `6379:6379`), `airaware-migrate-1` (exited `0`), and `airaware-api-1` (port `8000`).
- Last line of `migrate-1` log (initial load): `records=5 inserted=5 updated=0 unchanged=0` (subsequent run with unchanged data skips new inserts).

### Breaking the database on purpose
- `db` stopped: `/health` returns `200 OK` (`{"status":"ok","service":"airaware","env":"local"}`).
- `db` stopped: `/ready` returns `503` (`{"status":"not_ready","reason":"database unavailable: [Errno -2] Name or service not known"}`).
- `db` started: `/ready` recovers automatically to `200 OK` (`{"status":"ready","records":5}`) without restarting `api`.
- Why load balancers stop sending traffic on `/ready` failure without restarting the app: liveness (`/health`) confirms the process is alive, while readiness (`/ready`) reflects dependency availability so traffic drains away from unhealthy instances without killing a healthy API process during transient DB hiccups.

### Tests and coverage
- `uv run poe test`: `2 passed` (	ests/unit/test_unit.py).
- `uv run poe test-integration`: `7 passed` (	ests/integration/test_api_integration.py with session-scoped fresh database + migrations).
- `uv run poe cov`: `9 passed`, total coverage `73%` (src/airaware/store.py at `0%` and src/airaware/logging_setup.py at `46%` are the lowest-covered modules; `store.py` is unused/legacy in the current path and `logging_setup.py` setup branches are only partially exercised).
