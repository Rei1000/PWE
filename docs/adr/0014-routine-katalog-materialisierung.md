# ADR-0014: Routine — Katalogmodell und einheitliche Materialisierung (Variante D)

## Status

Angenommen (Gate 7.3d)

## Kontext

Gate 7.3a–7.3c haben `ExternesKommando` als Bibliotheksobjekt und die API-Ausführung über `kommando_id` auf materialisiertem Snapshot etabliert. Domain Model §4.10 definiert `Routine` als geordnete Aktionsfolge im Katalog-Bibliotheksmodul. Eine Architekturprüfung (Variante D) hat entschieden:

- Entwurf: `kommando_id` **oder** `routine_id` (gegenseitig exklusiv)
- Materialisierte Version: **immer** einheitlicher `MaterialisierteRoutine`-Snapshot
- Einzelkommando → synthetische Ein-Aktions-Routine
- Laufzeit: Application-Orchestrierung ohne Run-Time-Aggregate (Gate 7.3e)
- Gate 7.3b-Endpunkt bleibt vorerst kompatibel

## Entscheidung

### Bibliotheksmodul

| Aspekt | Entscheidung |
|--------|--------------|
| Aggregate Root | `Routine` im Katalog-Bibliotheksmodul (ADR-0012-Muster) |
| Inhalt | Geordnete Folge fachlicher Aktionen |
| Gate 7.3d | Nur Aktionsart `ExternesKommandoAusfuehren` |
| Repository | `BibliothekRepository.save_routine` / `get_routine` — keine separaten Ports |
| Semantik | Mutable save (wie `ExternesKommando`) |

### Entwurf (`ProzedurSchrittEntwurf`)

| Regel | Detail |
|-------|--------|
| Referenzen | Optional `kommando_id` **oder** optional `routine_id` |
| XOR | Höchstens eine der beiden — frühe Validierung bei Zuweisung |
| Manuell | Beide leer erlaubt (rein manueller Schritt) |
| **Wechsel** | **Keine stille Ersetzung** (projektrules §6). Neue Zuweisung schlägt fehl, wenn die andere Referenz gesetzt ist → `AutomatisierungDoppeltZugewiesen`. Wechsel erfordert **zwei explizite Schritte**: zuerst Entfernen (`None`), dann neue Zuweisung. |

`AutomatisierungDoppeltZugewiesen` wird ausgelöst bei:
- gleichzeitig gesetzter `kommando_id` und `routine_id` (Entwurfs-Invariante, Veröffentlichen),
- Zuweisungsversuch einer Referenz, während die andere noch gesetzt ist.

### Materialisierung (`MaterialisierterProzedurSchritt`)

| Pfad | Ergebnis |
|------|----------|
| `routine_id` | `MaterialisierteRoutine` mit `herkunft=bibliothek`, `routine_id` gesetzt; alle Kommandos aufgelöst und eingebettet |
| `kommando_id` | `MaterialisierteRoutine` mit `herkunft=einzelkommando`, **keine** erfundene `routine_id`; eine Kommando-Aktion |
| Keine Automatisierung | `materialisierte_routine=None` |

**Herkunft** (`MaterialisierteRoutineHerkunft`):

- `bibliothek` — aus Bibliotheksroutine; `routine_id` vorhanden
- `einzelkommando` — synthetisch aus direkter `kommando_id`; **keine** künstliche Bibliotheks-`routine_id`

### Rückwärtskompatibilität Gate 7.3b

| Feld | Status |
|------|--------|
| `materialisierte_routine` | **Führend** — einheitlicher Automatisierungs-Snapshot |
| `externes_kommando` | **Deprecated** — wird bei `herkunft=einzelkommando` weiterhin gesetzt, damit Gate 7.3b unverändert funktioniert |

Keine dauerhafte doppelte Wahrheit: `externes_kommando` ist abgeleiteter Kompatibilitäts-Snapshot aus der ersten Kommando-Aktion bei Einzelkommando-Pfad. Laufzeit Gate 7.3e+ arbeitet gegen `materialisierte_routine`.

### Kompatibilitätsinvariante (materialisierter Schritt)

| Situation | Regel |
|-----------|-------|
| Neu (Einzelkommando) | `materialisierte_routine` führend; `externes_kommando` abgeleitet aus erster Aktion — muss identisch sein |
| Neu (Bibliotheksroutine) | nur `materialisierte_routine`; `externes_kommando=None` |
| Legacy (pre-7.3d) | nur `externes_kommando`, `materialisierte_routine=None` — lesbar |
| Beide gesetzt, abweichend | `MaterialisierteAutomatisierungInkonsistent` — nie still akzeptiert |
| Beide gesetzt bei Bibliotheksroutine | `MaterialisierteAutomatisierungInkonsistent` |

Validierung: `validiere_materialisierter_schritt_automatisierung()` bei Materialisierung und Deserialisierung.

**Exit-Strategie:**
- Gate 7.3e: Runner normalisiert Legacy über `aufgeloeste_materialisierte_routine()` — siehe [ADR-0015](0015-routine-ausfuehren-application-runner.md)
- Gate 7.3f: Entscheidung, wann `externes_kommando` nicht mehr geschrieben wird
- Gate 7.3b-Endpunkt: deprecated, Entfernung nach schrittzentrierter API

### Laufzeit (bewusst nicht in 7.3d)

- Kein Run-Time-Aggregate `Routine`
- Orchestrierung in Application Layer (Gate 7.3e)
- API langfristig schrittzentriert (Gate 7.3f); Gate 7.3b-Endpunkt bleibt vorerst

## Begründung

- Einheitlicher materialisierter Automatisierungspfad (Variante D) ohne Big-Bang-Migration von 7.3a/b
- XOR nur auf Entwurfsebene — Admin-Mehrdeutigkeit vermeiden
- Vollständige Snapshot-Materialisierung für Audit und Unabhängigkeit von Bibliotheksänderungen (Domain §10)
- Klare Herkunft unterscheidet Bibliotheksroutine von synthetischer Ein-Aktions-Routine

## Konsequenzen

- `ProduktdefinitionVeroeffentlichen` löst Routinen und Kommandos aus `BibliothekRepository` auf
- PostgreSQL: Tabelle `routine`; JSON-Payload in Entwurf/Version enthält `routine_id` bzw. `materialisierte_routine`
- Neue Domain-Fehler: `RoutineNichtGefunden`, `KommandoInRoutineNichtGefunden`, `AutomatisierungDoppeltZugewiesen`, `MaterialisierteAutomatisierungInkonsistent`, `LeereRoutine`, `UngueltigeAktionsreihenfolge`
- Gate 7.3e: Runner liest `materialisierte_routine`; Gate 7.3f: schrittzentrierte API

## Bezug

- Domain Model §4.8, §4.10, §10
- [ADR-0012](0012-katalog-bibliothek-externes-kommando.md) — Bibliotheks-Modul, Facade
- [ADR-0003](0003-routine-nachweis-wellen.md) — Wiederholung auf Schritt-Ebene
- Gate 7.3b — Kompatibilität über deprecated `externes_kommando`
