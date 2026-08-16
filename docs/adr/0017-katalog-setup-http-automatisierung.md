# ADR-0017: Katalog-Setup-HTTP für Automatisierung (Gate 6.3a)

## Status

Angenommen (Gate 6.3a)

## Kontext

Gate 7.3 liefert Run-Time-Ausführung (`RoutineAusfuehren`, ADR-0016). Gate 6.2 deckt den manuellen Prüferflow ab. Application-Use-Cases für Bibliothek und Automatisierungs-Zuweisung existieren (Gate 7.3a/d), sind aber nicht über HTTP erreichbar — ein automatisierbarer Prüfschritt ist per öffentlicher API nicht einrichtbar.

Gate 6.3a schließt diese Lücke mit einem **minimalen Katalog-Setup-Contract**, nicht mit vollständiger Katalog-Administration.

## Entscheidung

### Endpunkte (Gate 6.3a)

| Methode | Pfad | Use Case |
|---------|------|----------|
| POST | `/katalog/bibliothek/kommandos` | `ExternesKommandoAnlegen` |
| PUT | `/katalog/entwuerfe/{produktdefinition_id}/schritte/{schritt_id}/automatisierung` | `KommandoProzedurSchrittZuweisen` |

### Abgrenzungen

| Thema | Regel |
|-------|-------|
| Betrieb | PC-/Laborbetrieb gemäß [ADR-0001](0001-v1-scope-deferrals.md) — **kein Auth** in 6.3a |
| Mehrbenutzer / Internet | Endpunkte **nicht** für ungeschützte Bereitstellung vorgesehen; Auth folgt Gate 8.1 |
| Admin-API | **Keine** vollständige Bibliotheksverwaltung — Grundlage für spätere Gate-8.2a-CRUD |
| Dev-Wegwerfcode | **Kein** dedizierter `/dev/seed`-Endpunkt — Setup über fachliche Katalog-HTTP |
| Ausführung | **Keine** Geräteaktion, kein `ExternesKommandoPort` in Katalog-Routen |
| Adapter | **Keine** COM-, Baudraten-, Timeout- oder Port-Felder im Contract |
| Freie Ausführung | **Kein** `kommandocode` zur Laufzeit — nur Bibliotheks-Anlage und Entwurfs-Zuweisung per `kommando_id` |
| Routinen | **Kein** `routine_id` im Request; Routine-Anlage/-Zuweisung = Gate 8.2a |
| Schema | **Keine** DB-Änderung; Alembic = Gate 7.5 |
| Schichten | Katalog-HTTP delegiert ausschließlich an Katalog-Application |

### POST `/katalog/bibliothek/kommandos`

**Request:** `{ "bezeichnung", "kommandocode" }` — `extra=forbid`; Client setzt **keine** `kommando_id`.

**Response 201:** `{ "kommando_id", "bezeichnung" }` — **ohne** `kommandocode` (schmaler Contract; Ausführung liest materialisierten Snapshot, Setup-Flow benötigt nur `kommando_id` für Zuweisung).

**Idempotenz:** nicht idempotent — jeder POST erzeugt neue `kommando_id`.

### PUT Automatisierung zuweisen

**Request:** `{ "kommando_id" }` — ausschließlich; `extra=forbid`; kein `routine_id`, kein `kommandocode`.

**Response 200:** `{ "produktdefinition_id", "schritt_id", "kommando_id", "routine_id": null }` — `routine_id: null` zeigt Entwurfszustand; Request akzeptiert kein `routine_id`.

**PUT-Semantik:**

| Fall | Verhalten |
|------|-----------|
| Gleiche `kommando_id` erneut | Idempotent — HTTP 200, kein neues Bibliotheksobjekt |
| Andere `kommando_id` bei gesetztem Kommando | **409** `automatisierung_doppelt_zugewiesen` — Wechsel erfordert explizites Entfernen (nicht in 6.3a) |
| `routine_id` am Schritt gesetzt | **409** `automatisierung_doppelt_zugewiesen` |
| Entfernen (`kommando_id: null`) | **Nicht** in 6.3a exponiert |

### Fehlerformat

404/409/422 mit `{ "detail", "code" }` — keine Roh-Exception-Texte.

## Konsequenzen

- Erstmals vollständig HTTP-basierter Setup- und Ausführungsflow für Einzelkommando-Automatisierung
- Gate 6.3b/c bauen auf diesen Endpunkten auf (Frontend-Ausführung; Demo-Seed als externer HTTP-Client `scripts/seed_demo_automatisierung.py`, kein `/dev`-Endpoint)
- Gate 8.2a erweitert Bibliothek-HTTP (Listen, Routinen, CRUD) — kein Ersatz für 6.3a / 6.3c

## Nicht-Ziele (Gate 6.3a)

Routine anlegen/zuweisen, Bibliothek listen/löschen, Admin-UI, Frontend, Auth, Alembic, Legacy-Abbau, Monitoring, Feature-Flag `KATALOG_WRITE_ENABLED`.
