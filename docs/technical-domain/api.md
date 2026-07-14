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
| POST | `/prueflaeufe` | `PruefungStarten` |
| POST | `/prueflaeufe/{id}/schritte/{schritt_id}/automatisierung/ausfuehren` | `RoutineAusfuehren` |
| POST | `/prueflaeufe/{id}/schritte/{schritt_id}/kommandos/{kommando_id}/ausfuehren` | `ExternesKommandoAusfuehren` (**deprecated**, Gate 7.3b) |
| POST | `/prueflaeufe/{id}/komponenten` | `KomponenteErfassen` |
| POST | `/prueflaeufe/{id}/schritte/{schritt_id}/nachweise` | `NachweisErfassen` |
| POST | `/prueflaeufe/{id}/schritte/{schritt_id}/beurteilung` | `SchrittBeurteilen` |
| POST | `/prueflaeufe/{id}/abschluss` | `PruefungAbschliessen` |
| GET | `/prueflaeufe/{id}/protokoll/pdf` | `ProtokollErzeugen` |

## Fehlerformat

Alle API-Fehler (Domain und Validierung) liefern ein einheitliches JSON-Objekt:

```json
{"detail": "Lesbare Fehlermeldung", "code": "maschinenlesbarer_code"}
```

| HTTP | `code` (Beispiele) | Auslöser |
|------|---------------------|----------|
| 404 | `version_nicht_gefunden`, `prueflauf_nicht_gefunden`, … | `DomainError`-Subklassen mit Suffix `NichtGefunden` |
| 409 | `invariant_verletzt`, … | `InvariantViolation` und übrige fachliche Konflikte |
| 422 | `validation`, `ungueltiger_wert` | Pydantic / ungültige Enum-Werte |

Öffentliche `detail`-Texte sind generisch; technische Exception-Texte werden nicht ausgegeben.

Implementierung: `api/fehler.py`, Handler in `api/errors.py`.

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
| Monitoring | HTTP 200 ≠ fachlicher Erfolg — Metriken müssen `fehlgeschlagen` auswerten |

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

## Externes Kommando ausführen (Gate 7.3b, **deprecated**)

`POST /prueflaeufe/{prueflauf_id}/schritte/{schritt_id}/kommandos/{kommando_id}/ausfuehren`

**Deprecated** — OpenAPI `deprecated: true`. Verhalten unverändert (Gate 7.3b); kein Redirect auf `RoutineAusfuehren`. Zielendpoint: `POST .../automatisierung/ausfuehren` (ADR-0016).

Führt ein **bereits materialisiertes** Einzelkommando aus der referenzierten `ProduktdefinitionsVersion` aus. Request-Body: leeres JSON `{}` oder kein Body. **`extra="forbid"`** — unbekannte Felder (z. B. `kommandocode`) → HTTP 422.

| Aspekt | Regel |
|--------|-------|
| Request-Body | `{}` oder kein Body; unbekannte Felder abgelehnt |
| Identifikation | `prueflauf_id`, `schritt_id`, `kommando_id` (Pfad) |
| Kommandocode-Quelle | Ausschließlich `MaterialisiertesExternesKommando` in der Version |
| Mutable Bibliothek | Wird zur Laufzeit **nicht** gelesen |
| Idempotenz | **Nicht idempotent** — jeder Aufruf erzeugt neue Nachweis-Wellen |
| Adapter (V1) | `SimuliertesExternesKommandoPort` (Default Dev/CI); COM via `EXTERNES_KOMMANDO_ADAPTER=com` + `[com]`-Extra |

**Response (201):**

```json
{
  "nachweise": [
    {"nachweis_id": "…", "art": "rohantwort"},
    {"nachweis_id": "…", "art": "extrahierter_wert"}
  ]
}
```

| HTTP | `code` | Auslöser |
|------|--------|----------|
| 404 | `prueflauf_nicht_gefunden` | Unbekannter Prüflauf |
| 404 | `materialisierter_prozedur_schritt_nicht_gefunden` | Schritt nicht in referenzierter Version |
| 409 | `kommando_nicht_freigegeben` | `kommando_id` passt nicht zum materialisierten Schritt |
| 409 | `invariant_verletzt` | Prüflauf bereits abgeschlossen |
| 409 | `externes_kommando_adapter_fehler` | Adapter meldet fehlgeschlagene Ausführung **ohne** audit-relevante Rohantwort |
| 409 | `externes_kommando_adapter_fehler` | Geräte-/Parserfehler **mit** Rohantwort — Body enthält zusätzlich `nachweise` (ROHANTWORT persistiert, Request commit) |
| 422 | `validation` | Unerlaubter Request-Body (z. B. `kommandocode`) |

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

## Read Model (Gate 6.0)

`GET /prueflaeufe/{id}` liefert den UI-tauglichen Zustand:

- Kopfdaten (Status, Version, Prüfobjekt, Prüfer)
- Materialisierte Schritte aus der referenzierten `ProduktdefinitionsVersion` (Reihenfolge, Sollvorgaben, Pflicht)
- Pro Schritt: Nachweise und Beurteilung (falls vorhanden)
- Sollbestückung und erfasste Komponenten
- **UI-Fortschritt (Gate 7.0):** `ist_abgeschlossen`, `fehlende_komponenten`, `kann_komponente_erfassen`, `kann_abgeschlossen_werden`; pro Schritt `kann_nachweis_erfassen`, `kann_beurteilt_werden`

Keine Fachlogik in der Route — Use Case `PrueflaufLesen` in `application/pruefausfuehrung/prueflauf_lesen.py`.

## Wiring (Persistenz)

| Modus | Auswahl | Verhalten |
|-------|---------|-----------|
| **In-Memory** | `DATABASE_URL` fehlt oder leer | `in_memory_deps()` — Dev, Tests, lokale Entwicklung ohne DB |
| **PostgreSQL** | `DATABASE_URL` gesetzt | Request-scoped Session, Commit/Rollback pro HTTP-Request ([ADR-0011](../adr/0011-api-postgresql-unit-of-work.md)) |

**Composition Root:** `api/persistence.py` (Konfiguration, PG-Wiring), `api/app.py` (Lifespan, Middleware), `api/deps.py` (`get_request_deps`).

**Tests:** API-Tests injizieren explizit `in_memory_deps()` — unabhängig von CI-`DATABASE_URL`. PostgreSQL-API-Integration separat (`@pytest.mark.postgresql`).

**Startfehler:** Ungültige oder nicht erreichbare `DATABASE_URL` → Anwendung startet nicht (`PersistenceConfigurationError`). Ungültige Kommando-Adapter-Konfiguration → `KommandoAdapterConfigurationError` ([ADR-0013](../adr/0013-com-adapter-wiring-fehlerabbildung.md)).

**Dev-Stack:** `docker compose up --build` startet API + PostgreSQL — siehe [`README-docker.md`](../../README-docker.md).

## Authentifizierung / Identity

| Thema | Status | Begründung |
|-------|--------|------------|
| Auth-Middleware, Tokens | ⏸ P2 | ADR-0001: V1 PC-only, kein Multi-User-Betrieb. |
| `pruefer_id` im Request-Body | ✅ V1-Slice | Ausreichend für Frontend-Prototyp; Identity-Context folgt mit Auth-Slice. |

## Frontend-Vorbereitung (Katalog)

Ohne veröffentlichte Produktdefinition schlägt `POST /prueflaeufe` mit `version_nicht_gefunden` fehl. Der minimale Katalog-Flow für den nächsten Frontend-Slice:

1. `POST /katalog/entwuerfe` — Entwurf anlegen
2. `POST /katalog/entwuerfe/{id}/veroeffentlichen` — aktive Version materialisieren
3. `POST /prueflaeufe` — Prüfung starten

Keine Admin-UI, keine vollständige Katalogverwaltung in diesem Slice.

## Bewusst offen (nach Merge)

- OpenAPI-Versionierung / erweiterte Validierungsdetails (`errors[]` bei 422)
- Authentifizierung und serverseitiger Identity-Context
