# ADR-0018: Legacy-Automatisierung Exit — API Exit (Gate 7.4a)

## Status

Angenommen (Gate 7.4a)

## Kontext

Gate 7.3f führte den schrittzentrierten Endpunkt ([ADR-0016](0016-automatisierung-http-api.md)) als führenden Run-Time-HTTP-Contract ein und markierte den Einzelkommando-Endpunkt (Gate 7.3b) als deprecated. Gate 6.3 hat Frontend und Demo vollständig auf ADR-0016 umgestellt.

Die Übergangsarchitektur umfasste fünf getrennte Aspekte (Schreiben, Lesen, Legacy-Use-Case, HTTP, Persistenz). Ein Write Exit vor dem API Exit würde einen öffentlichen deprecated Endpunkt hinterlassen, der `schritt.externes_kommando` verlangt, während neue Versionen dieses Feld nicht mehr schreiben — kaputter Zwischenzustand.

## Entscheidung

### Gate 7.4a — API Exit (dieser Slice)

| Regel | Detail |
|-------|--------|
| Führender Contract | [ADR-0016](0016-automatisierung-http-api.md) ist der **einzige** aktive Run-Time-HTTP-Contract für Automatisierung |
| Entfernt | `POST …/kommandos/{kommando_id}/ausfuehren` — vollständig, kein Redirect, kein Alias, keine stille Delegation |
| Entfernt | Application Use Case `ExternesKommandoAusfuehren` (keine produktive Abhängigkeit außer Legacy-HTTP) |
| Erhalten | `kommandoausfuehrung_kern` — weiterhin von `RoutineAusfuehren` genutzt; keine Kopie |
| Erhalten | Legacy-Lesen: Feld `externes_kommando`, Deserialisierung, `aufgeloeste_materialisierte_routine()` |
| Unverändert | Publish schreibt weiterhin Legacy-Snapshot neben `materialisierte_routine` (Write Exit = Gate 7.4b) |
| Breaking Change | Bewusst vor Produktion und nach dokumentierter Deprecation |

### Exit-Reihenfolge (verbindlich)

1. **Gate 7.4a — API Exit** (dieser ADR): Legacy-HTTP + Legacy-Use-Case
2. **Gate 7.4b — Write Exit**: neue Versionen schreiben kein `externes_kommando` mehr
3. **Gate 7.4c — Monitoring**: unabhängig; `fehlgeschlagen` auswerten
4. **Storage Exit**: physische Entfernung aus Persistenz/Mapping **erst nach Gate 7.5 / Alembic** und bewusster Datenstrategie

Physische Entfernung des Felds erfolgt **nicht** in Gate 7.4a oder 7.4b.

### Legacy-Lesekompatibilität (P0)

Alte Versionen mit ausschließlich `externes_kommando` (`materialisierte_routine=None`) bleiben lesbar und über ADR-0016 ausführbar:

- Read Model erkennt Automatisierung
- `aufgeloeste_materialisierte_routine()` normalisiert zur synthetischen Ein-Aktions-Routine
- `RoutineAusfuehren` / `POST …/automatisierung/ausfuehren` funktionieren
- Nachweise werden erzeugt

### Nicht-Ziele (Gate 7.4a)

- Write Exit / Materialisierungsänderung
- Storage Exit / JSON- oder Datenmigration / Alembic
- Entfernen von `externes_kommando` aus Domain-/Persistenzmodell
- API-v2, Redirect/Compatibility-Endpoint
- Refactoring von `kommandoausfuehrung_kern`
- Monitoring, Auth, Katalog-Admin, neue Aktionsarten
- Big-Bang-Umbau

## Begründung

- Nach Gate 6.3 ist der Legacy-HTTP-Pfad ohne Client-Nutzen und erhöht Vertragsfläche
- API Exit vor Write Exit vermeidet den toten öffentlichen Endpoint
- Gemeinsame Kernlogik bleibt eine Quelle der Wahrheit für COM/Simulation und Audit (ADR-0013/0015)
- Stufenweiser Abbau statt Big Bang reduziert Migrationsrisiko

## Konsequenzen

- OpenAPI enthält den Legacy-Pfad nicht mehr
- Clients dürfen nur noch ADR-0016 verwenden
- Historische ADR-/Changelog-Referenzen auf den deprecated Endpoint bleiben als Historie
- Design-Time-Entity `ExternesKommando` und Bibliotheks-HTTP (Gate 6.3a) bleiben unverändert

## Referenzen

- [ADR-0014](0014-routine-katalog-materialisierung.md)
- [ADR-0015](0015-routine-ausfuehren-application-runner.md)
- [ADR-0016](0016-automatisierung-http-api.md)
- `docs/roadmap.md` — Gate 7.4a–c
