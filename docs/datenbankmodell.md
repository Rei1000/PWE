# Datenbankmodell – Leitlinien (PWE)

Dieses Dokument beschreibt Regeln für persistierte Daten in PWE. Es enthält **keine** konkreten Tabellen, Spalten oder Beispieldaten — diese werden abgeleitet, sobald das Domain-Modell pro Bounded Context steht.

Die verbindliche Begriffswelt ist in `docs/projektrules.md` (Ubiquitous Language) dokumentiert.

---

## 1. Entities, Value Objects und Aggregate

- **Entity:** Objekt mit identitätsstiftendem Merkmal; Lebenszyklus über die Zeit hinweg nachverfolgbar.
- **Value Object:** Unveränderlicher Wert ohne eigene Identität außerhalb des Aggregats (z. B. Schrittstatus, Eingabewert).
- **Aggregat:** Konsistenzgrenze; Änderungen erfolgen ausschließlich über die Aggregate Root.

### Aggregate Roots (verbindlich)

| Context | Aggregate Root | Enthält (Beispiele) | Nicht eigenständige Aggregate |
|---------|----------------|---------------------|-------------------------------|
| **Katalog** | `Produktvariante` | Zuordnung zur Prüfprozedur, Stammdaten-Referenzen | — |
| **Katalog** | `Pruefprozedur` | Schrittfolge, Verweise auf Schrittvorlagen | Einzelne Schrittpositionen |
| **Katalog** | `PruefschrittVorlage` | Eingabefelddefinitionen, Hinweise, Routine-Referenz | Eingabefelder als Entitäten innerhalb |
| **Katalog** | `Routine` | Aktionen, Reihenfolge, Bedingungen | Einzelne Aktionen |
| **Katalog** | `ExternesKommando` | Kommando-Definition, Parameter | — |
| **Prüfausführung** | `Prueflauf` | Schrittergebnisse, Eingaben, Messwerte, Kommentare, Fotos | Messwerte, Fotos, Kommentare |
| **Protokoll** | `ProtokollSnapshot` | Unveränderlicher Zustand eines abgeschlossenen Prüflaufs | — |
| **Identity** | `Benutzer` | Rolle, persönliche Schrittreihenfolge | — |

**Auswertung** hat keine eigenen Aggregate — sie liest denormalisierte Read Models aus abgeschlossenen Prüfläufen.

In der ersten Anwendung: Artikelnummer = Instanz von `Produktvariante`; Geräteseriennummer = `Prüfobjekt-Kennung`; Platine = `Komponente`.

---

## 2. Beziehungen

- Beziehungen folgen der **fachlichen** Modellierung, nicht der UI-Bequemlichkeit.
- Kardinalitäten explizit dokumentieren (1:1, 1:n, n:m).
- Referenzielle Integrität: DB-Constraints vs. Anwendungslogik projektspezifisch festlegen.
- `Prueflauf` referenziert `Pruefprozedur` per ID (Snapshot der verwendeten Version bei Abschluss im `ProtokollSnapshot`).

---

## 3. Namensregeln

- Einheitliche Konvention für Tabellen und Spalten (z. B. `snake_case` in der DB).
- Fachbegriffe aus der Ubiquitous Language bevorzugen — keine ergometerspezifischen Tabellennamen.
- Migrationen beschreibend und versioniert benennen.

---

## 4. Migrationen

- Schemaänderungen versioniert und nachvollziehbar.
- Keine stillen Änderungen auf Produktionssystemen ohne Freigabeprozess.
- Rollback-Strategie für riskante Änderungen definieren.

---

## 5. Trennung Domain vs. ORM / Persistenz

- Das **Domänenmodell** beschreibt Regeln und Invarianten; es ist nicht identisch mit der Tabellenstruktur.
- **Persistenzmodelle** (ORM-Entities, Row-DTOs) sind Adapter-Sichten in `adapters/persistence/`.
- ORM-Annotationen und DB-Details dürfen die **Domain-Schicht** nicht durchziehen.

---

## 6. Engine-Leitlinien (PWE-spezifisch)

| Regel | Begründung |
|-------|------------|
| **Keine anwendungsspezifischen Tabellen** | Keine Tabellen wie `ergometer`, `com_port_log` oder `platine_firmware` als Domain-Kern. |
| **Generische Strukturen für Laufzeitdaten** | Schrittergebnisse, Eingaben, Messwerte über `(schritt_id, feld_id, wert)` — nicht über spaltenfixe Ergometer-Felder. |
| **Externe Kommandos als Konfiguration** | Kommandodefinitionen im Katalog speichern; Protokollimplementierung (COM, Modbus, …) nur im Adapter. |
| **Protokoll-Snapshot unveränderlich** | `ProtokollSnapshot` nach Erstellung schreibgeschützt. |
| **Auswertung als Read Model** | Dashboard-Tabellen/Views denormalisiert; ändern nie `Prueflauf` oder `ProtokollSnapshot`. |
| **Arbeitsplatz-Konfiguration außerhalb des Domain-Schemas** | Schnittstellenports, Drucker und Pfade in `infra/config/`, nicht im fachlichen Datenmodell. |

---

## 7. Qualität und Konsistenz

- Transaktionsgrenzen an Aggregat-Grenzen ausrichten (z. B. ein Schrittabschluss = eine konsistente Änderung am `Prueflauf`).
- Indizes nach Zugriffsmustern aus Use Cases ableiten.
- Testdaten getrennt von Produktion; keine echten personenbezogenen Daten in Repositories.

---

## 8. Nächster Schritt im Projekt

Sobald die Domain-Modelle pro Bounded Context definiert sind:

- logisches Datenmodell je Context ableiten,
- physisches Schema dokumentieren,
- Migrationen und Zugriffspfade mit `docs/architecture.md` abstimmen.
