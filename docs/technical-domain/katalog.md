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
| `ProduktdefinitionsVersion` | Materialisierte Prüfvorgabe | `domain/katalog/version.py` |

V1-Slice: Version wird als **immutable Dataclass** modelliert; Veröffentlichungsakt (Entwurf → Version) folgt in Katalog-Slice 2.

## Entities / Value Objects

| Typ | Name | Anmerkung |
|-----|------|-----------|
| VO | `MaterialisierterProzedurSchritt` | Enthält aufgelöste Sollvorgaben |
| VO | `ProduktdefinitionsVersion` | Root im Slice; später ggf. Publish-Service |

## Repository

| Port | Methode (V1) |
|------|--------------|
| `KatalogRepository` | `get_aktive_version_fuer_kodierung`, `save_version` |

## Domain Events (V1)

Keine — erst bei Persistenz/Event-Integration.

## Offen (nach V1-Slice)

- Produktdefinition (Entwurf) als editierbares Aggregate
- Aktivierungsregeln-Auswertung zur Laufzeit
- Bibliothek (PrüfschrittVorlage, Routine, ExternesKommando)
