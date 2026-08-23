# ADR-0023: Identity Bounded Context (Gate 8.1)

## Status

Angenommen (Gate 8.1 — Architektur)

## Kontext

Nach Gate 8.2–8.4 sind Katalog-Administration, Foto-Nachweis und Protokoll-Anzeige im Laborbetrieb ohne Authentifizierung nutzbar. Gate 8.1 (**Identity & Qualification**) führt Benutzer, Authentifizierung, Autorisierung und fachliche Qualifikation ein.

`docs/architecture.md` sieht Identity bereits als Querschnitt vor; Domain- und Application-Ordner sind Platzhalter. Ohne klare Context-Grenzen droht Vermischung von Rechte- und Qualifikationslogik in Katalog oder Prüfausführung.

## Problem

- Freies `pruefer_id` und ungeschützte Admin-APIs skalieren nicht auf Mehrbenutzer-/QM-Betrieb.
- Rollen, Profile und Einweisungen dürfen nicht in Katalog-Aggregates oder Prüflauf-Invarianten „mitwachsen“.
- Domain-Imports zwischen Contexts erzeugen zyklische Abhängigkeiten.

## Entscheidung

**Identity ist ein eigener Bounded Context** (`domain/identity/`, `application/identity/`) mit eigenen Ports und Adaptern.

### Aggregate

| Aggregate | Verantwortung |
|-----------|----------------|
| `Benutzer` | Identität, Status, Systemrollen (Mehrfachrollen), Credential-Handle, Profilzuordnungen |
| `Berechtigungsprofil` | Bezeichnung/Zweck; n:m zu Produktdefinition-IDs |
| `Einweisungsnachweis` | Qualifikation Benutzer × ProduktdefinitionsVersion |

### Value Objects (Auszug)

- `BenutzerId`, `ProfilId`, `EinweisungId`
- `Systemrolle`: Administrator · QM · Abteilungsleiter · Prüfer
- `BenutzerStatus`: Neu · Aktiv · Gesperrt · Archiviert
- `EinweisungsStatus` (mind. gültig / widerrufen / abgelaufen)
- Opaque `PasswortHash` (nie Klartext in der Domain)

### Policies / Domain Services

- Qualifikation für eine Version (`Profil` ∧ `Einweisung` ∧ Status/Rollen-Voraussetzungen) — Details: [ADR-0026](0026-qualification-model.md)
- Administrative Fähigkeits-Policies aus der Rollenmenge — Details: [ADR-0025](0025-authorization.md)

### Daten-Ownership

| Daten | Owner |
|-------|--------|
| Benutzer, Status, Rollen, Credentials-Referenz | Identity |
| Berechtigungsprofile | Identity |
| **Profil ↔ Produktdefinition**-Zuordnung | **Identity** |
| Einweisungsnachweise (inkl. `version_id`) | Identity |
| Session-Persistenz | Identity-**Adapter** (Infrastruktur), kein Domain-Aggregate |
| Produktdefinition, Version, Publish, Bibliothek | **Katalog** |
| Prüflauf, Nachweise, Beurteilung | **Prüfausführung** |
| ProtokollSnapshot | **Protokoll** |

### Context-Grenzen

| Context | Beziehung |
|---------|-----------|
| **Katalog** | Identity speichert nur **IDs** (`produktdefinition_id`, `version_id`). Keine Katalog-Fachobjekte in Identity. Publish kann Application-seitig Identity anstoßen (Einweisungs-Übernahme, ADR-0026). |
| **Prüfausführung** | Application orchestriert Qualifikationsprüfung vor Start. Prüflauf speichert `pruefer_id` = `BenutzerId` ([ADR-0027](0027-authenticated-pruefer-id.md)). Kein Import von Identity-Aggregates in die Prüfausführungs-Domain. |
| **Protokoll** | Übernimmt Prüfer-Referenz aus Prüflauf/Snapshot; kein direkter Identity-Domain-Zugriff. |

**Nur IDs zwischen Contexts. Keine Domain-Imports zwischen den Contexts.** Orchestrierung ausschließlich in Application (und API-Transport).

### Ausdrücklich nicht in Identity

- Produktdefinitions-Inhalt, Materialisierung, Routinen, COM
- Beurteilung, Nachweis-Fachregeln, PDF-Erzeugung/-Layout
- HTTP-/Cookie-/JWT-Bytes, CSRF-Tokens (Adapter/API; AuthN: [ADR-0024](0024-authentication-v1.md))
- Endpoint-Permission-Zeilen als Domain-Entities
- Auswertung/Dashboard (Gate 9)
- Geräte- oder Arbeitsplatz-Erkennung

### Slice-Zuordnung (Roadmap)

| Slice | Identity-Anteil |
|-------|-----------------|
| **8.1a** Identity Foundation | Benutzer, Status, Rollen am Benutzer, AuthN, Middleware, Guards; `pruefer_id`-Binding |
| **8.1b** Qualification Engine | Profile, Einweisungen, Startregel, Publish-Übernahme |
| **8.1c** Identity Administration | Verwaltungs-UI, Aktivieren/Sperren/Archivieren, Audit |

## Konsequenzen

- Neue Repositories/Ports nur für Identity; bestehende Katalog-/Prüflauf-Ports bleiben Owner ihrer Aggregate.
- Gate 8.1 erweitert den früheren Laborbetrieb (siehe Klarstellung [ADR-0001](0001-v1-scope-deferrals.md)); Authentifizierung und Qualifikation werden verbindlich.
- Frontend-Guards sind UX, keine Security Boundary ([ADR-0025](0025-authorization.md)).

## Alternativen

- Rechte nur im Katalog-Context: verworfen — vermischt Design-Time mit Identity.
- Nur API-Rollen-Flags ohne Domain: verworfen — Qualifikation und Audit fehlen.
- Externes IdP als V1-Pflicht: verworfen — Overkill für V1; später möglich.
