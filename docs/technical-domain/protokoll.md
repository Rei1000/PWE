# Technical Domain — Protokoll

Brücke Domain Model → Code. Fachliche Referenz: `docs/domain-model.md` §4.19. ADR: ADR-0004.

## Konsistenzgrenzen

| Grenze | Begründung |
|--------|------------|
| **ProtokollSnapshot** unveränderlich nach Erstellung | §4.19 |
| Entsteht bei **jedem** Laufabschluss (auch ungültig) | §4.19, §2 |
| Referenziert Version + Nachweis-IDs, keine Medienbinaries | ADR-0004 |

## Aggregate Root

**`ProtokollSnapshot`** — `domain/protokoll/snapshot.py`

Factory: `ProtokollSnapshot.aus_abschluss(view)` — importiert nur `PrueflaufAbschlussView`, nicht `Prueflauf` (ADR-0008).

## Value Objects

| Name | Inhalt |
|------|--------|
| `SchrittSnapshot` | Schritt-ID, Pflicht-Flag, Beurteilung, Nachweis-IDs |
| `ProtokollSnapshot` | Metadaten + Schritt-Snapshots |

## Repository

`ProtokollRepository` — `save`, `get_by_prueflauf`

## Abgrenzung

PDF-Erzeugung = Adapter (`ProtokollErzeugungPort`), nicht Domain.

## Offen

- Denormalisierungstiefe für Langzeitarchiv (ADR-0004 erlaubt Erweiterung)
- Mehrsprachige Snapshot-Darstellung
