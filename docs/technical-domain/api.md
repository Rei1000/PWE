# Technical Domain — API

Brücke Application → HTTP. Fachliche Referenz: `docs/architecture.md` §6–§7, ADR-0002.

## Prinzipien

| Regel | Umsetzung |
|-------|-----------|
| Keine Fachlogik | Routen delegieren ausschließlich an Application-Use-Cases |
| Keine Domain in DTOs | Pydantic-Schemas nur in `api/schemas.py` |
| Wiring | `api/deps.py` — Repositories und Adapter injizierbar |

## Endpunkte (V1-Slice)

| Methode | Pfad | Use Case |
|---------|------|----------|
| GET | `/health` | — |
| POST | `/katalog/entwuerfe` | `EntwurfAnlegen` |
| POST | `/katalog/entwuerfe/{id}/veroeffentlichen` | `ProduktdefinitionVeroeffentlichen` |
| POST | `/prueflaeufe` | `PruefungStarten` |
| POST | `/prueflaeufe/{id}/komponenten` | `KomponenteErfassen` |
| POST | `/prueflaeufe/{id}/schritte/{schritt_id}/nachweise` | `NachweisErfassen` |
| POST | `/prueflaeufe/{id}/schritte/{schritt_id}/beurteilung` | `SchrittBeurteilen` |
| POST | `/prueflaeufe/{id}/abschluss` | `PruefungAbschliessen` |
| GET | `/prueflaeufe/{id}/protokoll/pdf` | `ProtokollErzeugen` |

## Fehlerformat

Alle API-Fehler (Domain und Validierung) liefern ein einheitliches JSON-Objekt:

```json
{"detail": "Lesbare Fehlermeldung", "code": "maschinenlesbarer_code"}
```

| HTTP | `code` (Beispiele) | Auslöser |
|------|---------------------|----------|
| 404 | `version_nicht_gefunden`, `entwurf_nicht_gefunden`, … | `DomainError` (Subklassen → snake_case) |
| 409 | `invariant_verletzt` | `InvariantViolation` |
| 422 | `validation` | Pydantic / Request-Validierung |

Implementierung: `api/fehler.py`, Handler in `api/errors.py`.

## Wiring (Persistenz)

| Modus | Status | Begründung |
|-------|--------|------------|
| **In-Memory (Default)** | ✅ V1-Slice | `in_memory_deps()` — ausreichend für Transport-Slice, lokale Entwicklung und CI. Kein DB-Setup nötig. |
| **PostgreSQL via Konfiguration** | ⏸ P2 | Session-Lifecycle pro Request und Ops-Anbindung gehören zum nächsten Härtungsschritt (Deployment/Frontend-Integration). Application- und Persistence-Layer sind bereits postgres-fähig (ADR-0002, Gate 5). |

**Entscheidung:** In-Memory-Default ist für diesen API-Slice **akzeptabel**. Kein ADR-Update nötig — ADR-0002 trennt Transport von Persistenz; die API injiziert Repositories über `ApiDeps`.

## Authentifizierung / Identity

| Thema | Status | Begründung |
|-------|--------|------------|
| Auth-Middleware, Tokens | ⏸ P2 | ADR-0001: V1 PC-only, kein Multi-User-Betrieb. |
| `pruefer_id` im Request-Body | ✅ V1-Slice | Ausreichend für Frontend-Prototyp; Identity-Context folgt mit Auth-Slice. |

## Frontend-Vorbereitung (Katalog)

Ohne veröffentlichte Produktdefinition schlägt `POST /prueflaeufe` mit `version_nicht_gefunden` fehl. Der minimale Katalog-Flow für den nächsten Frontend-Slice:

1. `POST /katalog/entwuerfe` — Entwurf anlegen
2. `POST /katalog/entwuerfe/{id}/veroeffentlichen` — aktive Version materialisieren
3. `POST /prueflaeufe` — Prüfung starten

Keine Admin-UI, keine vollständige Katalogverwaltung in diesem Slice.

## Bewusst offen (nach Merge)

- OpenAPI-Versionierung / erweiterte Validierungsdetails (`errors[]` bei 422)
- PostgreSQL-Wiring in `create_app()` / `deps.py`
- Authentifizierung und serverseitiger Identity-Context
