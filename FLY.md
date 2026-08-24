# Fly.io

`fly.toml` only — no `fly launch`, `fly secrets set`, or `fly deploy` run.
Those create or spend real resources and weren't authorized.

## Region

`gru` (São Paulo) — closest Fly region to the trinational border; there
isn't one in southern Brazil/Paraguay/Argentina specifically.

## Health check

`/health` on the internal port (8000, matches the Dockerfile's default —
no `PORT` override needed here since Fly's own default lines up with it).
Stays a plain app-alive check, not a DB check, per the logging phase's
decision — a slow or momentarily-down database shouldn't flip the health
check and cause Fly to cycle machines.

## `CORS_ORIGINS` / `ALLOWED_HOSTS`

Not set in `fly.toml` — they depend on domains that don't exist yet (the
Fly app's own hostname, and wherever Cloudflare Pages ends up serving the
frontend from). Set both for real once those are known:

```
fly secrets set CORS_ORIGINS=https://<cloudflare-pages-domain>
fly secrets set ALLOWED_HOSTS=<fly-app>.fly.dev
```

## Conceptual deploy flow (not run)

```
fly launch                                    # creates the app, doesn't deploy yet
fly secrets set DATABASE_URL=postgresql+psycopg://...    # Neon connection string
fly secrets set CORS_ORIGINS=https://<cloudflare-pages-domain>
fly secrets set ALLOWED_HOSTS=<fly-app>.fly.dev
fly deploy
```

Migrations and data import happen against the Neon database directly
(see `NEON.md`), before or after the first deploy — either order works,
since the app doesn't run migrations on startup itself.

## Budget

~US$50 of credit mentioned as available on the account — a single small
Fly machine for a low-traffic public API is well within that, but actual
spend depends on machine size/count chosen at `fly launch` time, which
wasn't run.