# ADR-0016: Automatisierung am ProzedurSchritt — HTTP-API (Gate 7.3f)

## Status

Angenommen (Gate 7.3f)

## Kontext

Gate 7.3e implementiert `RoutineAusfuehren` als Application Use Case mit einheitlicher Normalisierung (`aufgeloeste_materialisierte_routine`), Teilfehler-Ergebnis und Audit-Korrelation. Gate 7.3b exponiert Einzelkommandos über `kommando_id` im Pfad mit hybridem 409-Verhalten.

Eine Architekturprüfung (Variante D) hat entschieden:

- Schrittzentrierter Automatisierungs-Endpunkt als **führender** API-Contract
- **HTTP 200** + vollständiges Ergebnisobjekt für jede **begonnene** Ausführung
- **404/409/422** + `{detail, code}` nur **vor** Ausführungsbeginn
- **Kein 409** mit Ergebnisobjekt am neuen Endpunkt
- Legacy 7.3b deprecated, Verhalten unverändert

## Entscheidung

### Endpunkt

```
POST /prueflaeufe/{prueflauf_id}/schritte/{schritt_id}/automatisierung/ausfuehren
```

| Regel | Detail |
|-------|--------|
| Use Case | ausschließlich `RoutineAusfuehren` |
| Identifikation | nur `prueflauf_id`, `schritt_id` |
| Kein `kommando_id`, `routine_id`, freier `kommandocode` | Automatisierung aus materialisiertem ProzedurSchritt |
| Request-Body | `{}` oder kein Body; `extra=forbid` |

### HTTP-Statusregeln

#### Fehler vor Ausführungsbeginn

| HTTP | Body | Persistenz |
|------|------|------------|
| 404 | `{detail, code}` | Rollback (ADR-0011) |
| 409 | `{detail, code}` | Rollback |
| 422 | `{detail, code}` | Rollback |

Keine `ausfuehrung_id`, keine Geräteaktion, keine neuen Nachweise.

Typische `code`-Werte: `prueflauf_nicht_gefunden`, `version_nicht_gefunden`, `materialisierter_prozedur_schritt_nicht_gefunden`, `keine_automatisierung_am_schritt`, `materialisierte_automatisierung_inkonsistent`, `invariant_verletzt`, `leere_routine`, `validation`.

#### Ausführung begonnen

| HTTP | Body |
|------|------|
| **200** | `AutomatisierungAusfuehrenResponse` (vollständig) |

Unabhängig von Erfolg oder Teilfehler. Teil-Evidenz wird committed. **Kein** `{detail, code}` im Ergebnis.

### Response-Schema `AutomatisierungAusfuehrenResponse`

| Feld | Typ | Regel |
|------|-----|-------|
| `ausfuehrung_id` | string (UUID) | Korrelation aller Nachweise dieses Aufrufs |
| `fehlgeschlagen` | bool | fachlicher Ausgang |
| `ausgefuehrte_aktionen` | int | erfolgreich abgeschlossene Aktionen |
| `abgebrochen_bei_aktion_position` | int \| null | null bei Erfolg |
| `fehlerart` | enum \| null | null bei Erfolg; sonst generisch |
| `nachweise` | list | neu in diesem Aufruf erzeugte Nachweise |

Zulässige `fehlerart`: `keine_geraeteantwort`, `geraetefehlschlag`, `ungueltige_antwort` — keine technischen Begriffe (COM, Timeout, PySerial).

### Idempotenz

- **Nicht idempotent** — jeder POST = neue `ausfuehrung_id`, neue Nachweis-Welle (ADR-0003)
- Kein serverseitiger Retry (ADR-0013)
- Kein Idempotency-Key in Gate 7.3f
- Clients dürfen bei unklarem Netzwerkfehler nicht blind wiederholen

### Legacy-Endpunkt (Gate 7.3b)

```
POST /prueflaeufe/{id}/schritte/{id}/kommandos/{kommando_id}/ausfuehren
```

| Aspekt | Regel |
|--------|-------|
| OpenAPI | `deprecated: true` |
| Verhalten | **unverändert** — kein Redirect, keine Delegation auf `RoutineAusfuehren` |
| Entfernung | nach Frontend-Migration; kein Datum in 7.3f |

#### Semantikdifferenz Legacy vs. Ziel

| Situation | Legacy 7.3b | Ziel 7.3f |
|-----------|-------------|-----------|
| Erfolg | 201, `{nachweise}` | 200, volles Ergebnis |
| Transport ohne Rohantwort | 409 `{detail,code}`, Rollback | 200, `fehlgeschlagen=true`, Commit |
| Gerätefehler mit Rohantwort | 409 `{detail,code,nachweise}` | 200, volles Ergebnis |
| Vor Ausführungsbeginn | 404/409 `{detail,code}` | 404/409/422 `{detail,code}` |

### Monitoring (Hinweis)

HTTP 200 bedeutet **nicht** automatisch fachlichen Erfolg. Metriken müssen `fehlgeschlagen` auswerten — keine Monitoring-Infrastruktur in Gate 7.3f.

### Route-Verantwortung

Nur: Request validieren → `RoutineAusfuehren` → Response mappen → HTTP 200. Keine Fachlogik.

## Konsequenzen

- Klare Trennung API-Fehler vs. fachliches Ausführungsergebnis
- OpenAPI ohne `oneOf`-Mischschema auf 200/409
- Frontend kann begonnene Teilausfälle als erfolgreiche HTTP-Antwort mit `fehlgeschlagen=true` behandeln (späterer Slice)

## Nicht-Ziele (Gate 7.3f)

Frontend, Legacy-Entfernung, Idempotency-Key, Retry, Pause/Resume, weitere Aktionsarten, GET auf `ausfuehrung_id`, Materialisierungs-Exit `externes_kommando`.

## Referenzen

- [ADR-0003](0003-routine-nachweis-wellen.md)
- [ADR-0011](0011-api-postgresql-unit-of-work.md)
- [ADR-0013](0013-com-adapter-wiring-fehlerabbildung.md)
- [ADR-0014](0014-routine-katalog-materialisierung.md)
- [ADR-0015](0015-routine-ausfuehren-application-runner.md)
