# Teststrategie — PWE

Operationalisierung von TDD (projektrules). Stack: ADR-0002.

## Schichten

| Schicht | Was testen | Werkzeug | Abhängigkeiten |
|---------|------------|----------|----------------|
| **Domain** | Aggregate-Invarianten, Wertobjekte | pytest, rein | keine |
| **Application** | Use-Case-Orchestrierung | pytest + In-Memory-Repos | Domain, Ports |
| **Adapter** | Mapping, SQL, COM-Simulation | pytest | extern |
| **API** | HTTP-Contract | pytest + httpx | Application |
| **Frontend** | Transport-Schemas, API-Client | vitest | adapters/api |

## Regeln

- Domain-Tests **ohne** Datenbank, COM, Dateisystem.
- Ein **Vertical-Slice-Test** pro Kern-Use-Case in `tests/application/`.
- In-Memory-Repos in `adapters/persistence/in_memory.py` — nicht in Tests duplizieren.
- PostgreSQL-Adapter in `adapters/persistence/postgresql/` — Mapping-Tests ohne DB; Repository-Tests mit `DATABASE_URL` (CI: Postgres-Service).

## V1-Pflicht vor Merge

```bash
cd backend && pip install -e ".[dev]" && pytest
```

## Nicht in V1

- E2E-Browser-Tests
- Lasttests
- Vollständige COM-Hardware-Tests
