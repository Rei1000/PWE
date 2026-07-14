# Technical Domain — Katalog

Brücke Domain Model → Code. Fachliche Referenz: `docs/domain-model.md` §4.1–§4.14, §10.

## Konsistenzgrenzen

| Grenze | Begründung (Domain Model) |
|--------|---------------------------|
| **ProduktdefinitionsVersion** ist unveränderlich nach Veröffentlichung | §4.7, §10 |
| Entwurf (Produktdefinition) ≠ Version | §4.6 vs §4.7 |
| Materialisierung bei Veröffentlichung | ADR-0005, ADR-0012, ADR-0014 |
| Bibliothek (Design Time) ≠ Ausführung (Run Time) | ADR-0012, ADR-0014, `ExternesKommandoPort` |

## Aggregate Roots (V1-Slice)

| Root | Verantwortung | Code |
|------|---------------|------|
| `Produktdefinition` | Editierbarer Entwurf | `domain/katalog/produktdefinition.py` |
| `ProduktdefinitionsVersion` | Materialisierte Prüfvorgabe | `domain/katalog/version.py` |
| `ExternesKommando` | Bibliothek — externes Gerätekommando | `domain/katalog/externes_kommando.py` |
| `Routine` | Bibliothek — geordnete Aktionsfolge | `domain/katalog/routine.py` |

Veröffentlichungsakt (Entwurf → Version): Katalog-Slice 2 + Gate 7.3a/d — `Produktdefinition.veroeffentlichen()`, Use Cases in `application/katalog/`.

## Entities / Value Objects

| Typ | Name | Anmerkung |
|-----|------|-----------|
| Entity | `Produktdefinition` | Root im Slice 2; mutable Entwurf |
| VO | `ProzedurSchrittEntwurf` | Schritt im Entwurf; optional `kommando_id` **oder** `routine_id` (XOR); Wechsel nur explizit (entfernen → neu zuweisen) |
| VO | `MaterialisierterProzedurSchritt` | Aufgelöste Sollvorgaben; `MaterialisierteRoutine` (führend); `MaterialisiertesExternesKommando` (deprecated, Gate 7.3b) |
| VO | `MaterialisierteRoutine` | Einheitlicher Automatisierungs-Snapshot; Herkunft `bibliothek` \| `einzelkommando` |
| VO | `MaterialisierteKommandoAktion` | Materialisierte Kommando-Aktion innerhalb einer Routine |
| VO | `MaterialisiertesExternesKommando` | Deprecated Kompatibilitäts-Snapshot (Einzelkommando-Pfad) |
| VO | `ProduktdefinitionsVersion` | Immutable nach Veröffentlichung |
| AR | `ExternesKommando` | Mutable Bibliothek; stabile `kommando_id` |
| AR | `Routine` | Mutable Bibliothek; stabile `routine_id`; mindestens eine Aktion |
| VO | `RoutineAktion` | Gate 7.3d: nur `ExternesKommandoAusfuehren` |
| Service | `materialisiere_sollvorgaben` | ADR-0005 Auflösungskette |

## Materialisierung (Variante D — ADR-0014)

| Entwurf | Materialisiert |
|---------|----------------|
| `kommando_id` | `MaterialisierteRoutine` (`herkunft=einzelkommando`, keine `routine_id`) + deprecated `externes_kommando` |
| `routine_id` | `MaterialisierteRoutine` (`herkunft=bibliothek`, `routine_id` gesetzt) |
| keine Automatisierung | `materialisierte_routine=None` |

**Führendes Feld:** `materialisierte_routine`. `externes_kommando` bleibt für Gate 7.3b-Kompatibilität beim Einzelkommando-Pfad.

### Kompatibilitätsinvariante

| Situation | Regel |
|-----------|-------|
| Einzelkommando (neu) | `materialisierte_routine` führend; `externes_kommando` abgeleitet, muss identisch sein |
| Bibliotheksroutine | nur `materialisierte_routine`; `externes_kommando=None` |
| Legacy (pre-7.3d) | nur `externes_kommando` — lesbar; Runner 7.3e normalisiert intern |
| Abweichung beider Felder | `MaterialisierteAutomatisierungInkonsistent` bei Materialisierung/Deserialisierung |

Validierung: `domain/katalog/materialisierung.py` → `validiere_materialisierter_schritt_automatisierung()`.

**Laufzeit-Auflösung (Gate 7.3e, ADR-0015):** `aufgeloeste_materialisierte_routine(schritt)` — einzige zentrale Normalisierung:

| Situation | Ergebnis |
|-----------|----------|
| `materialisierte_routine` gesetzt | Invariante prüfen, Routine zurückgeben |
| nur `externes_kommando` (Legacy) | synthetische Ein-Aktions-Routine, `herkunft=einzelkommando`, Position 1 |
| beide inkonsistent | `MaterialisierteAutomatisierungInkonsistent` |
| keine Automatisierung | `KeineAutomatisierungAmSchritt` |

Keine zweite Normalisierung in Application Layer oder Mapper.

**Exit:** Gate 7.3f legt fest, wann `externes_kommando` nicht mehr geschrieben wird.

### Entwurfs-Wechsel (Kommando ↔ Routine)

Keine stille Ersetzung (projektrules §6). Bei gesetzter Gegenreferenz schlägt Zuweisung mit `AutomatisierungDoppeltZugewiesen` fehl. Wechsel: zuerst `None`, dann neue Referenz.

## Repository

| Port | Methode (V1) |
|------|--------------|
| `KatalogRepository` | `get_aktive_version_fuer_kodierung`, `get_version`, `save_version`, `get_entwurf`, `save_entwurf` |
| `BibliothekRepository` | `save_externes_kommando`, `get_externes_kommando`, `save_routine`, `get_routine` |

`BibliothekRepository` ist fachliche Facade des **Bibliotheks-Moduls** innerhalb des Katalog-Bounded-Contexts — kein eigener Context, kein Mega-Aggregat, kein separates Repository pro Typ (ADR-0012, ADR-0014).

### Repository-Semantik

| Objekt | Port / Methode | Semantik |
|--------|----------------|----------|
| Produktdefinition (Entwurf) | `KatalogRepository.save_entwurf` | Mutable save |
| Bibliotheksobjekte | `BibliothekRepository.save_*` | Mutable save |
| ProduktdefinitionsVersion | `KatalogRepository.save_version` | Insert-only |
| Materialisierte Snapshots in Version | — | Unveränderlich nach Veröffentlichung |

Adapter dürfen mutable save technisch per INSERT/UPDATE oder SQL-Upsert umsetzen — der Port-Contract spricht nur von **save**.

## Application (Slice 2 + Gate 7.3a/d)

| Use Case | Datei |
|----------|-------|
| Entwurf anlegen | `application/katalog/entwurf_anlegen.py` |
| Veröffentlichen | `application/katalog/veroeffentlichen.py` |
| Externes Kommando anlegen | `application/katalog/externes_kommando_anlegen.py` |
| Kommando an ProzedurSchritt zuweisen | `application/katalog/kommando_zuweisen.py` |
| Routine anlegen | `application/katalog/routine_anlegen.py` |
| Routine an ProzedurSchritt zuweisen | `application/katalog/routine_zuweisen.py` |

## Domain Events (V1)

Keine — erst bei Persistenz/Event-Integration.

## Offen (nach Gate 7.3d)

- Routine-Ausführung / Runner (Gate 7.3e)
- API schrittzentriert (Gate 7.3f)
- Weitere Aktionsarten (Warten, Bestätigung, …)
- `PrüfschrittVorlage` in Bibliothek (Gate 8.2)
- Aktivierungsregeln-Auswertung zur Laufzeit
- Version deaktivieren (V1: neue Version ersetzt aktive)
