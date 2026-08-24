# Database migrations

Schema is managed by Alembic (`alembic/versions/`). `Base.metadata.create_all()`
is no longer used by `app/seed.py` or `scripts/import_places.py` — run
migrations first.

## New database

```
uv run alembic upgrade head
uv run python -m app.seed                              # 10 sample places, or:
uv run python scripts/import_places.py path/to/places.geojson   # the real catalog
```

## Existing database with the schema already present

If `places` already exists (created manually or via the old
`create_all()` bootstrap) and has real data you don't want touched, do
**not** run `upgrade head` — that runs `CREATE TABLE`, which will fail
against an existing table. Tell Alembic the schema is already at the
latest revision instead:

```
uv run alembic stamp head
```

This only writes Alembic's own bookkeeping row — it does not touch
`places` or its data. Used on `fluida_geo` and `fluida_geo_test` here;
confirmed the row count was identical before and after.

## Configuration

`alembic/env.py` reads the connection string from `app.core.config.settings`
(same `DATABASE_URL` as the app), not from `alembic.ini` — no credentials
live in that file.

## Test database

`tests/conftest.py` still uses `Base.metadata.drop_all()` /
`create_all()` directly, not Alembic — deliberate, not an oversight: the
test database is dropped and recreated from scratch on every test
session anyway, so going through migration history there would only add
time without adding confidence. Alembic is for schema that persists
(dev, staging, production); a throwaway test database doesn't need it.
