# Teststrategie — PWE

Operationalisierung von TDD (projektrules). Stack: ADR-0002.

## Schichten

| Schicht | Was testen | Werkzeug | Abhängigkeiten |
|---------|------------|----------|----------------|
| **Domain** | Aggregate-Invarianten, Wertobjekte | pytest, rein | keine |
| **Application** | Use-Case-Orchestrierung | pytest + In-Memory-Repos | Domain, Ports |
| **Adapter** | Mapping, SQL, COM-Simulation, PySerialTransport (Mock) | pytest | extern |
| **API** | HTTP-Contract | pytest + httpx | Application |
| **Frontend** | Transport-Schemas, API-Client | vitest | adapters/api |

## Regeln

- Domain-Tests **ohne** Datenbank, COM, Dateisystem.
- Ein **Vertical-Slice-Test** pro Kern-Use-Case in `tests/application/`.
- In-Memory-Repos in `adapters/persistence/in_memory.py` — nicht in Tests duplizieren.
- PostgreSQL-Adapter in `adapters/persistence/postgresql/` — Mapping-Tests ohne DB; Repository-Tests mit `DATABASE_URL` (CI: Postgres-Service).
- **OpenAPI-Contract-Tests** (Gate 7.3f): maschinenlesbare Prüfung von Response-Schemas, `deprecated`-Markierung Legacy-Endpunkte, `additionalProperties: false` am Request — `tests/api/test_api_openapi_automatisierung.py`.
- **Katalog-Setup-API-Tests** (Gate 6.3a): HTTP-E2E Setup + Automatisierung, OpenAPI — `tests/api/test_api_katalog_automatisierung_setup.py`, `test_api_openapi_katalog_automatisierung_setup.py`, PostgreSQL in `test_api_postgresql_katalog_automatisierung_setup.py`.

## V1-Pflicht vor Merge

```bash
cd backend && pip install -e ".[dev]" && pytest
```

## Nicht in V1

- E2E-Browser-Tests
- Lasttests
- Vollständige COM-Hardware-Tests (Arbeitsplatz mit physischem Gerät)
- Automatischer Retry im COM-Transport
