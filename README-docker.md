# Docker Dev-Stack — PWE (Gate 7.2 / 7.5)

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
| `PWE_DATEI_STORAGE_PFAD` | `/var/pwe/dateien` (Volume `pwe_dateien`) |
| `ENV` | `development` |

Optional für Demo-/Labor-Automatisierung (Gate 6.3c):

```yaml
# in docker-compose.yml unter backend.environment ergänzen:
PWE_DEMO_MODE: "true"
EXTERNES_KOMMANDO_ADAPTER: simulation
```

Default bleibt **ohne** Demo-Antworten (`PWE_DEMO_MODE=false`). Siehe Root-README Demo-Ablauf und `scripts/seed_demo_automatisierung.py`.

**Identity (Gate 8.1a–8.1c1):** Login/Session aktiv; Seed-Administrator optional (`PWE_SEED_ADMIN`, Default aktiv in Dev). Neu angelegte Benutzer erhalten `passwortwechsel_erforderlich=true` — Force-Change erzwingt Passwortänderung vor weiteren API-Aufrufen (Middleware). Identity-Administration nur als **Backend-API** (`/identity/*`); **keine** Admin-UI im Frontend (Gate 8.1c2). Siehe `docs/technical-domain/api.md` § Authentifizierung / Identity.

Schema: ausschließlich über Alembic (Gate 7.5 ✅). `docker compose up` migriert vor dem Backend-Start (`alembic upgrade head` im Entrypoint). Die FastAPI-Runtime erzeugt kein Schema.

**Bestehende Volumes vor 7.5b:** Wenn die DB noch per `create_all` ohne `alembic_version` angelegt wurde, einmalig neu aufsetzen (`docker compose down -v`) oder manuell `alembic stamp head` setzen — sonst schlägt `upgrade` mit „already exists“ fehl.

Details: `docs/datenbankmodell.md` §4, `backend/alembic/README`.

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
docker compose down        # Container stoppen, Volumes bleiben
docker compose down -v     # inkl. PostgreSQL-Daten (pgdata) und Datei-Storage (pwe_dateien)
```

**Backup:** Für vollständige Wiederherstellung müssen PostgreSQL-Volume (`pgdata`) und Datei-Volume (`pwe_dateien`) gemeinsam gesichert werden.

## Bewusst nicht enthalten

- Frontend-Container
- Produktions-Härtung (Secrets, TLS, Resource Limits)
- Automatische Migration *innerhalb* der FastAPI-Runtime (Migration nur Entrypoint/CLI)
- Identity-Administrations-**UI** (Backend API ab Gate 8.1c1 ✅; UI folgt Gate **8.1c2**)

Siehe `docs/roadmap.md` — Gate 8.2–8.4 ✅; Gate 8.1a/8.1b/8.1c1 ✅; nächster Slice **Gate 8.1c2** Identity Administration UI.
