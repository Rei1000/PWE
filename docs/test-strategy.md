# Teststrategie — PWE

Operationalisierung von TDD (projektrules). Stack: ADR-0002.

## Schichten

| Schicht | Was testen | Werkzeug | Abhängigkeiten |
|---------|------------|----------|----------------|
| **Domain** | Aggregate-Invarianten, Wertobjekte | pytest, rein | keine |
| **Application** | Use-Case-Orchestrierung | pytest + In-Memory-Repos | Domain, Ports |
| **Adapter** | Mapping, SQL, COM-Simulation, PySerialTransport (Mock) | pytest | extern |
| **API** | HTTP-Contract | pytest + httpx | Application |
| **Frontend** | Transport-Schemas, API-Client, Automatisierungs-Mutation/UI | vitest, Testing Library | adapters/api, components |

## Regeln

- Domain-Tests **ohne** Datenbank, COM, Dateisystem.
- Ein **Vertical-Slice-Test** pro Kern-Use-Case in `tests/application/`.
- In-Memory-Repos in `adapters/persistence/in_memory.py` — nicht in Tests duplizieren.
- PostgreSQL-Adapter in `adapters/persistence/postgresql/` — Mapping-Tests ohne DB; Repository-Tests mit `DATABASE_URL` (CI: Postgres-Service).
- **Alembic** (Gate 7.5 ✅): Upgrade/Downgrade/Re-Upgrade; Runtime ohne Migration schlägt fehl — `tests/adapters/test_alembic_bootstrap.py`, Session-Migrate in `tests/conftest.py`, isolierte Schemas via `ALEMBIC_SCHEMA`.
- **OpenAPI-Contract-Tests** (Gate 7.3f / 7.4a): Zielendpoint ADR-0016; Legacy-Pfad abwesend — `tests/api/test_api_openapi_automatisierung.py`.
- **Write Exit** (Gate 7.4b): Publish ohne Legacy-Snapshot; Altbestände lesbar — `tests/application/test_write_exit_materialisierung.py`, PostgreSQL in `test_postgresql_routine_materialisierung.py`.
- **Monitoring-Baseline** (Gate 7.4c): fachliche Beobachtung `fehlgeschlagen` — `tests/api/test_automatisierung_beobachtung.py`.
- **Katalog-Setup-API-Tests** (Gate 6.3a): HTTP-E2E Setup + Automatisierung, OpenAPI — `tests/api/test_api_katalog_automatisierung_setup.py`, `test_api_openapi_katalog_automatisierung_setup.py`, PostgreSQL in `test_api_postgresql_katalog_automatisierung_setup.py`.
- **Frontend-Automatisierung** (Gate 6.3b): Zod-Response inkl. `fehlgeschlagen=true`, Adapter-Zielendpoint, Mutation `retry: false`, Komponenten — `frontend/web/tests/api/automatisierung.test.ts`, `tests/hooks/`, `tests/components/`.
- **Demo-Seed** (Gate 6.3c): `PWE_DEMO_MODE`-Wiring, HTTP-E2E Demo-Flow, Script-Client-Tests — `tests/api/test_demo_mode_wiring.py`, `test_api_demo_seed_e2e.py`, `tests/scripts/test_seed_demo_automatisierung.py`; PostgreSQL in `test_api_postgresql_demo_seed.py`.
- **Bibliothek-HTTP CRUD** (Gate 8.2a): Application `test_katalog_bibliothek_crud.py`; API `test_api_katalog_bibliothek_crud.py`; OpenAPI `test_api_openapi_katalog_bibliothek_crud.py`; PostgreSQL `test_api_postgresql_katalog_bibliothek_crud.py`; Contract-Tests erweitert in `test_bibliothek_repository_contract.py`.
- **PrüfschrittVorlage** (Gate 8.2b1): Domain `test_pruefschritt_vorlage.py`; Application `test_katalog_pruefschritt_vorlage_crud.py`; API `test_api_katalog_pruefschritt_vorlage_crud.py`; OpenAPI `test_api_openapi_katalog_pruefschritt_vorlage_crud.py`; PostgreSQL `test_api_postgresql_katalog_pruefschritt_vorlage_crud.py`; Routine-HTTP-E2E-Regression `test_api_katalog_routine_http_e2e.py`; Contract-Tests in `test_bibliothek_repository_contract.py`; Alembic `0002` in `test_alembic_bootstrap.py`.

## V1-Pflicht vor Merge

```bash
cd backend && pip install -e ".[dev]" && pytest
```

## Nicht in V1

- E2E-Browser-Tests
- Lasttests
- Vollständige COM-Hardware-Tests (Arbeitsplatz mit physischem Gerät)
- Automatischer Retry im COM-Transport
