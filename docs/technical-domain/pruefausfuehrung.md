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
| `ExternesKommandoPort` | `adapters/simulation/externes_kommando.py` | `ExternesKommandoAusfuehren`, `RoutineAusfuehren` |
| `ExternesKommandoPort` | `adapters/com/externes_kommando.py` | `ExternesKommandoAusfuehren`, `RoutineAusfuehren` |
| `KatalogRepository` | — | Version/Snapshot lesen |

Gate 7.3b: Ausführung bindet `kommando_id` an materialisierten Snapshot in der `ProduktdefinitionsVersion` — **kein** Zugriff auf `BibliothekRepository` zur Laufzeit. Fehler für fehlende materialisierte Schritte liegen in `domain/pruefausfuehrung/errors.py` (`MaterialisierterProzedurSchrittNichtGefunden`), nicht im Katalog-Context.

Gate 7.3c: Adapterwahl ausschließlich in `api/kommando_wiring.py` (`create_kommando_port()`). Default: `SimuliertesExternesKommandoPort`. COM: `ComExternesKommandoPort` → `PySerialTransport` (optional Extra `[com]`). Transport-Lifecycle V1: **Port pro Kommando öffnen und schließen**. Technische Fehler ohne Geräte-Rohdaten → `ExternesKommandoAntwort(erfolgreich=False, rohdaten="")`; Application Einzelkommando wirft `ExternesKommandoAdapterFehler`. **Empfangene Geräte-Rohantwort** wird immer als ROHANTWORT-Nachweis persistiert (Domain Invariante 16), auch bei `erfolgreich=False`; Application liefert `ExternesKommandoAusfuehrungErgebnis`, API 409 mit `nachweise` ohne Exception-Rollback. Siehe [ADR-0013](../adr/0013-com-adapter-wiring-fehlerabbildung.md).

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
| API | Nicht in 7.3e — Gate 7.3f |

Ergebnis-Contract: `RoutineAusfuehrungErgebnis` — `ausfuehrung_id`, `nachweise`, `fehlgeschlagen`, `abgebrochen_bei_aktion_position`, `ausgefuehrte_aktionen`, optionale fachliche `fehlerart` (`keine_geraeteantwort`, `geraetefehlschlag`, `ungueltige_antwort`).

### Vorbedingungen vor externen Seiteneffekten (ADR-0015)

Alle lokal prüfbaren Domain-Invarianten werden **vor** dem ersten `ExternesKommandoPort`-Aufruf validiert. Ein Datenbank-Rollback kann irreversible Geräteaktionen nicht kompensieren.

Domain-API: `Prueflauf.stelle_offen_sicher()` — öffentliche Vorbedingungsprüfung, identisch zu `_ensure_offen()` bei Mutationen.

Use Cases validieren in fester Reihenfolge: laden → Katalog/Snapshot → Offenheit → erst dann Port (siehe ADR-0015). Die Kommando-Kernlogik wiederholt `stelle_offen_sicher()` unmittelbar vor dem Port-Aufruf.

## Domain Events (V1)

Keine.

## Nicht im Domain-Kern (noch offen)

- Fotospeicher
- Schrittzentrierte Routine-API (Gate 7.3f)

**Istbestückung** ist im Domain-Kern implementiert: `Prueflauf.erfasse_komponente()` (ADR-0006, Slice minimal).
