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

## Ports (Slice — Externes Kommando)

| Port | Adapter (V1) | Use Case |
|------|--------------|----------|
| `ExternesKommandoPort` | `adapters/simulation/externes_kommando.py` | `ExternesKommandoAusfuehren` |
| `ExternesKommandoPort` | `adapters/com/externes_kommando.py` | `ExternesKommandoAusfuehren` |
| `KatalogRepository` | — | `ExternesKommandoAusfuehren` (nur Version/Snapshot lesen) |

Gate 7.3b: Ausführung bindet `kommando_id` an materialisierten Snapshot in der `ProduktdefinitionsVersion` — **kein** Zugriff auf `BibliothekRepository` zur Laufzeit. Fehler für fehlende materialisierte Schritte liegen in `domain/pruefausfuehrung/errors.py` (`MaterialisierterProzedurSchrittNichtGefunden`), nicht im Katalog-Context.

Gate 7.3c: Adapterwahl ausschließlich in `api/kommando_wiring.py` (`create_kommando_port()`). Default: `SimuliertesExternesKommandoPort`. COM: `ComExternesKommandoPort` → `PySerialTransport` (optional Extra `[com]`). Transport-Lifecycle V1: **Port pro Kommando öffnen und schließen**. Technische Fehler → `ExternesKommandoAntwort(erfolgreich=False)`; Application → `ExternesKommandoAdapterFehler`. Kein automatischer Retry. Siehe [ADR-0013](../adr/0013-com-adapter-wiring-fehlerabbildung.md).

COM-Adapter nutzt injizierbaren `SeriellerTransport` (`adapters/com/transport.py`); Tests: `InMemorySeriellerTransport`; Produktion: `PySerialTransport`.

Laufzeit-VOs: `domain/pruefausfuehrung/kommando_ausfuehrung.py` (`ExternesKommandoAnfrage`, `ExternesKommandoAntwort`).

Invariante §4.11: Rohantwort → `NachweisArt.ROHANTWORT` (automatisch); extrahierte Werte → `EXTRAHIERTER_WERT` mit Bezug.

## Domain Events (V1)

Keine.

## Nicht im Domain-Kern (noch offen)

- Fotospeicher
- Vollständige Routine-Orchestrierung (folgt)

**Istbestückung** ist im Domain-Kern implementiert: `Prueflauf.erfasse_komponente()` (ADR-0006, Slice minimal).
