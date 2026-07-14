# ADR-0015: RoutineAusfuehren — Application Runner (Gate 7.3e)

## Status

Angenommen (Gate 7.3e)

## Kontext

Gate 7.3d hat `MaterialisierteRoutine` als einheitlichen Automatisierungs-Snapshot etabliert. Gate 7.3b führt weiterhin Einzelkommandos über `kommando_id` aus. Eine Architekturprüfung hat für Gate 7.3e entschieden:

- Application Use Case `RoutineAusfuehren`, kein Run-Time-Aggregate für Routinen
- `Prueflauf` bleibt einziger Run-Time Aggregate Root
- Zentrale Legacy-Normalisierung im Katalogmodell
- Gemeinsame interne Kommando-Kernlogik für Einzelkommando und Routine
- Nach Ausführungsbeginn: Aktionsfehler als Ergebnis, nicht als Exception
- Gate 7.3f mappt Ergebnis-Semantik später auf HTTP

## Entscheidung

### Form und Verantwortlichkeiten

| Aspekt | Entscheidung |
|--------|--------------|
| Use Case | `RoutineAusfuehren` — Application Layer |
| Run-Time-Aggregate | **Keins** — kein `RoutineFortschritt`, kein persistierter Routine-Run |
| Aggregate Root | **`Prueflauf`** — einziger Run-Time-Root |
| Ausführungsvorgabe | **`MaterialisierteRoutine`** — aufgelöst aus materialisiertem ProzedurSchritt |
| Speicherung | Genau **ein** `save(prueflauf)` pro Use-Case-Aufruf durch den aufrufenden Use Case |
| API | **Nicht** in Gate 7.3e — HTTP kommt in Gate 7.3f |

### Zentrale Legacy-Normalisierung

Eine einzige Domain-Funktion im materialisierten Katalogmodell:

`aufgeloeste_materialisierte_routine(schritt)` in `domain/katalog/materialisierung.py`

| Situation | Verhalten |
|-----------|-----------|
| `materialisierte_routine` vorhanden | Kompatibilitätsinvariante prüfen (Gate 7.3d), Routine zurückgeben |
| Nur `externes_kommando` (Legacy) | Synthetische Ein-Aktions-Routine, `herkunft=einzelkommando`, Position 1, keine künstliche `routine_id` |
| Beide vorhanden, inkonsistent | `MaterialisierteAutomatisierungInkonsistent` |
| Keine Automatisierung | `KeineAutomatisierungAmSchritt` |

Keine zweite Normalisierung in Application Layer oder Mapper.

### Gemeinsame Kommando-Kernlogik

Interne Funktion `kommandoausfuehrung_kern` (kein öffentlicher Use Case):

- Erhält: geöffneten `Prueflauf`, `schritt_id`, materialisierten Kommando-Snapshot, `ExternesKommandoPort`, Audit-Kontext
- Darf **nicht**: Repositories laden/speichern, Transaktionen committen, HTTP/COM kennen
- Verantwortlich: Port-Aufruf, Interpretation `ExternesKommandoAntwort`, Rohantwort-/Extraktions-Nachweise, Audit-Metadaten, generische Fehlerklassifikation

`ExternesKommandoAusfuehren` und `RoutineAusfuehren` nutzen dieselbe Kernlogik.

### Audit-Kontext (`automatisierung` im Nachweis-Payload)

Jeder automatisch erzeugte Nachweis enthält strukturiert:

```json
{
  "automatisierung": {
    "ausfuehrung_id": "<UUID pro Use-Case-Aufruf>",
    "herkunft": "bibliothek | einzelkommando",
    "aktion_position": 1,
    "kommando_id": "...",
    "routine_id": "..." 
  }
}
```

| Herkunft | Regeln |
|----------|--------|
| `bibliothek` | `routine_id` Pflicht |
| `einzelkommando` | keine künstliche `routine_id`, `aktion_position=1` |

- Pro Aufruf von `RoutineAusfuehren` und `ExternesKommandoAusfuehren`: neue `ausfuehrung_id`
- Alle Nachweise desselben Aufrufs tragen dieselbe Kennung
- Keine neue Entity oder Aggregate Root
- Manuelle Nachweise: **kein** Automatisierungsblock

Bestehende fachliche Payload-Inhalte (`kommando_id`, `kommandocode`, `rohdaten`, …) bleiben erhalten.

### Ausführungsmodell

| Regel | Detail |
|-------|--------|
| Modus | Synchron, sequenziell nach Aktionsposition |
| Aktionsarten Gate 7.3e | Nur materialisierte Kommando-Aktionen |
| Dispatch | Explizite Schleife — **keine Handler-Registry** |
| Fehlerstrategie | Stop-on-first-action-failure |
| Mid-Request-Commits | **Nein** |
| Versteckte Retries | **Nein** |

Registry frühestens neu bewerten, wenn eine **zweite echte Aktionsart** existiert.

### Ergebnis-Contract (`RoutineAusfuehrungErgebnis`)

| Feld | Bedeutung |
|------|-----------|
| `ausfuehrung_id` | Korrelation aller Nachweise dieses Aufrufs |
| `nachweise` | In diesem Aufruf neu erzeugte Nachweise |
| `fehlgeschlagen` | Eindeutiger Status (`erfolgreich = not fehlgeschlagen`) |
| `abgebrochen_bei_aktion_position` | Position bei Abbruch, sonst `None` |
| `ausgefuehrte_aktionen` | Anzahl erfolgreich abgeschlossener Aktionen |
| `fehlerart` | Optional, fachlich generisch — keine technischen Begriffe (COM, Timeout, PySerial) |

Zulässige `fehlerart`-Werte: `keine_geraeteantwort`, `geraetefehlschlag`, `ungueltige_antwort`.

### Transaktions- und Fehlerregeln

**Exceptions (Rollback) — vor Ausführungsbeginn:**

- Prüflauf / Version / Schritt nicht gefunden
- Keine Automatisierung am Schritt
- Inkonsistente Materialisierung
- Abgeschlossener Prüflauf
- Leere oder ungültige Routine vor dem ersten Port-Aufruf

**Ausführungsbeginn:** materialisierte Routine erfolgreich aufgelöst, Prüflauf als offen validiert — ab dann auch Transportfehler ohne Rohantwort bei der **ersten** Aktion → `RoutineAusfuehrungErgebnis`, kein Exception-Rollback.

**Ergebnis statt Exception — nach Ausführungsbeginn:**

- Transportfehler ohne Rohantwort
- Geräte-ERR mit Rohantwort
- Parserfehler mit Rohantwort
- Sonstiger generischer Adapterfehler mit klassifizierbarer Fehlerart

**Evidenz:**

- Bereits erzeugte Nachweise werden **niemals** durch späteren Aktionsfehler zurückgerollt
- Rohantwort mit Gerätedaten → ROHANTWORT-Nachweis
- Fehler ohne Rohantwort → kein fingierter Nachweis
- Erneuter Routineaufruf → neue `ausfuehrung_id`, neue Nachweise an dieselbe Durchführung

### Einzelkommando-Pfad (Gate 7.3b)

`ExternesKommandoAusfuehren` nutzt dieselbe Kernlogik und dasselbe Audit-Schema:

- HTTP-Contract Gate 7.3b **unverändert**
- Audit-Regel Gate 7.3c **unverändert** (Transport ohne Rohantwort → Exception → API 409 Rollback)
- `kommando_id` weiter gegen materialisierten Snapshot validiert
- Pro Aufruf neue `ausfuehrung_id`, `herkunft=einzelkommando`, `aktion_position=1`

### Gate 7.3f (Ausblick)

HTTP-Endpunkt für schrittzentrierte Routine-Ausführung mappt `RoutineAusfuehrungErgebnis` auf Statuscodes — nicht Teil von 7.3e.

## Konsequenzen

- Ein einheitlicher Ergebnis-Contract für alle **begonnenen** Routineausführungen
- Keine doppelte Nachweislogik zwischen Einzelkommando und Routine
- Legacy-Versionen werden zentral normalisiert — keine stille Feldauswahl
- ADR-0014 Exit-Strategie für `externes_kommando` bleibt; Runner liest über `aufgeloeste_materialisierte_routine`

## Referenzen

- [ADR-0014](0014-routine-katalog-materialisierung.md)
- [ADR-0013](0013-com-adapter-wiring-fehlerabbildung.md)
- `docs/technical-domain/pruefausfuehrung.md`
- `docs/technical-domain/katalog.md`
