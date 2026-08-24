# Fluida Geo — Backend

FastAPI service exposing the trinational border region's places catalog
(Foz do Iguaçu, Ciudad del Este/Presidente Franco, Puerto Iguazú) as
GeoJSON, for the [Fluida Geo frontend](../fluida-geo-frontend).

## Architecture

```
Cloudflare Pages (React/Vite)
        ↓ HTTPS
Fly.io (this service — FastAPI)
        ↓
Neon PostgreSQL
```

See `FLY.md`, `NEON.md`, `CLOUDFLARE.md` (in the frontend repo) for the
deployment side of each of these.

## Stack

Python 3.12, FastAPI, SQLAlchemy (sync), PostgreSQL via `psycopg`,
Pydantic / pydantic-settings, Alembic, uv, pytest.

Deliberately not used: async SQLAlchemy, PostGIS, Redis, RabbitMQ, a
repository-pattern abstraction layer, authentication. See `SECURITY.md`
for why auth and rate limiting specifically aren't here.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- PostgreSQL 16 (local, or a `DATABASE_URL` pointing at one — see `NEON.md`)

## Setup

```
uv sync
cp .env.example .env    # edit DATABASE_URL if not using the default local one
uv run alembic upgrade head
uv run python -m app.seed                                        # 10 sample places, or:
uv run python scripts/import_places.py path/to/places.geojson    # the real ~200-place catalog
uv run uvicorn app.main:app --reload
```

New database vs. one that already has the schema: see `MIGRATIONS.md`.

## Environment variables

See `.env.example` for the full list with defaults. `DATABASE_URL`,
`CORS_ORIGINS`, `ALLOWED_HOSTS`, `ENABLE_API_DOCS`, `DEBUG` — all
documented in `SECURITY.md` alongside the reasoning for each default.

## Endpoints

- `GET /health` — liveness only, no database check (see the logging
  section below for why)
- `GET /api/places` — GeoJSON `FeatureCollection`; optional
  `country`/`category`/`city` query params, combinable
- `GET /api/places/{id}` — a single GeoJSON `Feature`, 404 if missing

`coordinates` is always `[longitude, latitude]`.

## Importing places

`scripts/import_places.py` reads any GeoJSON `FeatureCollection`,
validates every feature before writing anything, and upserts by `id` —
safe to run repeatedly on the same or an updated file:

```
uv run python scripts/import_places.py path/to/places.geojson
```

`app/seed.py` is separate and stays small on purpose — 10 fixed records
for a zero-dependency dev bootstrap, not a sync of the real catalog.

## Migrations

Alembic. Full flow (new database vs. one with existing data) in
`MIGRATIONS.md`.

## Tests

```
uv run pytest
```

21 tests: API contract (GeoJSON shape, coordinate order, filters, 404),
importer (insert/update/idempotency/validation), health.

## Logging

Startup, unhandled errors (with the real traceback server-side only —
never in the response), and any response with status >= 400 are logged.
Healthy requests aren't, to keep it from being noisy. `/health` checks
the app only, not the database — a slow/unreachable DB shouldn't flip a
platform's health check and cause machine cycling; a separate check
would be the place for that if it's ever needed.

## Docker

```
docker build -t fluida-geo-backend .
```

Not run in this environment (Docker isn't installed here) — see the
Dockerfile's own comments for what was verified without it.

## Structure

```
app/
  api/routes/     — FastAPI routers
  core/           — settings, logging setup
  db/             — engine/session, models
  schemas/        — Pydantic GeoJSON schemas
  services/       — query logic
  seed.py
alembic/          — migrations
scripts/
  import_places.py
tests/
```

## Deploy

Planned: Fly.io (backend, `FLY.md`) + Neon (database, `NEON.md`) + GitHub
Actions CI (`.github/workflows/ci.yml`, validation only, no deploy step
yet). Nothing has been deployed — `fly launch`/`fly deploy` were not run.