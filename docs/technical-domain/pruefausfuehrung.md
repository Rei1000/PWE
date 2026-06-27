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
| `set_beurteilung()` | Einmal pro Durchführung (V1) |
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

## Domain Events (V1)

Keine.

## Nicht im Domain-Kern

- COM, Fotospeicher, Sollvergleich-Algorithmus (Application/Domain-Service später)
- Istbestückung (ADR-0006 — folgt)
