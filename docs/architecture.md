# Architektur – PWE (Initialversion)

Technische Architektur. Verbindliche Fachdomäne: **`docs/domain-model.md`**.

---

## 1. Ziel der Architektur

Die Architektur stellt sicher, dass die **Prüf-Workflow-Engine** als konfigurierbarer Kern wartbar, erweiterbar und von technischen Details entkoppelt bleibt.

Leitprinzipien:

- **Domain-Driven Design (DDD)** — Bounded Contexts entlang der Fachdomäne
- **Hexagonale Architektur (Ports/Adapter)**
- **Test-Driven Development (TDD)** in der Implementierungsphase

**Engine vs. erste Anwendung:** Der Kern modelliert Produktdefinitionen, Prüfläufe, Nachweise und ProtokollSnapshots generisch. Die Ergometer-Endprüfung ist erste **Konfiguration**.

---

## 2. Design Time, Run Time und Post-Run Time

| Phase | Context | Fachliche Objekte (Auszug) |
|-------|---------|----------------------------|
| **Design Time** | Katalog | Produktdefinition (Entwurf), ProduktdefinitionsVersion, Basisprodukt, Option, Kundenprofil, Prüfprozedur, ProzedurSchritt, PrüfschrittVorlage, Routine, Externes Kommando |
| **Run Time** | Prüfausführung | Prüflauf, PrüfschrittDurchführung, Nachweis, Beurteilung |
| **Post-Run Time** | Protokoll | ProtokollSnapshot |

**Identity** und **Auswertung** sind querschnittlich.

---

## 3. Systemkontext

| Akteur / System | Rolle |
|-----------------|-------|
| Prüfer (PC) | Prüfungsdurchführung (Rollenmodell Identity; Qualifikation erforderlich) |
| Administrator / QM / Abteilungsleiter | Katalog- und/oder Benutzerverwaltung gemäß Systemrollen ([ADR-0025](adr/0025-authorization.md)) |
| Prüfer (Smartphone) | Parallele Prüfungsbegleitung (V2+) |
| Externes Prüfobjekt | Über Adapter angebunden (erste Anwendung: COM) |
| Drucker | Ausgabe von ProtokollSnapshots (PDF) |
| PostgreSQL | Persistenz; Schema ausschließlich über Alembic (Gate 7.5 ✅) |
| Produktlaufkarte | Externe Eingangsinformation (Produktion) |

**Systemgrenze:** Konfigurierbare Prüfworkflows, Protokollierung, Auswertung — keine Fertigungssteuerung.

---

## 4. Fachliche Kernbereiche (Bounded Contexts)

| Context | Phase | Verantwortung |
|---------|-------|---------------|
| **Katalog** | Design Time | Produktdefinition, ProduktdefinitionsVersion, Bibliothek, Sollvorgaben, Sollbestückung, Aktivierungsregeln |
| **Prüfausführung** | Run Time | Prüflauf, PrüfschrittDurchführung, Nachweise, Beurteilungen, Routine-Orchestrierung |
| **Protokoll** | Post-Run Time | ProtokollSnapshot, Archiv |
| **Identity** | Querschnitt | Benutzer, Systemrollen, Berechtigungsprofile, Einweisungsnachweise, Prüferpräferenzen ([ADR-0023](adr/0023-identity-bounded-context.md)) |
| **Auswertung** | Read Model | Dashboard, Statistiken |

**Kein eigener Context:** Gerätekommunikation — erfolgt über `ExternesKommandoPort` und Adapter (z. B. `com/`).

In der ersten Anwendung: Artikelnummer = **Produktkodierung**; Platine = **Komponente**.

---

## 5. Fachliche Konsistenzgrenzen (Orientierung)

Aus **`docs/domain-model.md`** — technische Aggregate sind in `docs/technical-domain/` und im Code (`backend/src/domain/`) umgesetzt (Gate 1–6).

| Context | Zentrale Objekte | Konsistenz |
|---------|------------------|------------|
| **Katalog** | Produktdefinition, ProduktdefinitionsVersion, Prüfprozedur, ProzedurSchritt, PrüfschrittVorlage, Routine, Externes Kommando | Entwurf änderbar; Version unveränderlich |
| **Prüfausführung** | Prüflauf | Referenz auf ProduktdefinitionsVersion; enthält PrüfschrittDurchführungen und Nachweise |
| **Protokoll** | ProtokollSnapshot | Unveränderlich nach Erstellung |
| **Identity** | Benutzer, Berechtigungsprofil, Einweisungsnachweis | Rollen, Profile↔Produktdefinition-IDs, Einweisung↔Versions-IDs; nur ID-Referenzen zu Katalog |

**Context-Grenzen Identity:** Identity besitzt die Zuordnung **Profil ↔ Produktdefinition**. Zwischen Identity, Katalog, Prüfausführung und Protokoll nur **IDs** — **keine Domain-Imports** zwischen den Contexts ([ADR-0023](adr/0023-identity-bounded-context.md)). Authentifizierung V1: Session-Cookie ([ADR-0024](adr/0024-authentication-v1.md)); Qualifikation: [ADR-0026](adr/0026-qualification-model.md).

**Keine eigenständigen Wurzeln:** Einzelne Nachweise, Beurteilungen — Teil von PrüfschrittDurchführung bzw. Prüflauf.

---

## 6. Schichtenmodell

| Schicht | Zweck |
|---------|-------|
| **Frontend (PC / Mobile)** | Bedienoberfläche |
| **API** | Transport, Session, kein Fachwissen |
| **Application** | Use-Case-Orchestrierung |
| **Domain** | Fachregeln je Context |
| **Ports** | Domänensprachliche Verträge |
| **Adapter** | Technische Implementierungen |

---

## 7. Verantwortlichkeiten je Schicht

### Domain (je Context)

- **Katalog:** Produktdefinition, ProduktdefinitionsVersion, Basisprodukt, Option, Kundenprofil, Prüfprozedur, ProzedurSchritt, PrüfschrittVorlage, Routine, Sollvorgabe, Sollbestückung, Aktivierungsregel, ExternesKommando.
- **Prüfausführung:** Prüflauf, PrüfschrittDurchführung, Nachweis, Beurteilung, Pflichtschritt-Regeln, Routine-Ausführung.
- **Protokoll:** ProtokollSnapshot, Archiv-Invarianten.
- **Identity:** Benutzer, Systemrollen, Berechtigungsprofile, Einweisungsnachweise, Prüferpräferenzen.

### Ports

| Port | Verantwortung |
|------|---------------|
| `KatalogRepository` | Persistenz Katalog (Entwurf, Version) |
| `BibliothekRepository` | Facade für Bibliotheksobjekte im Katalog (`ExternesKommando`, Routine, PrüfschrittVorlage) |
| `PrueflaufRepository` | Persistenz Prüfläufe |
| `ExternesKommandoPort` | Ausführung externer Kommandos an Prüfobjekte (Run Time — nicht Katalog-Bibliothek) |
| `ProtokollErzeugungPort` | PDF-Erzeugung aus ProtokollSnapshot |
| `DruckPort` | Druck (zukünftig; Gate 8.4 nutzt Browser-PDF-Viewer, kein DruckPort) |
| `DateiSpeicherPort` | Fotos, Dateien — Gate 8.3a ✅ ([ADR-0022](adr/0022-foto-nachweis-dateispeicher.md)) |
| Identity-Repositories / Session-Ports | Benutzer, Profile, Einweisungen, Session — Gate 8.1 ([ADR-0023](adr/0023-identity-bounded-context.md), [ADR-0024](adr/0024-authentication-v1.md)); Implementierung ab 8.1a |

### Adapter

Technologie benennen (`com/`, `postgresql/`, `pdf/`), nicht Port-Namen.

---

## 8. Grundlegender Datenfluss

### Prüfung starten

1. Prüfer gibt **Produktkodierung** und **Prüfobjekt-Kennung** ein.
2. Application löst die **aktive ProduktdefinitionsVersion** auf.
3. **Prüfausführung** legt **Prüflauf** an — mit unveränderlicher Versionsreferenz.
4. Frontend erhält aktive **ProzedurSchritte** (ggf. gefiltert durch Aktivierungsregeln).

### PrüfschrittDurchführung mit Routine

1. **PrüfschrittDurchführung** für ProzedurSchritt wird angelegt.
2. Routine erzeugt **Nachweise** (Ist-Werte, Rohantworten, Fotos, …).
3. **Beurteilung** vergleicht Nachweise mit **Sollvorgaben** der Version.
4. Externe Kommandos über **Port** und Adapter (z. B. COM).

### Prüfung abschließen

1. Pflichtschritte und Gesamtvalidität prüfen (gültig/ungültig).
2. **ProtokollSnapshot** erzeugen — auch bei ungültigem Lauf.
3. Optional: PDF über `ProtokollErzeugungPort`.

---

## 9. Wichtige Abgrenzungen

- Keine Fachlogik in API, UI oder Adaptern.
- Keine gerätespezifische Logik im Domain-Kern.
- Prüflauf referenziert **ProduktdefinitionsVersion** — kein ad-hoc Snapshot, kein Live-Entwurf.
- Abgeschlossene Prüfläufe und ProtokollSnapshots sind unveränderlich.

---

## 10. Offene Architekturfragen

- Synchronisation PC/Smartphone
- Speicherstrategie für Fotos/Nachweise — Gate 8.3a ✅ ([ADR-0022](adr/0022-foto-nachweis-dateispeicher.md)); S3-Adapter offen
- Mehrsprachigkeit Protokoll vs. UI

Siehe auch offene Punkte in `docs/domain-model.md`.
