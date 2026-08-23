# Datenbankmodell – Leitlinien (PWE)

Regeln für persistierte Daten. Fachliche Referenz: **`docs/domain-model.md`**. Keine Tabellen oder Spalten in diesem Dokument.

---

## 1. Fachliche Persistenzobjekte

Persistenz folgt der Fachdomäne — nicht umgekehrt. Das Domänenmodell beschreibt **was** gespeichert wird; dieses Dokument beschreibt **Leitlinien** für die spätere technische Abbildung.

### Design Time (Katalog)

| Fachliches Objekt | Persistenz-Hinweis |
|-------------------|-------------------|
| Basisprodukt | Katalog |
| Option | Katalog |
| Kundenprofil | Katalog |
| Produktdefinition (Entwurf) | Änderbar |
| ProduktdefinitionsVersion | **Unveränderlich** nach Veröffentlichung; materialisierte Prüfvorgabe |
| Prüfprozedur, ProzedurSchritt | Im Entwurf änderbar; in Version materialisiert |
| PrüfschrittVorlage, Routine, Externes Kommando | Bibliothek; in Version materialisiert |
| Sollvorgabe, Sollbestückung, Aktivierungsregel | Teil von Produktdefinition / Version |

### Run Time (Prüfausführung)

| Fachliches Objekt | Persistenz-Hinweis |
|-------------------|-------------------|
| Prüflauf | Referenz auf `ProduktdefinitionsVersion` (unveränderlich) |
| PrüfschrittDurchführung | Kind von Prüflauf |
| Nachweis | Kind von PrüfschrittDurchführung; automatische unveränderlich |
| Beurteilung | Teil der PrüfschrittDurchführung |
| Istbestückung | Teil des Prüflaufs |

### Post-Run Time (Protokoll)

| Fachliches Objekt | Persistenz-Hinweis |
|-------------------|-------------------|
| ProtokollSnapshot | Unveränderlich; referenziert ProduktdefinitionsVersion |

---

## 2. Beziehungen (fachlich)

- `Prueflauf` → referenziert genau eine `ProduktdefinitionsVersion` (Referenz ändert sich nie).
- `ProtokollSnapshot` → gehört zu `Prueflauf`; referenziert dieselbe Version.
- `PruefschrittDurchfuehrung` → gehört zu `Prueflauf`; bezieht sich auf materialisierten `ProzedurSchritt`.
- `Nachweis` → gehört zu `PruefschrittDurchfuehrung`.
- Kardinalitäten und Integrität folgen dem Domain Model.

---

## 3. Namensregeln

- Fachbegriffe aus **`docs/domain-model.md`** bevorzugen.
- Keine ergometerspezifischen Tabellennamen (`ergometer`, `platine_firmware`, …).
- Keine veralteten Begriffe (`produktvariante`, `schrittstatus`).

---

## 4. Migrationen

- Schemaänderungen versioniert und nachvollziehbar.
- Veröffentlichte ProduktdefinitionsVersionen werden **nicht** nachträglich geändert — nur neue Versionen angelegt.

### Alembic (Gate 7.5 ✅)

PostgreSQL-Schemaänderungen erfolgen ausschließlich über Alembic-Migrationen. Die FastAPI-Runtime erzeugt oder verändert kein Datenbankschema.

| Aspekt | Stand |
|--------|-------|
| Ort | `backend/alembic.ini`, `backend/alembic/` |
| Quelle | `adapters.persistence.postgresql.schema.Base` |
| Initialmigration | `alembic/versions/0001_initial_schema.py` |
| Gate 8.2b1 | `alembic/versions/0002_pruefschritt_vorlage.py` — Tabelle `pruefschritt_vorlage`; Version-Payload optional `materialisierte_vorlage` |
| Gate 8.1b | `alembic/versions/0004_qualification_engine.py` — Tabellen `berechtigungsprofil`, `profil_produktdefinition`, `benutzer_profil`, `einweisungsnachweis` (Feature-Branch) |
| CLI / lokal | `cd backend && DATABASE_URL=… alembic upgrade head` |
| Docker | Entrypoint: `alembic upgrade head` → uvicorn |
| CI | Step `alembic upgrade head` vor pytest |
| Runtime | erwartet migriertes Schema; Startfehler wenn Kern-Tabelle fehlt |
| Tests | Upgrade/Downgrade/Re-Upgrade; Runtime ohne Migration schlägt fehl |

Optional für isolierte Testschemas: Umgebungsvariable `ALEMBIC_SCHEMA` (setzt `search_path` in `alembic/env.py`).

**Hinweis Naming-Conventions:** `Base.metadata` hat derzeit keine `naming_convention` — bewusst deferred; vor komplexeren Autogenerate-Migrationen separat bewerten.

---

## 5. Trennung Fachdomäne vs. Persistenz

- Domänenmodell ≠ Tabellenstruktur.
- Persistenzmodelle leben in `adapters/persistence/` — nicht in der Domain-Schicht.
- ORM-Details dürfen die Fachdomäne nicht durchziehen.

---

## 6. Engine-Leitlinien

| Regel | Begründung |
|-------|------------|
| **Keine anwendungsspezifischen Tabellen** | Ergometer-Begriffe nur als Konfigurationsdaten |
| **Generische Laufzeitstrukturen** | Nachweise, Eingaben über `(schritt_durchfuehrung_id, feld_id, wert)` — nicht spaltenfix |
| **Version unveränderlich** | ProduktdefinitionsVersion schreibgeschützt nach Veröffentlichung |
| **ProtokollSnapshot unveränderlich** | Nach Erstellung keine Updates |
| **Auswertung als Read Model** | Denormalisiert; ändert nie Prüflauf oder ProtokollSnapshot |
| **Arbeitsplatz-Konfiguration extern** | COM-Port, Drucker in `infra/config/` |

---

## 7. Qualität und Konsistenz

- Transaktionsgrenzen an fachlichen Grenzen (z. B. Schrittabschluss = konsistente Änderung am Prüflauf).
- Indizes nach Use Cases aus dem Domain Model ableiten.

---

## 8. Nächster Schritt

Gate **8.3a** abgeschlossen — Foto-Binärdaten liegen **extern** im Dateispeicher (`PWE_DATEI_STORAGE_PFAD`); Metadaten im `prueflauf.payload` JSON (**kein** Schema-Wechsel, keine Alembic-Migration); siehe [ADR-0022](adr/0022-foto-nachweis-dateispeicher.md). **Storage Exit** für Legacy-`externes_kommando` bleibt offen — separater Slice; kein Zusammenhang mit Datei-Storage.
