# Neon PostgreSQL

Not set up yet — this documents the flow, no Neon account or project was
created (that's an external action outside this repo's scope).

## Why no code change was needed

`app/db/session.py` builds its engine straight from `DATABASE_URL`
(`create_engine(settings.database_url)`), with nothing else hardcoded.
Neon's own connection strings already carry `sslmode=require` as a query
parameter, and `psycopg` (the driver in use) reads that directly from the
URL — so a Neon URL works here without touching this code, provided the
URL is used as Neon gives it, `sslmode` included.

## Setup flow

1. Create a Neon project and database (neon.tech).
2. Copy the connection string it gives you — keep `sslmode=require` in it.
3. Set it as `DATABASE_URL` (locally in `.env`, or as a secret on
   whatever platform runs this — never commit it):
   ```
   DATABASE_URL=postgresql+psycopg://user:password@ep-example-123456.us-east-2.aws.neon.tech/fluida_geo?sslmode=require
   ```
4. Run migrations against it:
   ```
   uv run alembic upgrade head
   ```
5. Load data:
   ```
   uv run python scripts/import_places.py path/to/places.geojson
   ```

## Notes

- Neon's free tier can pause an idle database; the first request after a
  pause takes longer while it resumes. Nothing to configure for this —
  SQLAlchemy's connection just waits for it.
- No pooler-specific configuration added (e.g., Neon's PgBouncer pooled
  connection string) — not needed at this traffic level, and adding it
  without a real need would be exactly the kind of premature complexity
  this project has been avoiding elsewhere.