# Security posture

The API is read-only for external users (GET endpoints only, no writes,
no auth). This document reflects that: pragmatic hardening for a public
catalog, not the checklist for a system with user accounts.

## Configured

- **CORS**: explicit origin list via `CORS_ORIGINS` (comma-separated),
  never a wildcard. `allow_credentials=False` — no cookies/auth headers
  are involved, so there's nothing for credentialed CORS to protect.
- **TrustedHostMiddleware**: `ALLOWED_HOSTS`, comma-separated, defaults
  to `*` for local dev. Set to the real domain in production.
- **Security headers** on every response: `X-Content-Type-Options`,
  `Referrer-Policy`, `X-Frame-Options`, `Permissions-Policy`. No CSP —
  this is a JSON API with no HTML to protect; a CSP header here would be
  guesswork about a frontend this repo doesn't render.
- **Errors**: unhandled exceptions are caught, logged with the real
  traceback server-side, and returned to the client as a bare
  `{"detail": "Internal server error"}` — no traceback, SQL, or
  `DATABASE_URL` ever reaches the response. `debug=False` by default
  (`DEBUG` env var) — Starlette's debug mode is what would otherwise leak
  tracebacks into responses.
- **Input**: `country`/`category` query params are `Literal[...]` types
  now, not bare `str` — FastAPI rejects invalid values with 422 before
  they reach the database layer, verified for real (`?country=XX` → 422,
  `?country=BR` → 200). Every query already went through SQLAlchemy's
  `select().where(...)`, which parameterizes — no string-built SQL
  anywhere in this codebase to begin with.
- **Docs**: `ENABLE_API_DOCS` (default `true`) controls `/docs`, `/redoc`,
  `/openapi.json`. No strong reason found to default it off — verified
  setting it `false` actually 404s those routes.
- **Secrets**: `.env` is gitignored; `.env.example` holds only placeholder
  values. `DATABASE_URL` and everything else come from real environment
  variables in every environment beyond local dev (Fly secrets, etc.).

## Deliberately not done

**Rate limiting**: not implemented. An in-process/in-memory limiter would
be actively misleading here — Fly.io can and does run multiple instances,
and an in-memory counter only sees requests that happen to land on the
same instance, so it wouldn't actually bound abuse across the deployment.
The right layer for this is the edge/infrastructure (Cloudflare in front
of Fly, or Fly's own request limits) once there's a real traffic pattern
to size it against, not a fragile approximation shipped now to satisfy a
checklist item.

**Auth/JWT/login**: not implemented, not needed — there is no admin
panel or write path this would protect.
