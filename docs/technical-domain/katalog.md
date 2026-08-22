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
| VO | `MaterialisierterProzedurSchritt` | Aufgelöste Sollvorgaben; `MaterialisierteRoutine` (führend); `MaterialisiertesExternesKommando` (Legacy-Lesen, Write Exit 7.4b) |
| VO | `MaterialisierteRoutine` | Einheitlicher Automatisierungs-Snapshot; Herkunft `bibliothek` \| `einzelkommando` |
| VO | `MaterialisierteKommandoAktion` | Materialisierte Kommando-Aktion innerhalb einer Routine |
| VO | `MaterialisiertePruefschrittVorlage` | Vorlagen-Snapshot in `MaterialisierterProzedurSchritt` (Gate 8.2b1) |
| VO | `MaterialisiertesExternesKommando` | Legacy-Kompatibilitäts-Snapshot (nur Lesen Altbestände; Write Exit Gate 7.4b) |
| VO | `ProduktdefinitionsVersion` | Immutable nach Veröffentlichung |
| AR | `ExternesKommando` | Mutable Bibliothek; stabile `kommando_id` |
| AR | `Routine` | Mutable Bibliothek; stabile `routine_id`; mindestens eine Aktion |
| AR | `PruefschrittVorlage` | Mutable Bibliothek; stabile `vorlage_id` (Gate 8.2b1, ADR-0020) |
| VO | `RoutineAktion` | Gate 7.3d: nur `ExternesKommandoAusfuehren` |
| Service | `materialisiere_sollvorgaben` | ADR-0005 Auflösungskette |

## Materialisierung (Variante D — ADR-0014)

| Entwurf | Materialisiert |
|---------|----------------|
| `kommando_id` | `MaterialisierteRoutine` (`herkunft=einzelkommando`, keine `routine_id`); **kein** Legacy-`externes_kommando` (Gate 7.4b) |
| `routine_id` | `MaterialisierteRoutine` (`herkunft=bibliothek`, `routine_id` gesetzt) |
| `vorlage_id` (Entwurf) | bei Veröffentlichung → `MaterialisiertePruefschrittVorlage` in `MaterialisierterProzedurSchritt` (Gate 8.2b1, ADR-0020) |
| keine Automatisierung | `materialisierte_routine=None` |

**Führendes Feld:** `materialisierte_routine`. Legacy-`externes_kommando` wird bei neuen Versionen **nicht** mehr geschrieben (Gate 7.4b, [ADR-0018](../adr/0018-legacy-automatisierung-exit.md)); Lesen alter Daten bleibt.

### Kompatibilitätsinvariante

| Situation | Regel |
|-----------|-------|
| Einzelkommando (neu, Gate 7.4b) | nur `materialisierte_routine`; `externes_kommando=None` |
| Bibliotheksroutine | nur `materialisierte_routine`; `externes_kommando=None` |
| Legacy (pre-7.3d / Altbestand) | nur `externes_kommando` — lesbar; Runner normalisiert intern |
| Beide gesetzt, konsistent (historisch) | erlaubt bei Deserialisierung |
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

**Exit:** Write Exit Gate 7.4b ([ADR-0018](../adr/0018-legacy-automatisierung-exit.md)) — neue Versionen schreiben kein `externes_kommando`. **Storage Exit** offen (separater Slice; Alembic-Basis Gate 7.5 ✅).

### Entwurfs-Wechsel (Kommando ↔ Routine)

Keine stille Ersetzung (projektrules §6). Bei gesetzter Gegenreferenz schlägt Zuweisung mit `AutomatisierungDoppeltZugewiesen` fehl. Wechsel: zuerst `None`, dann neue Referenz.

## Repository

| Port | Methode (V1) |
|------|--------------|
| `KatalogRepository` | `get_aktive_version_fuer_kodierung`, `get_version`, `save_version`, `get_entwurf`, `save_entwurf`, `list_entwuerfe` |
| `BibliothekRepository` | `save_externes_kommando`, `get_externes_kommando`, `save_routine`, `get_routine`, `list_externe_kommandos`, `list_routinen`, `delete_externes_kommando`, `delete_routine`, `save_pruefschritt_vorlage`, `get_pruefschritt_vorlage`, `list_pruefschritt_vorlagen`, `delete_pruefschritt_vorlage` |

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
| Automatisierung entfernen | `application/katalog/automatisierung_entfernen.py` |
| Externe Kommandos listen | `application/katalog/externe_kommandos_listen.py` |
| Externes Kommando lesen/aktualisieren/löschen | `externes_kommando_lesen.py`, `externes_kommando_aktualisieren.py`, `externes_kommando_loeschen.py` |
| Routinen listen/lesen/aktualisieren/löschen | `routinen_listen.py`, `routine_lesen.py`, `routine_aktualisieren.py`, `routine_loeschen.py` |
| PrüfschrittVorlagen anlegen/listen/lesen/aktualisieren/löschen | `pruefschritt_vorlage_anlegen.py`, `pruefschritt_vorlagen_listen.py`, `pruefschritt_vorlage_lesen.py`, `pruefschritt_vorlage_aktualisieren.py`, `pruefschritt_vorlage_loeschen.py` (Gate 8.2b1) |
| Entwurf lesen / Schritt-CRUD / Reihenfolge | `entwurf_lesen.py`, `prozedur_schritt_anlegen.py`, `prozedur_schritt_aktualisieren.py`, `prozedur_schritt_loeschen.py`, `prozedur_schritt_reihenfolge_aendern.py` (Gate 8.2b2, ADR-0021) |

## HTTP (Gate 6.3a + 8.2a, ADR-0017, ADR-0019)

| Endpunkt | Use Case |
|----------|----------|
| `POST /katalog/bibliothek/kommandos` | `ExternesKommandoAnlegen` (6.3a) |
| `GET /katalog/bibliothek/kommandos` | `ExterneKommandosListen` |
| `GET /katalog/bibliothek/kommandos/{id}` | `ExternesKommandoLesen` |
| `PUT /katalog/bibliothek/kommandos/{id}` | `ExternesKommandoAktualisieren` |
| `DELETE /katalog/bibliothek/kommandos/{id}` | `ExternesKommandoLoeschen` |
| `POST /katalog/bibliothek/routinen` | `RoutineAnlegen` |
| `GET /katalog/bibliothek/routinen` | `RoutinenListen` |
| `GET /katalog/bibliothek/routinen/{id}` | `RoutineLesen` |
| `PUT /katalog/bibliothek/routinen/{id}` | `RoutineAktualisieren` |
| `DELETE /katalog/bibliothek/routinen/{id}` | `RoutineLoeschen` |
| `POST /katalog/bibliothek/vorlagen` | `PruefschrittVorlageAnlegen` (Gate 8.2b1) |
| `GET /katalog/bibliothek/vorlagen` | `PruefschrittVorlagenListen` |
| `GET /katalog/bibliothek/vorlagen/{id}` | `PruefschrittVorlageLesen` |
| `PUT /katalog/bibliothek/vorlagen/{id}` | `PruefschrittVorlageAktualisieren` |
| `DELETE /katalog/bibliothek/vorlagen/{id}` | `PruefschrittVorlageLoeschen` |
| `PUT /katalog/entwuerfe/{id}/schritte/{schritt_id}/automatisierung` | `KommandoProzedurSchrittZuweisen` / `RoutineProzedurSchrittZuweisen` / `AutomatisierungEntfernen` |
| `GET /katalog/entwuerfe/{id}` | `EntwurfLesen` (Gate 8.2b2) |
| `POST /katalog/entwuerfe/{id}/schritte` | `ProzedurSchrittAnlegen` (Gate 8.2b2) |
| `PUT /katalog/entwuerfe/{id}/schritte/{schritt_id}` | `ProzedurSchrittAktualisieren` (Gate 8.2b2) |
| `DELETE /katalog/entwuerfe/{id}/schritte/{schritt_id}` | `ProzedurSchrittLoeschen` (Gate 8.2b2) |
| `PUT /katalog/entwuerfe/{id}/schritte/reihenfolge` | `ProzedurSchrittReihenfolgeAendern` (Gate 8.2b2) |

Kommando- oder Routine-Zuweisung XOR; Entfernen mit `{ "kommando_id": null, "routine_id": null }`. Keine Ausführung, keine Adapterfelder. Laborbetrieb ohne Auth ([ADR-0001](../adr/0001-v1-scope-deferrals.md)).

Entwurfs-Wechsel: andere `kommando_id` bei gesetztem Kommando → `AutomatisierungDoppeltZugewiesen` (409) — kein stiller Ersatz (projektrules §6).

## Domain Events (V1)

Keine — erst bei Persistenz/Event-Integration.

## Offen (nach Gate 8.2c1)

- Entwurfseditor-UI (Gate 8.2c2) — Bibliothek-Admin-UI abgeschlossen (Gate 8.2c1)
- Eingabefelder an PrüfschrittVorlage
- Aktivierungsregeln-Auswertung zur Laufzeit
- Version deaktivieren (V1: neue Version ersetzt aktive)
