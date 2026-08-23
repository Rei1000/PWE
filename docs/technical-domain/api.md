# Technical Domain — API

Brücke Application → HTTP. Fachliche Referenz: `docs/architecture.md` §6–§7, ADR-0002.

## Prinzipien

| Regel | Umsetzung |
|-------|-----------|
| Keine Fachlogik | Routen delegieren ausschließlich an Application-Use-Cases |
| Keine Domain in DTOs | Pydantic-Schemas nur in `api/schemas.py` |
| Wiring | `api/deps.py`, `api/persistence.py` — Repositories injizierbar, PG request-scoped |

## Endpunkte (V1-Slice)

| Methode | Pfad | Use Case |
|---------|------|----------|
| GET | `/health` | — |
| GET | `/prueflaeufe/{id}` | `PrueflaufLesen` |
| POST | `/katalog/entwuerfe` | `EntwurfAnlegen` |
| POST | `/katalog/entwuerfe/{id}/veroeffentlichen` | `ProduktdefinitionVeroeffentlichen` |
| POST | `/katalog/bibliothek/kommandos` | `ExternesKommandoAnlegen` (Gate 6.3a) |
| GET | `/katalog/bibliothek/kommandos` | `ExterneKommandosListen` (Gate 8.2a) |
| GET | `/katalog/bibliothek/kommandos/{kommando_id}` | `ExternesKommandoLesen` (Gate 8.2a) |
| PUT | `/katalog/bibliothek/kommandos/{kommando_id}` | `ExternesKommandoAktualisieren` (Gate 8.2a) |
| DELETE | `/katalog/bibliothek/kommandos/{kommando_id}` | `ExternesKommandoLoeschen` (Gate 8.2a) |
| POST | `/katalog/bibliothek/routinen` | `RoutineAnlegen` (Gate 8.2a) |
| GET | `/katalog/bibliothek/routinen` | `RoutinenListen` (Gate 8.2a) |
| GET | `/katalog/bibliothek/routinen/{routine_id}` | `RoutineLesen` (Gate 8.2a) |
| PUT | `/katalog/bibliothek/routinen/{routine_id}` | `RoutineAktualisieren` (Gate 8.2a) |
| DELETE | `/katalog/bibliothek/routinen/{routine_id}` | `RoutineLoeschen` (Gate 8.2a) |
| POST | `/katalog/bibliothek/vorlagen` | `PruefschrittVorlageAnlegen` (Gate 8.2b1) |
| GET | `/katalog/bibliothek/vorlagen` | `PruefschrittVorlagenListen` (Gate 8.2b1) |
| GET | `/katalog/bibliothek/vorlagen/{vorlage_id}` | `PruefschrittVorlageLesen` (Gate 8.2b1) |
| PUT | `/katalog/bibliothek/vorlagen/{vorlage_id}` | `PruefschrittVorlageAktualisieren` (Gate 8.2b1) |
| DELETE | `/katalog/bibliothek/vorlagen/{vorlage_id}` | `PruefschrittVorlageLoeschen` (Gate 8.2b1) |
| PUT | `/katalog/entwuerfe/{id}/schritte/{schritt_id}/automatisierung` | `KommandoProzedurSchrittZuweisen` / `RoutineProzedurSchrittZuweisen` / `AutomatisierungEntfernen` (6.3a + 8.2a) |
| GET | `/katalog/entwuerfe/{produktdefinition_id}` | `EntwurfLesen` (Gate 8.2b2) |
| POST | `/katalog/entwuerfe/{produktdefinition_id}/schritte` | `ProzedurSchrittAnlegen` (Gate 8.2b2) |
| PUT | `/katalog/entwuerfe/{produktdefinition_id}/schritte/{schritt_id}` | `ProzedurSchrittAktualisieren` (Gate 8.2b2) |
| DELETE | `/katalog/entwuerfe/{produktdefinition_id}/schritte/{schritt_id}` | `ProzedurSchrittLoeschen` (Gate 8.2b2) |
| PUT | `/katalog/entwuerfe/{produktdefinition_id}/schritte/reihenfolge` | `ProzedurSchrittReihenfolgeAendern` (Gate 8.2b2) |
| POST | `/prueflaeufe` | `PruefungStarten` |
| POST | `/prueflaeufe/{id}/schritte/{schritt_id}/automatisierung/ausfuehren` | `RoutineAusfuehren` ([ADR-0016](../adr/0016-automatisierung-http-api.md) — alleiniger Run-Time-Contract) |
| POST | `/prueflaeufe/{id}/komponenten` | `KomponenteErfassen` |
| POST | `/prueflaeufe/{id}/schritte/{schritt_id}/nachweise` | `NachweisErfassen` (ohne `art: foto`) |
| POST | `/prueflaeufe/{id}/schritte/{schritt_id}/nachweise/foto` | `FotoNachweisErfassen` (Gate 8.3a, multipart) |
| GET | `/prueflaeufe/{id}/nachweise/{nachweis_id}/datei` | `NachweisDateiLesen` (Gate 8.3a) |
| POST | `/prueflaeufe/{id}/schritte/{schritt_id}/beurteilung` | `SchrittBeurteilen` |
| POST | `/prueflaeufe/{id}/abschluss` | `PruefungAbschliessen` |
| GET | `/prueflaeufe/{id}/protokoll/pdf` | `ProtokollErzeugen` |
| POST | `/identity/profile` | `ProfilAnlegen` (Gate 8.1b) |
| GET | `/identity/profile` | `ProfileListen` (Gate 8.1b) |
| GET | `/identity/profile/{profil_id}` | `ProfilLesen` (Gate 8.1b) |
| PUT | `/identity/profile/{profil_id}` | `ProfilAktualisieren` (Gate 8.1b) |
| POST | `/identity/profile/{profil_id}/deaktivieren` | `ProfilDeaktivieren` (Gate 8.1c1) |
| POST | `/identity/profile/{profil_id}/aktivieren` | `ProfilAktivieren` (Gate 8.1c1) |
| PUT | `/identity/profile/{profil_id}/benutzer/{benutzer_id}` | `ProfilBenutzerZuordnen` (Gate 8.1b) |
| DELETE | `/identity/profile/{profil_id}/benutzer/{benutzer_id}` | `ProfilBenutzerEntfernen` (Gate 8.1b) |
| POST | `/identity/einweisungen` | `EinweisungAnlegen` (Gate 8.1b) |
| GET | `/identity/einweisungen` | `EinweisungenFuerBenutzerListen` (Gate 8.1b) |
| GET | `/identity/einweisungen/{einweisung_id}` | `EinweisungLesen` (Gate 8.1b) |
| POST | `/identity/einweisungen/{einweisung_id}/widerrufen` | `EinweisungWiderrufen` (Gate 8.1b) |
| GET | `/identity/benutzer` | `BenutzerListen` (Gate 8.1c1) |
| GET | `/identity/benutzer/{benutzer_id}` | `BenutzerLesen` (Gate 8.1c1) |
| POST | `/identity/benutzer` | `BenutzerAnlegen` (Gate 8.1c1) |
| POST | `/identity/benutzer/{id}/aktivieren` | `BenutzerAktivieren` (Gate 8.1c1) |
| POST | `/identity/benutzer/{id}/sperren` | `BenutzerSperren` (Gate 8.1c1) |
| POST | `/identity/benutzer/{id}/entsperren` | `BenutzerEntsperren` (Gate 8.1c1) |
| POST | `/identity/benutzer/{id}/archivieren` | `BenutzerArchivieren` (Gate 8.1c1) |
| POST | `/identity/benutzer/{id}/wiederherstellen` | `BenutzerWiederherstellen` (Gate 8.1c1) |
| PUT | `/identity/benutzer/{benutzer_id}/rollen` | `BenutzerRollenSetzen` (Gate 8.1c1) |
| POST | `/identity/benutzer/{benutzer_id}/passwort` | `PasswortZuruecksetzen` (Admin, Gate 8.1c1) |
| GET | `/identity/audit` | Identity-Audit lesen (Gate 8.1c1, Admin only) |
| POST | `/auth/passwort` | `PasswortAendern` (Self-Change, Gate 8.1c1) |

## Fehlerformat

Alle API-Fehler (Domain und Validierung) liefern ein einheitliches JSON-Objekt:

```json
{"detail": "Lesbare Fehlermeldung", "code": "maschinenlesbarer_code"}
```

| HTTP | `code` (Beispiele) | Auslöser |
|------|---------------------|----------|
| 401 | `ungueltige_anmeldedaten`, `nicht_authentifiziert`, `session_abgelaufen`, … | AuthN (Gate 8.1a) |
| 403 | `qualifikation_unzureichend`, `nicht_berechtigt`, `prueflauf_nicht_eigentuemer`, `passwort_wechsel_erforderlich`, … | Qualifikation / Ownership / Rollen / Force-Change (Gate 8.1b/8.1c1) |
| 404 | `version_nicht_gefunden`, `prueflauf_nicht_gefunden`, `nachweis_nicht_gefunden`, `datei_nicht_gefunden`, `nachweis_kein_foto`, … | `DomainError`-Subklassen mit Suffix `NichtGefunden` bzw. `NachweisKeinFoto` |
| 409 | `invariant_verletzt`, `letzter_administrator_verletzt`, `foto_nur_per_multipart`, `kommando_in_verwendung`, `routine_in_verwendung`, `einweisung_bereits_gueltig`, … | `InvariantViolation` und übrige fachliche Konflikte |
| 413 | `datei_zu_gross` | `DateiZuGross` |
| 415 | `ungueltiger_dateityp` | `UngueltigerDateityp` |
| 503 | `datei_speicherung_fehlgeschlagen` | Storage-Infrastrukturfehler |
| 422 | `validation`, `ungueltiger_wert` | Pydantic / ungültige Enum-Werte |

Öffentliche `detail`-Texte sind generisch; technische Exception-Texte werden nicht ausgegeben.

Implementierung: `api/fehler.py`, Handler in `api/errors.py`.

## Katalog-Setup für Automatisierung (Gate 6.3a, ADR-0017)

Minimaler Setup-Contract für PC-/Laborbetrieb ([ADR-0001](../adr/0001-v1-scope-deferrals.md)). Historisch ohne Auth eingeführt; ab Gate **8.1** gilt Session-Authentifizierung und Autorisierung ([ADR-0024](../adr/0024-authentication-v1.md), [ADR-0025](../adr/0025-authorization.md)) — Endpunkte sind **nicht** für ungeschützte Internetbereitstellung vorgesehen. Keine Ausführungslogik im Katalog-Layer.

### Externes Kommando anlegen

`POST /katalog/bibliothek/kommandos`

| Aspekt | Regel |
|--------|-------|
| Request | `{ "bezeichnung", "kommandocode" }` — `extra=forbid`; Client setzt **keine** `kommando_id` |
| Response 201 | `{ "kommando_id", "bezeichnung" }` — **ohne** `kommandocode` (schmaler Contract; Ausführung aus Materialisierung) |
| Idempotenz | **Nein** — jeder POST = neue `kommando_id` |
| Fehler | 422 `validation` |

### Automatisierung an Entwurfsschritt zuweisen (Gate 6.3a + 8.2a, ADR-0019)

`PUT /katalog/entwuerfe/{produktdefinition_id}/schritte/{schritt_id}/automatisierung`

| Aspekt | Regel |
|--------|-------|
| Kommando zuweisen | `{ "kommando_id": "…" }` — Gate 6.3a unverändert |
| Routine zuweisen | `{ "routine_id": "…" }` — Gate 8.2a |
| Entfernen | `{ "kommando_id": null, "routine_id": null }` — beide Keys explizit |
| XOR | `kommando_id` und `routine_id` nicht gleichzeitig gesetzt |
| Leerer Body `{}` | 422 |
| Response 200 | `{ "produktdefinition_id", "schritt_id", "kommando_id", "routine_id" }` |
| Wechsel ohne Entfernen | 409 `automatisierung_doppelt_zugewiesen` |
| Fehler | 404, 409, 422 |

E2E-Flow: Kommando anlegen → Entwurf → Zuweisen → Veröffentlichen → Prüflauf → `POST .../automatisierung/ausfuehren` (ADR-0016).

## Bibliothek-HTTP CRUD (Gate 8.2a, ADR-0019)

Vollständige Design-Time-Verwaltung der Bibliothek. Listen ohne `kommandocode`; Detail-GET mit `kommandocode`. DELETE mit Referenzschutz (409) — nur offene Entwürfe und Routinen, nicht veröffentlichte Versionen. Siehe [ADR-0019](../adr/0019-bibliothek-http-crud.md).

## PrüfschrittVorlage-HTTP CRUD (Gate 8.2b1, ADR-0020)

Vollständige Design-Time-Verwaltung von `PruefschrittVorlage` in der Bibliothek. Minimalfelder V1: `bezeichnung`, optionale `beschreibung`. Keine Eingabefelder, keine Sollvorgaben, keine Automatisierung in der Vorlage.

| Methode | Pfad | Use Case |
|---------|------|----------|
| POST | `/katalog/bibliothek/vorlagen` | `PruefschrittVorlageAnlegen` |
| GET | `/katalog/bibliothek/vorlagen` | `PruefschrittVorlagenListen` |
| GET | `/katalog/bibliothek/vorlagen/{vorlage_id}` | `PruefschrittVorlageLesen` |
| PUT | `/katalog/bibliothek/vorlagen/{vorlage_id}` | `PruefschrittVorlageAktualisieren` |
| DELETE | `/katalog/bibliothek/vorlagen/{vorlage_id}` | `PruefschrittVorlageLoeschen` |

| Aspekt | Regel |
|--------|-------|
| Write-Schemas | `extra="forbid"` |
| DELETE-Referenzschutz | 409 `vorlage_in_verwendung` — nur offene Entwürfe mit `vorlage_id`; veröffentlichte Versionen blockieren nicht |
| Publish | unbekannte `vorlage_id` → 409 `vorlage_nicht_gefunden` — keine stille Korrektur |
| Materialisierung | neue Versionen erhalten `MaterialisiertePruefschrittVorlage`-Snapshot; Run Time liest nie mutable Bibliothek |
| Legacy-Versionen | ohne Snapshot weiterhin lesbar/ausführbar — keine Rückmigration |

Regressionstest: vollständiger Routine-HTTP-E2E-Pfad in `tests/api/test_api_katalog_routine_http_e2e.py`.

## Entwurfsbearbeitung HTTP (Gate 8.2b2, ADR-0021)

Erweiterte Bearbeitung von `ProzedurSchrittEntwurf` im mutable Entwurf. **Kein** Root-Metadaten-Edit, **keine** Entwurfs-Liste, **keine** Automatisierung in Schritt-Write-Contracts.

| Methode | Pfad | Use Case |
|---------|------|----------|
| GET | `/katalog/entwuerfe/{produktdefinition_id}` | `EntwurfLesen` |
| POST | `/katalog/entwuerfe/{produktdefinition_id}/schritte` | `ProzedurSchrittAnlegen` |
| PUT | `/katalog/entwuerfe/{produktdefinition_id}/schritte/{schritt_id}` | `ProzedurSchrittAktualisieren` |
| DELETE | `/katalog/entwuerfe/{produktdefinition_id}/schritte/{schritt_id}` | `ProzedurSchrittLoeschen` |
| PUT | `/katalog/entwuerfe/{produktdefinition_id}/schritte/reihenfolge` | `ProzedurSchrittReihenfolgeAendern` |

| Aspekt | Regel |
|--------|-------|
| Schritt-POST | `schritt_id`, `vorlage_id`, `ist_pflicht`, `sollvorgaben`; neue Schritte am Ende; **kein** `kommando_id`/`routine_id` |
| Schritt-PUT | Vollständiges PUT: `vorlage_id`, `ist_pflicht`, `sollvorgaben`; Automatisierung bleibt unverändert |
| Reihenfolge | separater Endpoint; vollständige Permutation `{ "schritt_ids": [...] }`; Ergebnis 1..n |
| DELETE | 204; Reihenfolge normalisiert |
| Vorlage | gegen `BibliothekRepository.get_pruefschritt_vorlage`; 404 `vorlage_nicht_gefunden` |
| Write-Schemas | `extra="forbid"` |
| Publish | unverändert; leerer Entwurf → 409 `invariant_verletzt` |

Automatisierung weiterhin ausschließlich über `PUT .../automatisierung` (Gate 6.3a + 8.2a).

## Automatisierung ausführen (Gate 7.3f, ADR-0016)

`POST /prueflaeufe/{prueflauf_id}/schritte/{schritt_id}/automatisierung/ausfuehren`

Führt die **materialisierte Automatisierung** des ProzedurSchritts aus (Einzelkommando oder Bibliotheksroutine). Use Case: ausschließlich `RoutineAusfuehren`. Request-Body: `{}` oder kein Body; **`extra="forbid"`**.

| Aspekt | Regel |
|--------|-------|
| Identifikation | nur `prueflauf_id`, `schritt_id` — kein `kommando_id`, `routine_id`, freier `kommandocode` |
| Vor Ausführungsbeginn | HTTP 404/409/422 + `{detail, code}` — kein Port, kein Save |
| Ausführung begonnen | **immer HTTP 200** + `AutomatisierungAusfuehrenResponse` — auch bei Teilfehler |
| Kein Hybrid-409 | Am Zielendpoint **niemals** 409 mit Ergebnisobjekt |
| Idempotenz | **Nicht idempotent** — jeder POST = neue `ausfuehrung_id`, neue Nachweis-Welle |
| Monitoring | HTTP 200 ≠ fachlicher Erfolg — Beobachtung wertet `fehlgeschlagen` aus (Gate 7.4c) |

**Response (200):**

```json
{
  "ausfuehrung_id": "…",
  "fehlgeschlagen": false,
  "ausgefuehrte_aktionen": 2,
  "abgebrochen_bei_aktion_position": null,
  "fehlerart": null,
  "nachweise": [
    {"nachweis_id": "…", "art": "rohantwort"},
    {"nachweis_id": "…", "art": "extrahierter_wert"}
  ]
}
```

| HTTP | `code` (Beispiele) | Auslöser |
|------|---------------------|----------|
| 404 | `prueflauf_nicht_gefunden`, `version_nicht_gefunden`, `materialisierter_prozedur_schritt_nicht_gefunden` | Vor Ausführungsbeginn |
| 409 | `keine_automatisierung_am_schritt`, `materialisierte_automatisierung_inkonsistent`, `invariant_verletzt`, `leere_routine` | Vor Ausführungsbeginn |
| 422 | `validation` | Unerlaubter Request-Body |

Zulässige `fehlerart` im Ergebnis (nur bei `fehlgeschlagen=true`): `keine_geraeteantwort`, `geraetefehlschlag`, `ungueltige_antwort`.

Route: nur Validierung, `RoutineAusfuehren`, Mapping — keine Fachlogik ([ADR-0016](../adr/0016-automatisierung-http-api.md)).

**Fachliche Beobachtung (Gate 7.4c):** Nach begonnener Ausführung wird ein strukturiertes Log-Event `automatisierung_ausgefuehrt` geschrieben (`fehlgeschlagen`, `fachlicher_erfolg`, `ausfuehrung_id`, Nachweisanzahl, …). Vorbedingungsfehler vor Beginn: Event `automatisierung_nicht_begonnen`. Ableitung nur aus bestehendem Ergebnis bzw. Fehlerabbildung — keine Infrastruktur-Metriken, keine Änderung des HTTP-Contracts. Implementierung: `api/automatisierung_beobachtung.py`.

**Legacy-Exit ([ADR-0018](../adr/0018-legacy-automatisierung-exit.md)):** Einzelkommando-HTTP entfernt (Gate 7.4a). Write Exit (Gate 7.4b): neue Versionen schreiben kein `externes_kommando`. Alte Versionen mit ausschließlich `externes_kommando` bleiben über ADR-0016 ausführbar. **Storage Exit** (physische Feldentfernung) offen — separater Slice; Alembic-Basis Gate 7.5 ✅.

### Kommando-Adapter (Gate 7.3c)

| Variable | Default | Bedeutung |
|----------|---------|-----------|
| `EXTERNES_KOMMANDO_ADAPTER` | `simulation` | `simulation` oder `com` |
| `SERIELL_PORT` | — | Pflicht bei `com` (z. B. `/dev/ttyUSB0`, `COM3`) |
| `SERIELL_BAUDRATE` | `9600` | Positive Ganzzahl |
| `SERIELL_TIMEOUT_MS` | `3000` | Timeout in Millisekunden (> 0) |

Ungültige Konfiguration → Startfehler (`KommandoAdapterConfigurationError`). Kein Fallback auf Simulation bei `com`. PySerial: optionales Backend-Extra `[com]`.

## NachweisArt — API-Contract

`POST /prueflaeufe/{id}/schritte/{schritt_id}/nachweise` erwartet im Feld `art` einen **lowercase snake_case-String** — nicht den internen Python-Enum-Namen.

| Transport (`art` im JSON) | Domain (`NachweisArt`) |
|-----------------------------|-------------------------|
| `messwert` | `NachweisArt.MESSWERT` |
| `foto` | `NachweisArt.FOTO` |
| `kommentar` | `NachweisArt.KOMMENTAR` |
| `manuelle_eingabe` | `NachweisArt.MANUELLE_EINGABE` |
| `rohantwort` | `NachweisArt.ROHANTWORT` |
| `extrahierter_wert` | `NachweisArt.EXTRAHIERTER_WERT` |
| `ergaenzung` | `NachweisArt.ERGAENZUNG` |
| `komponentenerfassung` | `NachweisArt.KOMPONENTENERFASSUNG` |

**Beispiel (gültig):**

```json
{"art": "messwert", "payload": {"spannung": 230}}
```

**Ungültig:** `"MESSWERT"`, `"Messwert"`, `"unbekannt"` → HTTP 422, `{"detail": "Validierungsfehler", "code": "validation"}`.

Mapping: `NachweisArtEnum` (Pydantic, `api/schemas.py`) → `NachweisArt(body.art.value)` in der Route — Domain bleibt unabhängig von Pydantic.

Antworten (`NachweisResponse`, Read Model) liefern `art` als denselben String-Wert (`messwert`, …).

**Gate 8.3a:** `art: "foto"` am generischen JSON-Endpunkt ist **verboten** (409 `foto_nur_per_multipart`). Foto-Nachweise nur über Multipart-Endpunkt — siehe [ADR-0022](../adr/0022-foto-nachweis-dateispeicher.md).

## Foto-Nachweis (Gate 8.3a, ADR-0022)

### Upload

`POST /prueflaeufe/{id}/schritte/{schritt_id}/nachweise/foto`

| Aspekt | Regel |
|--------|-------|
| Content-Type | `multipart/form-data` |
| Feld | `datei` (Binärdatei) |
| MIME V1 | `image/jpeg`, `image/png` — Magic-Byte-Prüfung |
| Max. Größe | 5 MiB |
| Response 201 | `{ nachweis_id, art, datei_id, mime_type, groesse_bytes, dateiname? }` |
| Fehler | 404, 409, 413, 415, 503 |

### Download

`GET /prueflaeufe/{id}/nachweise/{nachweis_id}/datei`

Fachliche Kontextvalidierung: Nachweis muss zum Prüflauf gehören und `art=foto` sein. Response: Binärinhalt, `Content-Type` aus Payload, `Content-Disposition: inline`.

Download unterliegt der Session-Authentifizierung ([ADR-0024](../adr/0024-authentication-v1.md)); fachliche Kontextvalidierung (Nachweis gehört zum Prüflauf) bleibt bestehen ([ADR-0022](../adr/0022-foto-nachweis-dateispeicher.md)). Qualifikation wird **nur beim Start** geprüft (nicht erneut bei Download/Mutationen); Mutationen erfordern Prüflauf-Ownership (siehe unten).

## Read Model (Gate 6.0)

`GET /prueflaeufe/{id}` liefert den UI-tauglichen Zustand:

- Kopfdaten (Status, Version, Prüfobjekt, Prüfer)
- Materialisierte Schritte aus der referenzierten `ProduktdefinitionsVersion` (Reihenfolge, Sollvorgaben, Pflicht)
- Pro Schritt: Nachweise und Beurteilung (falls vorhanden)
- Sollbestückung und erfasste Komponenten
- **UI-Fortschritt (Gate 7.0):** `ist_abgeschlossen`, `fehlende_komponenten`, `kann_komponente_erfassen`, `kann_abgeschlossen_werden`; pro Schritt `kann_nachweis_erfassen`, `kann_beurteilt_werden`
- **Automatisierung (Gate 6.3b):** pro Schritt `hat_automatisierung`, `kann_automatisierung_ausfuehren`, optional `automatisierung_bezeichnung` — siehe `docs/technical-domain/pruefausfuehrung.md`
- **Demo-Labor (Gate 6.3c):** `PWE_DEMO_MODE=true` aktiviert feste Simulationsantwort für `DEMO_MESSWERT` (nur Adapter `simulation`); Seed: `scripts/seed_demo_automatisierung.py`. Default `false` — kein verstecktes Demo-Verhalten.

Keine Fachlogik in der Route — Use Case `PrueflaufLesen` in `application/pruefausfuehrung/prueflauf_lesen.py`.

## Wiring (Persistenz)

| Modus | Auswahl | Verhalten |
|-------|---------|-----------|
| **In-Memory** | `DATABASE_URL` fehlt oder leer | `in_memory_deps()` — Dev, Tests, lokale Entwicklung ohne DB |
| **PostgreSQL** | `DATABASE_URL` gesetzt | Request-scoped Session, Commit/Rollback pro HTTP-Request ([ADR-0011](../adr/0011-api-postgresql-unit-of-work.md)) |

**Composition Root:** `api/persistence.py` (Konfiguration, PG-Wiring), `api/app.py` (Lifespan, Middleware), `api/deps.py` (`get_request_deps`).

**Tests:** API-Tests injizieren explizit `in_memory_deps()` — unabhängig von CI-`DATABASE_URL`. PostgreSQL-API-Integration separat (`@pytest.mark.postgresql`).

**Startfehler:** Ungültige oder nicht erreichbare `DATABASE_URL` → Anwendung startet nicht (`PersistenceConfigurationError`). Ungültige Kommando-Adapter-Konfiguration → `KommandoAdapterConfigurationError` ([ADR-0013](../adr/0013-com-adapter-wiring-fehlerabbildung.md)).

**Schema (Gate 7.5 ✅):** PostgreSQL-Schemaänderungen erfolgen ausschließlich über Alembic-Migrationen. Die FastAPI-Runtime erzeugt oder verändert kein Datenbankschema. Siehe [`datenbankmodell.md`](../datenbankmodell.md) §4.

**Dev-Stack:** `docker compose up --build` startet API + PostgreSQL — siehe [`README-docker.md`](../../README-docker.md).

## Authentifizierung / Identity

Gate **8.1** ([ADR-0023](../adr/0023-identity-bounded-context.md)–[0027](../adr/0027-authenticated-pruefer-id.md)). **Stand:** **8.1a** ✅ · **8.1b** ✅ · **8.1c1** ✅ · **8.1c2** ✅ (Verwaltungs-UI).

| Thema | Stand | Slice |
|-------|-------|-------|
| Authentifizierung | Serverseitige **Session** + Cookie (**HttpOnly**, **Secure**, **SameSite**); **kein** JWT / LocalStorage-Token in V1 ([ADR-0024](../adr/0024-authentication-v1.md)); `/auth/login`, `/auth/logout`, `/auth/me` | 8.1a ✅ |
| Authentifizierter Benutzer | Request-Kontext aus Session; Login nur bei Status **Aktiv** | 8.1a ✅ |
| `pruefer_id` | Bei **neuen** Prüfläufen aus dem Session-Benutzer abgeleitet — **kein** Trust in clientgelieferte freie Strings ([ADR-0027](../adr/0027-authenticated-pruefer-id.md)); historische freie Werte bleiben lesbar | 8.1a ✅ |
| Systemrollen | Administrator, QM, Abteilungsleiter, Prüfer (Mehrfachrollen); API erzwingt Policies, Frontend-Guards nur UX ([ADR-0025](../adr/0025-authorization.md)) | 8.1a ✅ |
| Qualification | Profil ↔ Produktdefinition; Einweisung ↔ ProduktdefinitionsVersion; Startregel ([ADR-0026](../adr/0026-qualification-model.md)) | **8.1b** ✅ |
| Force-Change | `passwortwechsel_erforderlich` — Middleware blockiert alle Pfade außer `/auth/me`, `/auth/logout`, `/auth/passwort` | **8.1c1** ✅ |
| Identity Administration (Backend) | Benutzer-Lifecycle, Rollen, Passwort-Reset, Profil aktiv/inaktiv, append-only Audit | **8.1c1** ✅ |
| Identity Administration (UI) | `/verwaltung` — Benutzer, Profile, Einweisungen; Force-Change; Rollenmatrix UX | **8.1c2** ✅ |

### Identity-HTTP (Gate 8.1b / 8.1c1) und Verwaltungs-UI (8.1c2)

Unter `/identity` (Session erforderlich; Rollen je Endpoint). Verwaltungs-**UI** unter `/verwaltung` (Frontend, Gate **8.1c2** ✅).

| Ressource | Operationen | Lesen (Admin/QM/Abt.) | Schreiben |
|-----------|-------------|------------------------|-----------|
| Profile | LIST/Anlegen/Lesen/Aktualisieren; Benutzer zuordnen/entfernen; **aktivieren/deaktivieren** | ✅ | Admin, QM (Profil); Admin, Abt. (Zuordnung) |
| Einweisungen | Anlegen/Lesen/Liste; **Widerrufen** | ✅ | Admin, Abt. (Anlegen/Widerruf) |
| Benutzer | LIST/Lesen; Anlegen; Status (aktivieren/sperren/entsperren/archivieren/wiederherstellen); Rollen; Admin-Passwort-Reset | ✅ | **Administrator** only |
| Audit | LIST | **Administrator** only | — (append-only via Mutationen) |

**Identity-Lesematrix:** Benutzer/Profile/Einweisungen lesen — Administrator, QM, Abteilungsleiter; **Prüfer** ❌. Audit und Login-Metadaten nur Administrator ([ADR-0025](../adr/0025-authorization.md)).

### Bekannte API-Einschränkung: Benutzer ↔ Berechtigungsprofil (Gate 8.1c2, P2)

Für die Zuordnung **Benutzer ↔ Berechtigungsprofil** existieren Write-Operationen (`PUT`/`DELETE` `/identity/profile/{profil_id}/benutzer/{benutzer_id}`), aber **kein dedizierter Read-Endpunkt**, über den die UI beim ersten Laden die bestehenden Profilzuordnungen eines Benutzers vollständig abrufen kann.

| Aspekt | Einordnung |
|--------|------------|
| Backend | Bleibt fachliche Source of Truth für Zuweisen und Entfernen |
| UI (Gate 8.1c2) | `sessionStorage` nur als **temporärer UX-Cache** für in der aktuellen Sitzung vorgenommene Zuordnungsänderungen |
| Erstes Laden | Bestehende serverseitige Zuordnungen sind in der UI **nicht vollständig rekonstruierbar** |
| Security | Kein Security-Problem — Zuweisung/Entfernen bleibt serverseitig autorisiert |
| Architektur | Kein Architekturbruch |
| Gate 8.1c2 | **Kein Bestandteil von Gate 8.1** — bekannte API-/UX-Einschränkung außerhalb des Scopes |

**Mögliche spätere Verbesserung (noch kein verbindliches Design):** dedizierter Read-Contract, z. B. Benutzer-Detail inklusive `profil_ids` oder eigener Read-Endpunkt für Benutzer↔Profile.

**Passwort:**

| Endpoint | Zweck |
|----------|-------|
| `POST /auth/passwort` | Self-Change (aktiver Benutzer, altes Passwort); setzt `passwortwechsel_erforderlich=false`; invalidiert alle Sessions |
| `POST /identity/benutzer/{id}/passwort` | Admin-Reset; setzt Force-Change; invalidiert alle Sessions des Zielbenutzers |

Neu angelegte Benutzer: Status **Neu**, `passwortwechsel_erforderlich=true`; Login erst nach Aktivierung.

### Prüflauf: Qualifikation, Ownership und Lesen (Gate 8.1b)

- **Start** (`POST /prueflaeufe`): nur mit gültiger Qualifikation (Prüfer-Rolle + passendes Profil + gültige Einweisung). Sonst **403** `qualifikation_unzureichend`. Qualifikation **nur hier** — nicht bei späteren Mutationen oder Reads.
- **Schreiben** (Nachweise, Foto, Automatisierung, Beurteilung, Abschluss): AuthN + Ownership (`Session-Benutzer == pruefer_id`) — sonst **403** `prueflauf_nicht_eigentuemer`.
- **Lesen** (`GET` Prüflauf, Protokoll/PDF, Foto-Download): AuthN (Status Aktiv) — **bewusst ohne** Ownership, Qualifikation oder Profil. Ziel: Wissensfluss (Prüfer lernen voneinander; QM/Abteilungen brauchen Transparenz). Feinere Leserechte später möglich ([ADR-0025](../adr/0025-authorization.md)).
- **Publish:** `POST /katalog/entwuerfe/{id}/veroeffentlichen` akzeptiert optional `einweisung_uebernehmen` (Default `false`) — übernimmt gültige Einweisungen auf die neue Version ([ADR-0026](../adr/0026-qualification-model.md)).

## Frontend-Vorbereitung (Katalog)

Ohne veröffentlichte Produktdefinition schlägt `POST /prueflaeufe` mit `version_nicht_gefunden` fehl. Der minimale Katalog-Flow:

1. `POST /katalog/entwuerfe` — Entwurf anlegen
2. `POST /katalog/entwuerfe/{id}/veroeffentlichen` — aktive Version materialisieren (optional `einweisung_uebernehmen`)
3. `POST /prueflaeufe` — Prüfung starten (authentifiziert + Qualifikation)

## Bewusst offen (nach Merge)

- OpenAPI-Versionierung / erweiterte Validierungsdetails (`errors[]` bei 422)
- Audit-Dashboard-UI (Backend-Read-API `/identity/audit` vorhanden; bewusst nicht in Gate 8.1c2)
- Read-Endpunkt Benutzer↔Profil (P2 — siehe § Bekannte API-Einschränkung)
