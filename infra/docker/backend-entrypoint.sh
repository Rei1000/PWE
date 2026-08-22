#!/bin/sh
# Gate 7.5b: Migration außerhalb der FastAPI-Runtime, dann App-Start.
set -e
cd /app/backend
alembic upgrade head
exec uvicorn api.app:create_app --factory --host 0.0.0.0 --port 8000
