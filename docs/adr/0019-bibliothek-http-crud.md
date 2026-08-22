# ADR-0019: Bibliothek-HTTP CRUD (Gate 8.2a)

## Status

Angenommen (Gate 8.2a)

## Kontext

Gate 6.3a ([ADR-0017](0017-katalog-setup-http-automatisierung.md)) liefert minimalen Katalog-Setup-HTTP (Kommando anlegen, Einzelkommando zuweisen). Application-Use-Cases für Routinen und Routine-Zuweisung existieren (Gate 7.3a/d), sind aber nicht vollständig über HTTP erreichbar. Gate 8.2a schließt die **Bibliotheksverwaltung** als Design-Time-Katalog-API — ohne UI (8.2c), ohne Auth (8.1), ohne Run-Time.

## Entscheidung

### Schichten und Abgrenzung

| Regel | Detail |
|-------|--------|
| Phase | **Design Time** — Katalog-Bounded-Context |
| Kein Run-Time | Kein `ExternesKommandoPort`, kein `RoutineAusfuehren`, keine Geräteausführung |
| Kein Auth | Laborbetrieb gemäß [ADR-0001](0001-v1-scope-deferrals.md) |
| Kein Frontend | Gate 8.2c |
| Kein Schema | Bestehende Tabellen `externes_kommando`, `routine` — keine Alembic-Migration |
| Rückwärtskompatibilität | Gate 6.3a-Contracts unverändert (POST Kommando, Einzelkommando-Zuweisung) |

### Externes Kommando — HTTP

| Methode | Pfad | Use Case |
|---------|------|----------|
| POST | `/katalog/bibliothek/kommandos` | `ExternesKommandoAnlegen` (6.3a — unverändert) |
| GET | `/katalog/bibliothek/kommandos` | `ExterneKommandosListen` |
| GET | `/katalog/bibliothek/kommandos/{kommando_id}` | `ExternesKommandoLesen` |
| PUT | `/katalog/bibliothek/kommandos/{kommando_id}` | `ExternesKommandoAktualisieren` |
| DELETE | `/katalog/bibliothek/kommandos/{kommando_id}` | `ExternesKommandoLoeschen` |

**Listen-Response:** `{ "kommando_id", "bezeichnung" }` — **ohne** `kommandocode`.

**Detail-Response:** `{ "kommando_id", "bezeichnung", "kommandocode" }`.

**Update-Request:** `{ "bezeichnung", "kommandocode" }` — `extra=forbid`; mutable save über `BibliothekRepository.save_externes_kommando`.

**Keine** Adapter-/COM-Felder. Keine freie Kommandoausführung.

### Routine — HTTP

| Methode | Pfad | Use Case |
|---------|------|----------|
| POST | `/katalog/bibliothek/routinen` | `RoutineAnlegen` |
| GET | `/katalog/bibliothek/routinen` | `RoutinenListen` |
| GET | `/katalog/bibliothek/routinen/{routine_id}` | `RoutineLesen` |
| PUT | `/katalog/bibliothek/routinen/{routine_id}` | `RoutineAktualisieren` |
| DELETE | `/katalog/bibliothek/routinen/{routine_id}` | `RoutineLoeschen` |

**Anlegen/Update-Request:** `{ "bezeichnung", "kommando_ids": ["…", …] }` — Reihenfolge = Aktionspositionen ab 1; `extra=forbid`.

**Listen-Response:** `{ "routine_id", "bezeichnung", "anzahl_aktionen" }`.

**Detail-Response:** `{ "routine_id", "bezeichnung", "aktionen": [{ "position", "kommando_id" }] }` — **ohne** `kommandocode` in Aktionen.

Domain-Invarianten (`LeereRoutine`, `UngueltigeAktionsreihenfolge`) bleiben führend. Keine neuen Aktionsarten.

### Automatisierung am Entwurfsschritt — erweitert

`PUT /katalog/entwuerfe/{produktdefinition_id}/schritte/{schritt_id}/automatisierung`

| Zustand | Request-Body | Use Case |
|---------|--------------|----------|
| Kommando zuweisen | `{ "kommando_id": "…" }` | `KommandoProzedurSchrittZuweisen` (6.3a) |
| Routine zuweisen | `{ "routine_id": "…" }` | `RoutineProzedurSchrittZuweisen` |
| Entfernen | `{ "kommando_id": null, "routine_id": null }` — **beide** Keys explizit | `AutomatisierungEntfernen` |

**XOR:** `kommando_id` und `routine_id` dürfen nicht gleichzeitig gesetzt sein. Leerer Body `{}` → 422.

**Keine stille Ersetzung:** Wechsel Kommando ↔ Routine erfordert zuerst explizites Entfernen → `AutomatisierungDoppeltZugewiesen` (409), wie Gate 7.3d.

### DELETE — Referenzschutz

| Objekt | Löschen verhindern (409 `kommando_in_verwendung` / `routine_in_verwendung`) wenn |
|--------|-------------------------------------------------------------------------------------|
| Externes Kommando | offener Entwurf referenziert `kommando_id` direkt **oder** Routine referenziert `kommando_id` |
| Routine | offener Entwurf referenziert `routine_id` |

**Veröffentlichte** `ProduktdefinitionsVersionen` blockieren DELETE **nicht** (materialisierte Snapshots sind unabhängig von der mutable Bibliothek).

Prüfung über `KatalogRepository.list_entwuerfe()` und `BibliothekRepository.list_routinen()` — kein API-Zugriff auf Repositories.

### Repository-Erweiterungen

**BibliothekRepository:** `list_externe_kommandos`, `list_routinen`, `delete_externes_kommando`, `delete_routine`.

**KatalogRepository:** `list_entwuerfe` — nur für Referenzprüfung beim DELETE.

In-Memory und PostgreSQL: gleicher Contract. Keine Pagination, Suche, Sortier-Engine.

### Fehlerformat

`{ "detail", "code" }` — u. a. `externes_kommando_nicht_gefunden`, `routine_nicht_gefunden`, `kommando_in_verwendung`, `routine_in_verwendung`, `automatisierung_doppelt_zugewiesen`, `validation` (422).

Referenzkonflikte beim DELETE: HTTP **409**.

## Nicht-Ziele (Gate 8.2a)

PrüfschrittVorlage, Entwurfseditor, Admin-UI, Auth, Storage, Run-Time-Änderungen, neue Routine-Aktionsarten, Pagination, Suche, Bulk-Ops, OpenAPI-Codegen, Alembic, Storage Exit.

## Konsequenzen

- Gate 8.2c kann Bibliothek-HTTP konsumieren
- Demo-Seed (6.3c) bleibt auf 6.3a-Endpoints
- ADR-0016 Run-Time-Contract unverändert

## Referenzen

- [ADR-0012](0012-katalog-bibliothek-externes-kommando.md)
- [ADR-0014](0014-routine-katalog-materialisierung.md)
- [ADR-0017](0017-katalog-setup-http-automatisierung.md)
- `docs/technical-domain/katalog.md`
