# Teststrategie — PWE

Operationalisierung von TDD (projektrules). Stack: ADR-0002.

## Schichten

| Schicht | Was testen | Werkzeug | Abhängigkeiten |
|---------|------------|----------|----------------|
| **Domain** | Aggregate-Invarianten, Wertobjekte | pytest, rein | keine |
| **Application** | Use-Case-Orchestrierung | pytest + In-Memory-Repos | Domain, Ports |
| **Adapter** | Mapping, SQL, COM-Simulation | pytest, Testcontainers (später) | extern |
| **API** | HTTP-Contract | pytest + httpx (später) | Application |

## Regeln

- Domain-Tests **ohne** Datenbank, COM, Dateisystem.
- Ein **Vertical-Slice-Test** pro Kern-Use-Case in `tests/application/`.
- In-Memory-Repos in `adapters/persistence/in_memory.py` — nicht in Tests duplizieren.
- Persistenz-Tests erst nach PostgreSQL-Adapter (Gate 5).

## V1-Pflicht vor Merge

```bash
cd backend && pip install -e ".[dev]" && pytest
```

## Nicht in V1

- E2E-Browser-Tests
- Lasttests
- Vollständige COM-Hardware-Tests
