FROM python:3.12-slim

# Pinned uv binary, not pip-installed uv — avoids needing pip/build tools
# in the image just to install the installer.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Dependencies copied and installed before app code so this layer only
# rebuilds when pyproject.toml/uv.lock actually change, not on every code
# edit. psycopg[binary] means no compiler is needed here at all.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY scripts ./scripts
RUN uv sync --frozen --no-dev

RUN useradd --create-home --uid 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Shell form so ${PORT} expands — Fly.io (and most platforms) inject PORT
# at runtime; 8000 is only the local-run fallback, never assume Fly's own.
CMD ["sh", "-c", "uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
