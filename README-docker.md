# Docker Dev-Stack — PWE (Gate 7.2)

Reproduzierbarer lokaler Start von **FastAPI + PostgreSQL** mit persistenter Datenbank.

## Enthalten

| Service | Port | Zweck |
|---------|------|-------|
| `backend` | 8000 | PWE-API mit PostgreSQL ([ADR-0011](docs/adr/0011-api-postgresql-unit-of-work.md)) |
| `db` | 5432 | PostgreSQL 15 |

Das Frontend läuft **nicht** im Container — weiterhin separat via `npm run dev` (Proxy → `:8000`).

## Voraussetzungen

- Docker mit Compose v2 (`docker compose`)

## Start

```bash
docker compose up --build
```

API erreichbar unter http://localhost:8000 — Health: `GET /health`.

Die API startet erst, wenn PostgreSQL healthy ist (`depends_on` + Healthcheck).

## Umgebung

| Variable | Wert im Compose-Stack |
|----------|------------------------|
| `DATABASE_URL` | `postgresql+psycopg://postgres:postgres@db:5432/app` |
| `ENV` | `development` |

Schema wird beim API-Start via `init_schema` angelegt (kein Alembic in diesem Slice).

## Frontend anbinden

```bash
# Terminal 1 — Stack
docker compose up --build

# Terminal 2 — Frontend
cd frontend/web && npm install && npm run dev
```

Öffnen: http://localhost:5173 (Dev-Proxy leitet `/api` an `:8000` weiter).

## Stoppen / Daten

```bash
docker compose down        # Container stoppen, Volume bleibt
docker compose down -v     # inkl. PostgreSQL-Daten (pgdata)
```

## Bewusst nicht enthalten

- Frontend-Container
- Alembic / Migrations
- Produktions-Härtung (Secrets, TLS, Resource Limits)
- Auth / Identity

Siehe `docs/roadmap.md` Gate 7.2 und folgende Gates.
