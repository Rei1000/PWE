# ADR-0021: Erweiterte HTTP-Bearbeitung von ProduktdefinitionsEntwürfen (Gate 8.2b2)

## Status

Angenommen (Gate 8.2b2)

## Kontext

Gate 8.2b1 liefert `PruefschrittVorlage` in der Bibliothek und Publish-Materialisierung ([ADR-0020](0020-pruefschritt-vorlage-materialisierung.md)). Entwürfe können nur per `POST /katalog/entwuerfe` mit vollständiger Schrittliste angelegt und per `PUT .../automatisierung` automatisiert werden — **kein** schrittweises Bearbeiten per HTTP.

Gate 8.2c (Admin-UI) benötigt stabile Design-Time-HTTP-Contracts zum Lesen und Bearbeiten von Entwürfen ohne Frontend in diesem Slice.

## Entscheidung

### Architektur

| Aspekt | Entscheidung |
|--------|--------------|
| Schreibendes Aggregate | **Nur** `Produktdefinition` (mutable Entwurf) |
| `ProzedurSchrittEntwurf` | Value Object innerhalb des Aggregates — **kein** eigenes AR |
| Veröffentlichte Versionen | **Unveränderlich** — Entwurfsänderungen wirken erst nach erneutem Publish auf **neue** Versionen |
| Run Time | **Keine** Lesung aus dem Entwurf — nur materialisierte Version |
| Automatisierung | **Ausschließlich** `PUT .../schritte/{schritt_id}/automatisierung` (Gate 6.3a/8.2a) — nicht im Schritt-PUT |
| Vorlage | `vorlage_id` bei Anlage/Änderung gegen `BibliothekRepository` validieren — **kein** Kopieren mutable Vorlageninhalte in den Entwurf |
| Materialisierung | Unverändert über bestehenden `ProduktdefinitionVeroeffentlichen`-Pfad |

### Leerer Entwurf

Ein Entwurf **darf** zeitweise **null** ProzedurSchritte enthalten. `veroeffentlichen()` lehnt das ab (`InvariantViolation` — mindestens ein Schritt). DELETE des letzten Schritts ist erlaubt.

### Schritt-ID

| Regel | Detail |
|-------|--------|
| Identität | `schritt_id` wird über URL/Pfad adressiert — **nicht** per PUT änderbar |
| Vergabe | **Client-seitig** bei `POST .../schritte` (konsistent mit `POST /entwuerfe`) |
| Eindeutigkeit | Innerhalb eines Entwurfs eindeutig — Duplikat → `SchrittIdBereitsVorhanden` (409) |
| Leer | Nach Trim leer → `InvariantViolation` (409) |

### Reihenfolge

| Regel | Detail |
|-------|--------|
| Eindeutigkeit | `reihenfolge` ist innerhalb des Entwurfs eindeutig |
| Lückenlos | Nach Anlage, Löschung und Reorder: Werte **1..n** ohne Lücken |
| Anlage | Neuer Schritt wird **am Ende** eingefügt (`max(reihenfolge)+1`) — kein Positionsfeld im POST |
| Änderung | **Nur** über `PUT .../schritte/reihenfolge` — nicht im Schritt-PUT |
| Reorder-Contract | Vollständige Permutation aller `schritt_id` — keine Teil-Reorder, keine stillen Ergänzungen |

Request Reorder: `{ "schritt_ids": ["s3", "s1", "s2"] }` → `reihenfolge` 1, 2, 3 entsprechend.

### Schritt-PUT (vollständig)

Bearbeitbar: `vorlage_id`, `ist_pflicht`, `sollvorgaben`.

**Nicht** bearbeitbar: `schritt_id`, `kommando_id`, `routine_id`, `reihenfolge`.

Bestehende Automatisierung (`kommando_id`/`routine_id`) bleibt beim PUT **unverändert**.

Vollständiges PUT — fehlende Felder sind kein PATCH.

### DELETE

`DELETE .../schritte/{schritt_id}` → **204**. Schritt-VO inkl. Automatisierungsreferenzen entfällt. Verbleibende Schritte werden auf `1..n` neu nummeriert. Keine Bibliotheks- oder Versions-Mutation.

### HTTP-Contract

| Methode | Pfad | Use Case |
|---------|------|----------|
| GET | `/katalog/entwuerfe/{produktdefinition_id}` | `EntwurfLesen` |
| POST | `/katalog/entwuerfe/{produktdefinition_id}/schritte` | `ProzedurSchrittAnlegen` |
| PUT | `/katalog/entwuerfe/{produktdefinition_id}/schritte/{schritt_id}` | `ProzedurSchrittAktualisieren` |
| DELETE | `/katalog/entwuerfe/{produktdefinition_id}/schritte/{schritt_id}` | `ProzedurSchrittLoeschen` |
| PUT | `/katalog/entwuerfe/{produktdefinition_id}/schritte/reihenfolge` | `ProzedurSchrittReihenfolgeAendern` |

Bestehend unverändert: `POST /entwuerfe`, `POST .../veroeffentlichen`, `PUT .../automatisierung`.

Write-Schemas: `extra="forbid"`. Keine Runtime-, Materialisierungs- oder Adapter-Felder.

GET-Response: `produktdefinition_id`, `produktkodierung`, `sollbestueckung` (read-only), `prozedur_schritte` mit `schritt_id`, `vorlage_id`, `ist_pflicht`, `reihenfolge`, `sollvorgaben`, `kommando_id`, `routine_id`.

### Persistenz

Entwurf bleibt JSON-Payload in `produktdefinition_entwurf` — **keine** Alembic-Migration.

## Nicht-Ziele (Gate 8.2b2)

Entwurf LIST, Root-Metadaten bearbeiten (`produktkodierung`, `sollbestueckung`, Ebenen-Sollvorgaben), Aktivierungsregeln, Eingabefelder, Frontend (8.2c), Auth, Storage, Run-Time, neue Routine-Aktionsarten, Pagination, Suche, Bulk außer Reorder, OpenAPI-Codegen, allgemeine Refactorings.

## Konsequenzen

- Domain-Methoden auf `Produktdefinition` kapseln Schritt-Mutationen und Invarianten
- Application-Use-Cases: laden → Domain → optional Vorlagen-Lookup → `save_entwurf`
- Gate 8.2c konsumiert GET/CRUD ohne weitere Backend-Slices

## Referenzen

- Domain Model §4.4, §4.8
- [ADR-0005](0005-sollvorgaben-materialisierung.md)
- [ADR-0017](0017-katalog-setup-http-automatisierung.md)
- [ADR-0020](0020-pruefschritt-vorlage-materialisierung.md)
