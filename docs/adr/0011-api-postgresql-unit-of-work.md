# ADR-0011: Request-scoped Unit of Work für API ↔ PostgreSQL

## Status

Angenommen (Gate 7.1)

## Kontext

Gate 7.0 führte `PrueflaufAbschlussPersistenz` ein — atomarer Abschluss ohne globales Unit of Work (ADR-0010). Die PostgreSQL-Adapter committeten bis dahin pro Repository-Aufruf.

Gate 7.1 soll die FastAPI-Anwendung konfigurierbar mit PostgreSQL betreiben. Offene Fragen:

1. Wo liegt die Composition Root?
2. Wie wird zwischen In-Memory und PostgreSQL gewählt?
3. Wie garantiert eine HTTP-Operation dieselbe Session/Transaktion?
4. Wird ADR-0010 ersetzt oder ergänzt?

## Entscheidung

**Request-scoped Unit of Work** über SQLAlchemy-Session pro HTTP-Request:

| Aspekt | Entscheidung |
|--------|--------------|
| Auswahl Persistenz | `DATABASE_URL` gesetzt → PostgreSQL; fehlt oder leer → In-Memory (expliziter Dev-/Test-Modus) |
| Composition Root | `api/persistence.py` + `api/app.py` (Lifespan, Middleware) |
| Session-Lifecycle | Middleware öffnet Session, setzt `request.state.deps`, committet bei Erfolg, rollback bei Fehler |
| Repository-Commits | PostgreSQL-Adapter committen standardmäßig **nicht** (`commit=False`); Commit nur durch Request-UoW |
| Abschluss-Port | **Bleibt** (ADR-0010); orchestriert zwei Saves ohne eigenes Commit |
| Tests | Explizites `create_app(deps=…)` mit `in_memory_deps()` — unabhängig von CI-`DATABASE_URL` |

## Begründung

- Eine HTTP-Operation = eine Transaktionsgrenze — ausreichend für V1-Use-Cases
- Kein globales UoW-Objekt in Domain/Application nötig
- Abschluss-Port bleibt fachlich sinnvoll; unter PostgreSQL nutzt er dieselbe Request-Session
- In-Memory bleibt Default ohne DB-Setup; CI-API-Tests bleiben stabil

## Konsequenzen

- Routen nutzen `get_request_deps(request)` statt `request.app.state.deps`
- App-Lifespan: Engine create/dispose, `init_schema` beim Start
- Ungültige `DATABASE_URL` → `PersistenceConfigurationError` beim Start (kein stilles Fallback auf In-Memory)
- Gate 7.2 (docker-compose) kann `DATABASE_URL` für lokale Entwicklung setzen

## Bezug

- Ergänzt [ADR-0010](0010-prueflauf-abschluss-transaktion.md) — ersetzt es nicht
- [ADR-0002](0002-backend-stack.md) — Transport/Persistenz-Trennung unverändert
