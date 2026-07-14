# ADR-0012: Bibliotheks-Modulierung im Katalog (ExternesKommando)

## Status

Angenommen (Gate 7.3a)

## Kontext

Gate 7.3 (Routinen / Externes Kommando über API) ist zu groß für einen Slice. Domain Model §4.11 verlangt zentrale Kommandoverwaltung; Entwürfe sollen Bibliotheksobjekte nur per ID referenzieren. Beim Veröffentlichen müssen Inhalte unveränderlich in die `ProduktdefinitionsVersion` materialisiert werden.

Offene Modellierungsfragen:

1. Ein Mega-Aggregat „Bibliothek“ vs. typisierte Aggregate Roots?
2. Ein Repository pro Bibliothekstyp vs. Facade?
3. Abgrenzung zum ausführenden `ExternesKommandoPort` in Prüfausführung?

## Entscheidung

**Variante C — Bibliotheks-Modul mit typisierten Aggregate Roots und gemeinsamer Repository-Facade:**

| Aspekt | Entscheidung |
|--------|--------------|
| Bounded Context | `ExternesKommando` lebt im **Katalog** (Design Time) |
| Bibliotheks-Modul | Fachliches Modul **innerhalb** des Katalog-Bounded-Contexts — **kein** eigener Bounded Context, **kein** Bibliotheks-Mega-Aggregat |
| Aggregate Root | `ExternesKommando` — eigenständig, stabile `kommando_id` |
| Weitere Roots | `Routine` (Gate 7.3d), `PrüfschrittVorlage` später im selben Modul |
| Repository | `BibliothekRepository` — fachliche **Facade** des Bibliotheks-Moduls; **kein** `ExternesKommandoRepository` |
| Entwurf | `ProzedurSchrittEntwurf.kommando_id` optional |
| Materialisierung | `MaterialisiertesExternesKommando` in `MaterialisierterProzedurSchritt` (Snapshot: `kommando_id`, `bezeichnung`, `kommandocode`) |
| Ausführung | `ExternesKommandoPort` bleibt ausschließlich in **Prüfausführung** (Run Time) |
| Laufzeit | Veröffentlichte Versionen referenzieren **keine** mutable Bibliothek |

Gate 7.3a implementiert nur das Katalog-Minimum — keine HTTP-Ausführung, keine Routine-Domain.

### Repository-Semantik (fachlicher Contract)

| Objekt | Port | Semantik |
|--------|------|----------|
| `Produktdefinition` (Entwurf) | `KatalogRepository.save_entwurf` | **Mutable save** — überschreibt den gespeicherten Zustand bei bekannter ID |
| Bibliotheksobjekte (z. B. `ExternesKommando`) | `BibliothekRepository.save_*` | **Mutable save** — überschreibt den gespeicherten Zustand bei bekannter `kommando_id` |
| `ProduktdefinitionsVersion` | `KatalogRepository.save_version` | **Insert-only** — `UnveraenderlichesObjektBereitsVorhanden` bei Duplikat |

Der Port beschreibt **save** als fachliche Persistierung des Aggregate-Zustands. Ob der Adapter intern INSERT, UPDATE oder SQL-Upsert verwendet, ist **reine Implementierungsdetail** — nicht Teil des Domänen- oder Port-Contracts.

## Begründung

- Klare Trennung Design Time (Bibliothek, Entwurf) vs. Run Time (Port, Adapter COM/Simulation)
- Facade skaliert für spätere Bibliothekstypen ohne Repository-Explosion
- Materialisierung garantiert Audit-Nachvollziehbarkeit und Unabhängigkeit von späteren Bibliotheksänderungen
- Minimale Snapshot-Felder — keine vorsorgliche Metadatenfülle

## Konsequenzen

- `ProduktdefinitionVeroeffentlichen` benötigt `BibliothekRepository` zur Auflösung von `kommando_id`
- PostgreSQL: Tabelle `externes_kommando`; JSON-Payload für Entwurf/Version enthält Referenz bzw. Snapshot
- PostgreSQL-Adapter darf für mutable Bibliotheksobjekte SQL-Upsert nutzen — semantisch äquivalent zu mutable save
- Gate 7.3b: API-Ausführung über materialisierten Snapshot / `kommando_id`, nicht freie Strings; Laufzeit liest **keine** mutable Bibliothek
- Gate 7.3d: `Routine` als weiteres Aggregate Root — siehe [ADR-0014](0014-routine-katalog-materialisierung.md)

## Bezug

- Domain Model §4.11, §10
- [ADR-0005](0005-sollvorgaben-materialisierung.md) — Materialisierungsprinzip
- `ExternesKommandoPort` — unverändert in Prüfausführung (Gate 5.3/5.4)
