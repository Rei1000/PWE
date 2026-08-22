FROM python:3.11-slim

WORKDIR /app/backend

COPY backend/pyproject.toml .
COPY backend/src ./src
COPY backend/alembic.ini .
COPY backend/alembic ./alembic
COPY infra/docker/backend-entrypoint.sh /entrypoint.sh

RUN pip install --no-cache-dir ".[persistence,pdf,api]" \
    && chmod +x /entrypoint.sh

ENV PYTHONPATH=/app/backend/src

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
