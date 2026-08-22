# ADR-0020: PrüfschrittVorlage im Katalog und Materialisierung (Gate 8.2b1)

## Status

Angenommen (Gate 8.2b1)

## Kontext

Gate 8.2a liefert Bibliothek-HTTP CRUD für `ExternesKommando` und `Routine` ([ADR-0019](0019-bibliothek-http-crud.md)). `ProzedurSchrittEntwurf` und `MaterialisierterProzedurSchritt` tragen eine opaque `vorlage_id` ohne Bibliotheksobjekt oder Publish-Validierung.

Domain Model §4.9 und §10 verlangen `PrüfschrittVorlage` als wiederverwendbare Bibliotheksdefinition, materialisiert bei Veröffentlichung. ADR-0012 reserviert `PrüfschrittVorlage` als weiteres Aggregate Root im Bibliotheksmodul.

Gate 8.2b wurde in **8.2b1** (Vorlage) und **8.2b2** (Entwurfsbearbeitung HTTP) zerlegt — zwei Aggregate, ein Slice nicht reviewbar.

## Entscheidung

### Architektur

| Aspekt | Entscheidung |
|--------|--------------|
| Bounded Context | `PrüfschrittVorlage` im **Katalog** (Design Time) — **kein** eigener Context |
| Aggregate Root | `PruefschrittVorlage` — eigenständig, stabile `vorlage_id` |
| Repository | `BibliothekRepository` — fachliche **Facade** (ADR-0012-Muster) |
| Semantik | Mutable save analog Kommando/Routine |
| Run Time | **Keine** Lesung aus mutable Bibliothek — nur materialisierter Snapshot |

### Minimalfelder V1

| Feld | Pflicht |
|------|---------|
| `vorlage_id` | ja (server-generiert bei Anlage) |
| `bezeichnung` | ja (nach Trim nicht leer) |
| `beschreibung` | optional |

**Bewusst nicht in 8.2b1:** Eingabefelder, Sollvorgaben, Automatisierung, Reihenfolge, Pflichtstatus, Aktivierungsregeln, Arbeitsanweisungs-Storage.

### Materialisierung

Neuer Value Object `MaterialisiertePruefschrittVorlage` mit Snapshot (`vorlage_id`, `bezeichnung`, `beschreibung`).

`MaterialisierterProzedurSchritt` erhält `materialisierte_vorlage: MaterialisiertePruefschrittVorlage | None`. `vorlage_id` bleibt als Referenz/Audit erhalten.

Beim Veröffentlichen: alle `vorlage_id` des Entwurfs gegen `BibliothekRepository` auflösen. Fehlende Vorlage → `VorlageNichtGefunden` — keine Veröffentlichung mit dangling ID.

### Rückwärtskompatibilität

Bestehende `ProduktdefinitionsVersionen` können nur `vorlage_id` ohne `materialisierte_vorlage` enthalten. Deserialisierung, Lesen, Ausführung und Protokollierung bleiben gültig. **Keine** erzwungene Datenmigration. **Kein** nachträgliches Erzeugen von Snapshots aus der aktuellen Bibliothek für Altversionen.

Neue Veröffentlichungen schreiben immer einen vollständigen Vorlagen-Snapshot.

### DELETE-Referenzschutz

DELETE blockiert, wenn mindestens ein **offener Entwurf** die `vorlage_id` referenziert → `VorlageInVerwendung` (HTTP 409).

**Veröffentlichte Versionen blockieren DELETE nicht** — materialisierter bzw. historischer Snapshot ist unabhängig.

Prüfung über `KatalogRepository.list_entwuerfe()` — kein API-Zugriff auf Repositories.

### PostgreSQL / Alembic

Neue Tabelle `pruefschritt_vorlage` ausschließlich über Alembic-Migration (Gate 7.5-Pfad). Kein `create_all`, keine Runtime-Schemaerzeugung.

### HTTP (Design Time)

| Methode | Pfad |
|---------|------|
| POST | `/katalog/bibliothek/vorlagen` |
| GET | `/katalog/bibliothek/vorlagen` |
| GET | `/katalog/bibliothek/vorlagen/{vorlage_id}` |
| PUT | `/katalog/bibliothek/vorlagen/{vorlage_id}` |
| DELETE | `/katalog/bibliothek/vorlagen/{vorlage_id}` |

Write-Schemas: `extra="forbid"`. Keine Pagination, Suche, Bulk.

### Regression Gate 8.2a

Vollständiger HTTP-E2E-Pfad Routine anlegen → zuweisen → veröffentlichen → Prüflauf → `automatisierung/ausfuehren` als Regressionstest in 8.2b1 (kein separater PR).

## Nicht-Ziele (Gate 8.2b1)

Entwurfsbearbeitung HTTP (8.2b2), Admin-UI (8.2c), Auth, Storage, Eingabefelder, Aktivierungsregeln, Run-Time-Änderungen, neue Routine-Aktionsarten, Pagination, Suche, Bulk, OpenAPI-Codegen, Storage Exit.

## Konsequenzen

- `ProduktdefinitionVeroeffentlichen` benötigt Auflösung von `PrüfschrittVorlage` über `BibliothekRepository`
- Tests mit Veröffentlichung müssen referenzierte Vorlagen in der Bibliothek anlegen
- Gate 8.2c kann Vorlagen-HTTP konsumieren
- Gate 8.2b2 baut auf validierten `vorlage_id` und Publish-Pfad auf

## Referenzen

- Domain Model §4.8, §4.9, §10
- [ADR-0005](0005-sollvorgaben-materialisierung.md)
- [ADR-0012](0012-katalog-bibliothek-externes-kommando.md)
- [ADR-0019](0019-bibliothek-http-crud.md)
