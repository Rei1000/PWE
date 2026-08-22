# ADR-0018: Legacy-Automatisierung Exit (Gate 7.4a / 7.4b)

## Status

Angenommen — Gate 7.4a API Exit ✅, Gate 7.4b Write Exit ✅, Gate 7.4c Monitoring ✅. Storage Exit offen (nach Gate 7.5).

## Kontext

Gate 7.3f führte den schrittzentrierten Endpunkt ([ADR-0016](0016-automatisierung-http-api.md)) als führenden Run-Time-HTTP-Contract ein. Gate 6.3 stellte Frontend und Demo auf ADR-0016 um. Die Übergangsarchitektur umfasste Schreiben, Lesen, Legacy-Use-Case, HTTP und Persistenz des Felds `externes_kommando`.

## Entscheidung

### Exit-Reihenfolge (verbindlich)

1. **Gate 7.4a — API Exit** ✅: Legacy-HTTP + Use Case `ExternesKommandoAusfuehren`
2. **Gate 7.4b — Write Exit** ✅: neue Versionen schreiben kein `externes_kommando` mehr
3. **Gate 7.4c — Monitoring** ✅: fachliche Beobachtung über `fehlgeschlagen` ([ADR-0016](0016-automatisierung-http-api.md)); keine APM-Plattform
4. **Storage Exit**: physische Entfernung aus Persistenz/Mapping **erst nach Gate 7.5 / Alembic** und bewusster Datenstrategie

### Gate 7.4a — API Exit

| Regel | Detail |
|-------|--------|
| Führender Contract | [ADR-0016](0016-automatisierung-http-api.md) alleiniger Run-Time-HTTP-Contract |
| Entfernt | `POST …/kommandos/{kommando_id}/ausfuehren`; Use Case `ExternesKommandoAusfuehren` |
| Erhalten | `kommandoausfuehrung_kern`, Legacy-Lesen, `aufgeloeste_materialisierte_routine()` |

### Gate 7.4b — Write Exit

| Regel | Detail |
|-------|--------|
| Publish | schreibt **nur** `materialisierte_routine`; `externes_kommando=None` |
| Wahrheit neuer Versionen | ausschließlich `materialisierte_routine` |
| Unverändert | Runtime (`RoutineAusfuehren`), HTTP/API, Read Model, Frontend, Demo |
| Unverändert | Mapping/Deserialisierung von `externes_kommando` (Lesen Altbestände) |
| Unverändert | Domain-Feld und JSON-Schema-Option; **keine** Datenmigration, **kein** Alembic |
| Design-Time | Bibliotheks-Entity `ExternesKommando` und Katalog-Setup-HTTP bleiben |

### Legacy-Lesekompatibilität (P0, gilt weiter)

Alte Versionen mit ausschließlich `externes_kommando` (`materialisierte_routine=None`) bleiben lesbar und über ADR-0016 ausführbar über `aufgeloeste_materialisierte_routine()`.

## Nicht-Ziele

| Slice | Nicht |
|-------|-------|
| 7.4a | Write Exit, Storage Exit |
| 7.4b | Storage Exit, Feldentfernung, Migration, Alembic, Monitoring, API-/Runtime-/Frontend-Änderung |

## Begründung

- API Exit vor Write Exit vermeidet toten öffentlichen Legacy-Endpoint
- Write Exit vor Storage Exit erlaubt Altbestände ohne Migration
- Stufenweiser Abbau statt Big Bang

## Konsequenzen

- Neue Veröffentlichungen persistieren kein Legacy-Feld mehr (JSON ohne `externes_kommando`)
- Bestehende Versionen mit Legacy-Snapshot bleiben gültig
- Storage Exit und physische Feldentfernung folgen erst nach Gate 7.5

## Referenzen

- [ADR-0014](0014-routine-katalog-materialisierung.md)
- [ADR-0015](0015-routine-ausfuehren-application-runner.md)
- [ADR-0016](0016-automatisierung-http-api.md)
- `docs/roadmap.md` — Gate 7.4a–c
