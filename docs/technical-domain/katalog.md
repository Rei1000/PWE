# Technical Domain — Katalog

Brücke Domain Model → Code. Fachliche Referenz: `docs/domain-model.md` §4.1–§4.14, §10.

## Konsistenzgrenzen

| Grenze | Begründung (Domain Model) |
|--------|---------------------------|
| **ProduktdefinitionsVersion** ist unveränderlich nach Veröffentlichung | §4.7, §10 |
| Entwurf (Produktdefinition) ≠ Version | §4.6 vs §4.7 |
| Materialisierung bei Veröffentlichung | ADR-0005, ADR-0012 |
| Bibliothek (Design Time) ≠ Ausführung (Run Time) | ADR-0012, `ExternesKommandoPort` |

## Aggregate Roots (V1-Slice)

| Root | Verantwortung | Code |
|------|---------------|------|
| `Produktdefinition` | Editierbarer Entwurf | `domain/katalog/produktdefinition.py` |
| `ProduktdefinitionsVersion` | Materialisierte Prüfvorgabe | `domain/katalog/version.py` |
| `ExternesKommando` | Bibliothek — externes Gerätekommando | `domain/katalog/externes_kommando.py` |

Veröffentlichungsakt (Entwurf → Version): Katalog-Slice 2 + Gate 7.3a — `Produktdefinition.veroeffentlichen()`, Use Cases in `application/katalog/`.

## Entities / Value Objects

| Typ | Name | Anmerkung |
|-----|------|-----------|
| Entity | `Produktdefinition` | Root im Slice 2; mutable Entwurf |
| VO | `ProzedurSchrittEntwurf` | Schritt im Entwurf; optionale `kommando_id` |
| VO | `MaterialisierterProzedurSchritt` | Aufgelöste Sollvorgaben; optional `MaterialisiertesExternesKommando` |
| VO | `MaterialisiertesExternesKommando` | Snapshot bei Veröffentlichung (id, Bezeichnung, Kommandocode) |
| VO | `ProduktdefinitionsVersion` | Immutable nach Veröffentlichung |
| AR | `ExternesKommando` | Mutable Bibliothek; stabile `kommando_id` |
| Service | `materialisiere_sollvorgaben` | ADR-0005 Auflösungskette |

## Repository

| Port | Methode (V1) |
|------|--------------|
| `KatalogRepository` | `get_aktive_version_fuer_kodierung`, `get_version`, `save_version`, `get_entwurf`, `save_entwurf` |
| `BibliothekRepository` | `save_externes_kommando`, `get_externes_kommando` |

`BibliothekRepository` ist fachliche Facade des **Bibliotheks-Moduls** innerhalb des Katalog-Bounded-Contexts — kein eigener Context, kein Mega-Aggregat, kein separates Repository pro Typ (ADR-0012).

### Repository-Semantik

| Objekt | Port / Methode | Semantik |
|--------|----------------|----------|
| Produktdefinition (Entwurf) | `KatalogRepository.save_entwurf` | Mutable save |
| Bibliotheksobjekte | `BibliothekRepository.save_*` | Mutable save |
| ProduktdefinitionsVersion | `KatalogRepository.save_version` | Insert-only |
| Materialisierte Snapshots in Version | — | Unveränderlich nach Veröffentlichung |

Adapter dürfen mutable save technisch per INSERT/UPDATE oder SQL-Upsert umsetzen — der Port-Contract spricht nur von **save**.

### Kommando-Snapshot (`MaterialisiertesExternesKommando`)

| Feld | Begründung |
|------|------------|
| `kommando_id` | Stabile Identität der Bibliotheksdefinition; Korrelation Entwurf→Version; Basis für API-Ausführung in Gate 7.3b |
| `bezeichnung` | Menschlesbare Beschreibung für Prüferführung, Protokoll und Audit ohne Bibliotheks-Lookup |
| `kommandocode` | Ausführungsinhalt für `ExternesKommandoPort` zum Veröffentlichungszeitpunkt |

## Application (Slice 2 + Gate 7.3a)

| Use Case | Datei |
|----------|-------|
| Entwurf anlegen | `application/katalog/entwurf_anlegen.py` |
| Veröffentlichen | `application/katalog/veroeffentlichen.py` |
| Externes Kommando anlegen | `application/katalog/externes_kommando_anlegen.py` |
| Kommando an ProzedurSchritt zuweisen | `application/katalog/kommando_zuweisen.py` |

## Domain Events (V1)

Keine — erst bei Persistenz/Event-Integration.

## Offen (nach Gate 7.3a)

- `Routine`, `PrüfschrittVorlage` in Bibliothek (Gate 7.3 / 8.2)
- HTTP-Ausführung über `kommando_id` (Gate 7.3b)
- Aktivierungsregeln-Auswertung zur Laufzeit
- Version deaktivieren (V1: neue Version ersetzt aktive)
