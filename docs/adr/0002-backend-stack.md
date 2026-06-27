# ADR-0002: Backend-Technologiestack

## Status

Accepted

## Kontext

CI und Docker nutzen bereits Python 3.11. Vor Implementierung muss der Stack verbindlich sein, damit Technical Domain Design und Tests nicht abstrakt bleiben.

## Entscheidung

| Bereich | Wahl |
|---------|------|
| Sprache | Python 3.11+ |
| Paket/Tests | `pyproject.toml`, pytest |
| Domain-Modell | `@dataclass`, Standardbibliothek — **kein** ORM/Pydantic in Domain |
| Typisierung | `enum.Enum`, `typing` — pragmatisch, keine schwere Framework-Abhängigkeit |
| API (später) | FastAPI + httpx in Tests |
| Persistenz (später) | PostgreSQL, SQLAlchemy **nur** in `adapters/persistence/` |
| IDs V1 | UUID (`uuid4`) als String-Repräsentation |

Module unter `backend/src/` mit Importpfad über `pythonpath = ["src"]` in pytest.

## Konsequenzen

- Domain bleibt frameworkfrei und schnell testbar
- ORM-Details dringen nicht in Aggregate ein

## Alternativen

- Node/TypeScript Backend: verworfen — Docker/CI bereits auf Python
- Pydantic in Domain: verworfen — Validierung gehört an Domain-Grenzen (Application/Adapter), nicht in Entitätskern
