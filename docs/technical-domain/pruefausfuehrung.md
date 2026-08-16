# Technical Domain — Prüfausführung

Brücke Domain Model → Code. Fachliche Referenz: `docs/domain-model.md` §4.15–§4.18, §9.

## Konsistenzgrenzen

| Grenze | Begründung |
|--------|------------|
| **Prueflauf** ist Aggregate Root | §4.15 — enthält Durchführungen, Nachweise, Beurteilungen |
| Versionsreferenz unveränderlich | §4.15 Invariante |
| Eine **PruefschrittDurchfuehrung** pro ProzedurSchritt | ADR-0003 |
| Nachweise akkumulieren (Wellen), automatische unveränderlich | §4.17, ADR-0003 |
| Beurteilung festgelegt vor Schrittabschluss; Lauf unveränderlich nach Abschluss | §4.18, §4.15 |
| Nachweis ≠ Beurteilung | §11 |

## Aggregate Root

**`Prueflauf`** — `domain/pruefausfuehrung/prueflauf.py`

| Methode | Regel |
|---------|-------|
| `starten()` | Legt Durchführungen für alle aktiven ProzedurSchritte an |
| `stelle_offen_sicher()` | Vor externen Seiteneffekten — wirft bei abgeschlossenem Lauf |
| `add_nachweis()` | Nur bei offenem Lauf; Wellen via append |
| `beurteilen_schritt(schritt_id, sollvorgaben)` | ADR-0007 — Beurteilung via `BeurteilungService` |
| `erfasse_komponente(typ, seriennummer)` | ADR-0006 — Istbestückung |
| `to_abschluss_view(pflicht_map)` | ADR-0008 — Übergabe an Protokoll |
| `abschliessen()` | Pflichtschritte müssen beurteilt sein; NICHT_BESTANDEN → ungültig |

## Entities / Value Objects

| Typ | Name |
|-----|------|
| Entity (innerhalb Root) | `PruefschrittDurchfuehrung` |
| VO | `Nachweis` (immutable wenn automatisch) |
| Entity | `Beurteilung` (Teil der Durchführung) |
| Enum | `PrueflaufStatus`, `NachweisArt`, `BeurteilungErgebnis` |

## Repository

`PrueflaufRepository` — `save`, `get`

## Ports (Slice — Externes Kommando / Routine)

| Port | Adapter (V1) | Use Case |
|------|--------------|----------|
| `ExternesKommandoPort` | `adapters/simulation/externes_kommando.py` | `RoutineAusfuehren` |
| `ExternesKommandoPort` | `adapters/com/externes_kommando.py` | `RoutineAusfuehren` |
| `KatalogRepository` | — | Version/Snapshot lesen |

Gate 7.3b: Ausführung bindet `kommando_id` an materialisierten Snapshot in der `ProduktdefinitionsVersion` — **kein** Zugriff auf `BibliothekRepository` zur Laufzeit. Fehler für fehlende materialisierte Schritte liegen in `domain/pruefausfuehrung/errors.py` (`MaterialisierterProzedurSchrittNichtGefunden`), nicht im Katalog-Context.

Gate 7.3c: Adapterwahl ausschließlich in `api/kommando_wiring.py` (`create_kommando_port()`). Default: `SimuliertesExternesKommandoPort`. COM: `ComExternesKommandoPort` → `PySerialTransport` (optional Extra `[com]`). Transport-Lifecycle V1: **Port pro Kommando öffnen und schließen**. Technische Fehler ohne Geräte-Rohdaten → `ExternesKommandoAntwort(erfolgreich=False, rohdaten="")`. **Empfangene Geräte-Rohantwort** wird immer als ROHANTWORT-Nachweis persistiert (Domain Invariante 16), auch bei `erfolgreich=False`; fachlicher Ausgang über `RoutineAusfuehrungErgebnis.fehlgeschlagen` (ADR-0016: HTTP 200). Siehe [ADR-0013](../adr/0013-com-adapter-wiring-fehlerabbildung.md).

COM-Adapter nutzt injizierbaren `SeriellerTransport` (`adapters/com/transport.py`); Tests: `InMemorySeriellerTransport`; Produktion: `PySerialTransport`.

Laufzeit-VOs: `domain/pruefausfuehrung/kommando_ausfuehrung.py` (`ExternesKommandoAnfrage`, `ExternesKommandoAntwort`).

Invariante §4.11: Rohantwort → `NachweisArt.ROHANTWORT` (automatisch); extrahierte Werte → `EXTRAHIERTER_WERT` mit Bezug.

## Gate 7.3e — RoutineAusfuehren (ADR-0015)

| Aspekt | Entscheidung |
|--------|--------------|
| Use Case | `application/pruefausfuehrung/routine_ausfuehren.py` |
| Run-Time-Aggregate | **Keins** — `Prueflauf` bleibt einziger Root |
| Ausführungsvorgabe | `aufgeloeste_materialisierte_routine(schritt)` — zentrale Domain-Normalisierung |
| Kernlogik | `kommandoausfuehrung_kern` — intern, kein save/load |
| Speicherung | Genau ein `save(prueflauf)` pro Aufruf |
| Dispatch | Explizite Schleife über Kommando-Aktionen — keine Handler-Registry |
| Fehler vor Beginn | Exception (Rollback) |
| Fehler nach Beginn | `RoutineAusfuehrungErgebnis` — auch Transport ohne Rohantwort bei erster Aktion |
| Audit | Payload-Abschnitt `automatisierung` mit `ausfuehrung_id`, `herkunft`, `aktion_position`, `kommando_id`, optional `routine_id` |
| API | Gate 7.3f — [ADR-0016](../adr/0016-automatisierung-http-api.md), `POST .../automatisierung/ausfuehren` |

Ergebnis-Contract: `RoutineAusfuehrungErgebnis` — `ausfuehrung_id`, `nachweise`, `fehlgeschlagen`, `abgebrochen_bei_aktion_position`, `ausgefuehrte_aktionen`, optionale fachliche `fehlerart` (`keine_geraeteantwort`, `geraetefehlschlag`, `ungueltige_antwort`).

### Vorbedingungen vor externen Seiteneffekten (ADR-0015)

Alle lokal prüfbaren Domain-Invarianten werden **vor** dem ersten `ExternesKommandoPort`-Aufruf validiert. Ein Datenbank-Rollback kann irreversible Geräteaktionen nicht kompensieren.

Domain-API: `Prueflauf.stelle_offen_sicher()` — öffentliche Vorbedingungsprüfung, identisch zu `_ensure_offen()` bei Mutationen.

Use Cases validieren in fester Reihenfolge: laden → Katalog/Snapshot → Offenheit → erst dann Port (siehe ADR-0015). Die Kommando-Kernlogik wiederholt `stelle_offen_sicher()` unmittelbar vor dem Port-Aufruf.

## Domain Events (V1)

Keine.

## Nicht im Domain-Kern (noch offen)

- Fotospeicher

**Schrittzentrierte Automatisierungs-API** ist der alleinige Run-Time-HTTP-Contract (Gate 7.3f / ADR-0016). Legacy-Einzelkommando-HTTP entfernt in Gate 7.4a ([ADR-0018](../adr/0018-legacy-automatisierung-exit.md)). Legacy-Versionen mit ausschließlich `externes_kommando` bleiben über `aufgeloeste_materialisierte_routine()` les- und ausführbar; Write Exit = Gate 7.4b.

**Istbestückung** ist im Domain-Kern implementiert: `Prueflauf.erfasse_komponente()` (ADR-0006, Slice minimal).

Gate 6.3b — Frontend-Ausführung / Read-Model-Flags

| Feld | Bedeutung |
|------|-----------|
| `hat_automatisierung` | Fachlich: Schritt besitzt auflösbare Automatisierung via `aufgeloeste_materialisierte_routine` (inkl. Legacy). Inkonsistenz wird nicht verschluckt. |
| `kann_automatisierung_ausfuehren` | **UI-Führungsflag** (Variante B): offener Prüflauf und vollständige Istbestückung laut Read-Model-Führung. |
| `automatisierung_bezeichnung` | Optionale Anzeigehilfe aus der materialisierten Routine |

**Bewusste Trennung:** Fehlende Komponenten blockieren **nicht** `RoutineAusfuehren` / den öffentlichen POST-Endpunkt. Die API bleibt technisch aufrufbar. Das Read-Model-Flag spiegelt die bestehende Prüferführung („Komponenten zuerst“), analog zu `kann_nachweis_erfassen` — keine zusätzliche Domain-Invariante.

### Frontend-Semantik (ADR-0016)

- HTTP 200 inkl. `fehlgeschlagen=true` → typisiertes Ergebnis, **kein** `ApiError`
- 4xx vor Ausführungsbeginn → `ApiError` / `{detail, code}`
- Mutation: `retry: false`; Doppelklick gesperrt während Pending
- Nicht-Idempotenz: Hinweis auf neue Nachweis-Welle; bei Netzwerkfehler Read-Model invalidieren, **nicht** automatisch erneut ausführen
- Prüfer-UI nutzt **keinen** Katalog-Setup-Endpunkt (Gate 6.3a) und **keinen** Legacy-Kommando-Endpunkt
- Demo-/Seed-Orchestrierung: Gate 6.3c

## Gate 6.3c — Demo-/Labor-Seed

| Aspekt | Regel |
|--------|-------|
| Einstieg | `scripts/seed_demo_automatisierung.py` — externer HTTP-Client |
| Contracts | ausschließlich öffentliche Katalog-/Prüflauf-HTTP (ADR-0017, ADR-0016) |
| Simulation | nur mit `PWE_DEMO_MODE=true` und Adapter `simulation`: feste Antwort für `DEMO_MESSWERT` |
| Default | `PWE_DEMO_MODE` fehlt/false → **keine** Demo-Antworten |
| Idempotenz | **nicht** idempotent; erneutes Seeden erzeugt neue Objekte; aktive Version der Demo-Kodierung wird ersetzt |
| Fehler | Schritt stoppt; keine Multi-Request-Kompensation |
| Abgrenzung | Labor/Demo/Schulung — **kein** Ersatz für Gate 8.2 Katalog-Admin |
| StartPage | bewusst nicht erweitert (P1) |
