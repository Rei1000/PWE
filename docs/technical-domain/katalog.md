# Technical Domain — Katalog

Brücke Domain Model → Code. Fachliche Referenz: `docs/domain-model.md` §4.1–§4.14, §10.

## Konsistenzgrenzen

| Grenze | Begründung (Domain Model) |
|--------|---------------------------|
| **ProduktdefinitionsVersion** ist unveränderlich nach Veröffentlichung | §4.7, §10 |
| Entwurf (Produktdefinition) ≠ Version | §4.6 vs §4.7 |
| Materialisierung bei Veröffentlichung | ADR-0005 |

## Aggregate Roots (V1-Slice)

| Root | Verantwortung | Code |
|------|---------------|------|
| `Produktdefinition` | Editierbarer Entwurf | `domain/katalog/produktdefinition.py` |
| `ProduktdefinitionsVersion` | Materialisierte Prüfvorgabe | `domain/katalog/version.py` |

Veröffentlichungsakt (Entwurf → Version): Katalog-Slice 2 — `Produktdefinition.veroeffentlichen()`, Use Cases in `application/katalog/`.

## Entities / Value Objects

| Typ | Name | Anmerkung |
|-----|------|-----------|
| Entity | `Produktdefinition` | Root im Slice 2; mutable Entwurf |
| VO | `ProzedurSchrittEntwurf` | Schritt im Entwurf |
| VO | `MaterialisierterProzedurSchritt` | Enthält aufgelöste Sollvorgaben |
| VO | `ProduktdefinitionsVersion` | Immutable nach Veröffentlichung |
| Service | `materialisiere_sollvorgaben` | ADR-0005 Auflösungskette |

## Repository

| Port | Methode (V1) |
|------|--------------|
| `KatalogRepository` | `get_aktive_version_fuer_kodierung`, `get_version`, `save_version`, `get_entwurf`, `save_entwurf` |

## Application (Slice 2)

| Use Case | Datei |
|----------|-------|
| Entwurf anlegen | `application/katalog/entwurf_anlegen.py` |
| Veröffentlichen | `application/katalog/veroeffentlichen.py` |

## Domain Events (V1)

Keine — erst bei Persistenz/Event-Integration.

## Offen (nach Slice 2)

- Bibliothek (PrüfschrittVorlage, Routine, ExternesKommando)
- Aktivierungsregeln-Auswertung zur Laufzeit
- Version deaktivieren (V1: neue Version ersetzt aktive)
