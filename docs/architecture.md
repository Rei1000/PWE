# Architektur – PWE (Initialversion)

## 1. Ziel der Architektur

Die Architektur von PWE stellt sicher, dass die **Prüf-Workflow-Engine** als konfigurierbarer Kern wartbar, erweiterbar und von technischen Details entkoppelt bleibt. Fachlogik, Anwendungssteuerung und Infrastruktur werden strikt getrennt.

Leitprinzipien:

- **Domain-Driven Design (DDD)** für fachliche Klarheit und Bounded Contexts.
- **Hexagonale Architektur (Ports/Adapter)** für Austauschbarkeit technischer Komponenten (Datenbank, externe Schnittstellen, PDF, Druck).
- **Test-Driven Development (TDD)** als Umsetzungsprinzip in der Implementierungsphase.

**Engine vs. erste Anwendung:** Der fachliche Kern modelliert Prüfprozesse, Prüfläufe, Schritte, Routinen und Protokolle generisch. Die Ergometer-Endprüfung ist die erste **Konfiguration** dieser Engine — nicht der Architekturmittelpunkt.

Die verbindliche Begriffswelt ist in `docs/projektrules.md` (Ubiquitous Language) dokumentiert.

---

## 2. Design Time und Run Time

Die Domäne lässt sich entlang des Lebenszyklus von Prüfdefinitionen und Prüfinstanzen trennen. Diese Sicht vereinfacht Bounded-Context-Grenzen — sie ist kein zusätzlicher technischer Layer.

| Phase | Context | Frage |
|-------|---------|-------|
| **Design Time** | Katalog | *Was* darf geprüft werden und *wie* ist der Prozess definiert? |
| **Run Time** | Prüfausführung | *Wie* wird ein konkreter Prüfvorgang ausgeführt und bewertet? |
| **Post-Run Time** | Protokoll | *Was* ist der unveränderliche Nachweis eines abgeschlossenen Prüflaufs? |

**Identity** und **Auswertung** sind querschnittlich: Identity steuert Zugriff und Präferenzen; Auswertung liest abgeschlossene Daten (CQRS-Read-Seite) ohne den Prüflauf-Kern zu verändern.

---

## 3. Systemkontext

| Akteur / System | Rolle |
|-----------------|-------|
| Prüfer (PC) | Hauptarbeitsplatz für Prüfungsdurchführung und Konfiguration (Admin) |
| Prüfer (Smartphone) | Parallele Prüfungsbegleitung im lokalen Netzwerk |
| Externes Prüfobjekt | Über konfigurierte Schnittstellen angebunden (z. B. COM in der ersten Anwendung) |
| Drucker | Ausgabe von Prüfprotokollen |
| PostgreSQL | Persistenz von Katalogdaten, Prüfläufen und Archivdaten |
| Externe Arbeitsanweisungen | Referenzierte Dokumente, nicht im Systemkern |

**Systemgrenze:** PWE modelliert und führt konfigurierbare Prüfworkflows aus, erzeugt Protokolle und wertet Prüfdaten aus. ERP-Systeme und gerätespezifische Fachlogik außerhalb der Konfiguration gehören nicht zum Kern.

---

## 4. Fachliche Kernbereiche (Bounded Contexts)

| Context | Phase | Verantwortung |
|---------|-------|---------------|
| **Katalog** | Design Time | Produktvarianten, Basisprodukte, Stammdaten, Prüfschritt-Bibliothek, Prüfprozeduren, Routinen, externe Kommandos, Arbeitsanweisungs-Referenzen |
| **Prüfausführung** | Run Time | Prüflauf-Lebenszyklus, Schrittausführung, Eingaben, Pflichtschritte, Status, Wiederholungsprüfung, Routine-Orchestrierung |
| **Protokoll** | Post-Run Time | Unveränderliches Archiv, Protokollerzeugung, Fotos, Historie |
| **Identity** | Querschnitt | Benutzer, Rollen (Admin/User), persönliche Schrittreihenfolge |
| **Auswertung** | Read Model | Dashboard, Statistiken, Filter — liest abgeschlossene Prüfläufe, verändert keine Prüfdaten |

In der ersten Anwendung sind z. B. Artikelnummer, Grundmodell und Platine **Konfigurationsinstanzen** von Produktvariante, Basisprodukt und Komponente.

**Bewusst kein eigener Context:**

- **Gerätekommunikation / COM:** Kein Bounded Context. Externe Kommunikation ist ein **Port** mit technischem **Adapter** (z. B. COM-Treiber). Die fachliche Semantik (Kommando senden/lesen, Soll-Ist-Vergleich) gehört zu **Katalog** (Definition) bzw. **Prüfausführung** (Ausführung).
- **Arbeitsplatz:** Kein Domain-Context. Konfiguration von COM-Port, Drucker und Speicherpfad ist **Infrastruktur-/Deployment-Konfiguration**, nicht Fachdomäne.

Abhängigkeiten zwischen Contexts laufen über Application Services und Ports, nicht über direkte Infrastruktur-Kopplung.

---

## 5. Aggregate (fachliche Konsistenzgrenzen)

| Context | Aggregate Root | Konsistenzgrenze |
|---------|----------------|------------------|
| **Katalog** | `Produktvariante` | Zuordnung Produktvariante → Prüfprozedur, verknüpfte Stammdaten |
| **Katalog** | `Pruefprozedur` | Zusammenstellung und Versionierung einer Prozedur |
| **Katalog** | `PruefschrittVorlage` | Wiederverwendbare Schrittdefinition in der Bibliothek |
| **Katalog** | `Routine` | Aktionsfolge inkl. Referenzen auf externe Kommandos |
| **Katalog** | `ExternesKommando` | Definition eines externen Kommandos |
| **Prüfausführung** | `Prueflauf` | Gesamter Laufzeitstatus: Schritte, Eingaben, Messwerte, Kommentare |
| **Protokoll** | `ProtokollSnapshot` | Unveränderlicher Nachweis eines abgeschlossenen Prüflaufs |
| **Identity** | `Benutzer` | Konto, Rolle, persönliche Schrittreihenfolge |

**Keine Aggregate:** Einzelne Eingabefelder, Messwerte oder Fotos sind Entitäten/Wertobjekte *innerhalb* von `Prueflauf` bzw. `ProtokollSnapshot` — keine eigenen Aggregate Roots.

---

## 6. Schichtenmodell

| Schicht | Zweck |
|---------|-------|
| **Frontend (PC)** | Bedienoberfläche für Prüfung, Verwaltung und Dashboard |
| **Frontend (Mobile)** | Smartphone-Oberfläche für parallele Prüfungsbegleitung (Scan, Foto, Eingaben) |
| **API** | Transportschicht (HTTP/WebSocket), Session- und Zugriffsrahmen, kein Fachwissen |
| **Application** | Use-Case-Orchestrierung über Bounded Contexts hinweg |
| **Domain** | Fachregeln, Entitäten, Wertobjekte, Invarianten je Context |
| **Ports** | Technologieneutrale Verträge (Persistenz, externe Kommandos, PDF, Druck, Dateispeicher) |
| **Adapter/Infrastruktur** | Technische Implementierungen: `com/`, `postgresql/`, `pdf/`, … |

**Abhängigkeitsregel:** Abhängigkeiten zeigen nach innen. Domain kennt weder Framework noch Datenbank noch konkrete Kommunikationsprotokolle.

---

## 7. Verantwortlichkeiten je Schicht

### Domain (je Context)

- **Katalog:** Produktvariante, Prüfprozedur, PrüfschrittVorlage, Routine, Aktion, Sollwert, ExternesKommando.
- **Prüfausführung:** Prüflauf, Schrittstatus, Eingabefelder, Pflichtschritt-Regeln, Routine-Ausführungslogik (ohne Kenntnis konkreter Kommunikationsprotokolle).
- **Protokoll:** Archiv-Invarianten, Protokollzusammenstellung.
- **Identity:** Rollen, Berechtigungsregeln, persönliche Schrittreihenfolge.
- **Auswertung:** Aggregations- und Filterbegriffe (Read Model, keine Domain-Invarianten).

### Application

- Use Cases aus dem Pflichtenheft orchestrieren.
- Koordination zwischen Domain-Contexts und Ports.
- Synchronisation PC/Smartphone-Sitzungen.

### Ports (fachliche Verträge — Domänensprache)

| Port | Verantwortung |
|------|---------------|
| `KatalogRepository` | Persistenz von Katalog-Aggregaten |
| `PrueflaufRepository` | Persistenz von Prüfläufen |
| `ExternesKommandoPort` | Senden/Lesen externer Kommandos an Prüfobjekte |
| `ProtokollErzeugungPort` | Erzeugung eines Prüfprotokolls (Ausgabeformat) |
| `DruckPort` | Ausgabe eines Protokolls auf Drucker |
| `DateiSpeicherPort` | Speicherung und Abruf von Dateien (Fotos, Archive) |

Ports sprechen ausschließlich Domänensprache — keine Protokoll-, Format- oder Framework-Details.

### Adapter (technische Implementierungen)

Adapter benennen die **Technologie oder das Protokoll**, nicht den Port. Ein Port kann mehrere Adapter haben (Open/Closed Principle).

| Port | Adapter (Beispiele) |
|------|---------------------|
| `ExternesKommandoPort` | `com/` (v1), später `can/`, `usb/`, `tcp/`, `rest/`, `simulation/` |
| `KatalogRepository`, `PrueflaufRepository`, … | `persistence/postgresql/` |
| `ProtokollErzeugungPort` | `pdf/` |
| `DruckPort` | `print/` |
| `DateiSpeicherPort` | `storage/filesystem/` |

Die Auswahl des Adapters erfolgt zur Laufzeit über Arbeitsplatz-Konfiguration (`infra/config/`), nicht über Domain-Code.

---

## 8. Grundlegender Datenfluss

### Prüfung starten

1. Prüfer gibt Produktvariante und Prüfobjekt-Kennung ein (in der ersten Anwendung: Artikelnummer und Geräteseriennummer).
2. Application ermittelt über **Katalog** die passende Prüfprozedur.
3. **Prüfausführung** legt neuen Prüflauf an.
4. Frontend erhält Schrittliste (ggf. benutzerindividuelle Reihenfolge aus **Identity**).

### Prüfschritt mit Routine ausführen

1. **Prüfausführung** startet Schritt; Routine wird aus Katalog-Definition geladen.
2. Application führt Aktionen sequenziell aus (warten, Sollwertvergleich, Benutzerbestätigung, externes Kommando).
3. Bei Aktion „externes Kommando": Application ruft **Port** auf; Adapter (z. B. COM) führt technische Kommunikation aus.
4. Ergebnisse fließen zurück in **Prüfausführung** für Statusentscheidung.
5. Bei paralleler Nutzung: Synchronisation an gekoppelte Sitzung.

### Prüfung abschließen

1. **Prüfausführung** prüft Pflichtschritte und Gesamtstatus.
2. **Protokoll** erzeugt unveränderliches Archiv (PDF über Port).
3. Optional: Druck über Port.

---

## 9. Wichtige Abgrenzungen

- Keine Fachlogik in API, UI oder Infrastruktur-Adaptern.
- Keine gerätespezifische oder ergometerspezifische Logik im Domain-Kern — nur konfigurierbare Definitionen im Katalog.
- Externe Kommandos und Routinen sind konfigurierbar, nicht hardcodiert.
- Abgeschlossene Prüfläufe sind schreibgeschützt.
- Technologiehinweise (Python, PostgreSQL, COM) sind Orientierung für die erste Anwendung, keine Architektur-Festlegung.

---

## 10. Offene Architekturfragen

- Automatische Erkennung eines Arbeitsplatzes (Konfiguration vs. Erkennung).
- Synchronisationsmechanismus PC/Smartphone (Polling vs. Push/WebSocket).
- Speicherstrategie für Fotos (Dateisystem vs. Datenbank vs. Hybrid).
- Mehrsprachigkeit: i18n-Schicht vs. kundenspezifische Protokolltemplates.
- Skalierung auf mehrere Arbeitsplätze (zentrale DB, dezentrale Adapter-Anbindung).
