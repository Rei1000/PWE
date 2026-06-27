# Projektrichtlinien – PWE

Verbindliche Grundsätze für Entwicklung, Architektur und Agent-Arbeit in diesem Repository.

---

## Agent-Ausführungsregeln (verpflichtend)

Vor jeder Agent-Aufgabe ist verpflichtend folgender Arbeitsrahmen anzuwenden:

`prompts/agent/00-agent-task-frame.md`

Ohne vollständige Anwendung dieses Rahmens darf keine Analyse, Implementierung, Refactoring-, Dokumentations-, Test- oder Git-Aktion durchgeführt werden.

---

## Architecture Reflection (verpflichtend)

Vor jeder größeren Architekturentscheidung muss die aktuelle Lösung kritisch hinterfragt werden.

Es ist ausdrücklich zu prüfen:

- ob eine fachlich bessere Lösung existiert,
- ob die Domäne weiter vereinfacht werden kann,
- ob technische Konzepte versehentlich in der Domäne gelandet sind,
- ob Best Practices verletzt werden,
- ob die Entscheidung langfristig tragfähig ist.

Erst danach darf eine Architekturentscheidung als abgeschlossen gelten.

---

## Engine First

PWE ist eine **Prüf-Workflow-Engine**.

Konkrete Anwendungen (z. B. Ergometer-Endprüfung) dürfen **niemals** die Architektur der Engine bestimmen.

Spezialisierungen erfolgen ausschließlich durch **Konfiguration** und **Adapter** — nicht durch gerätespezifischen Domain-Code.

---

## Domain First

Die Fachdomäne hat Vorrang vor technischen Überlegungen.

Technische Infrastruktur darf **niemals** die Domäne formen.

Ports und Adapter folgen der Domäne — nicht umgekehrt.

---

## Simplicity First

Neue Abstraktionen sind nur zulässig, wenn sie die Domäne tatsächlich vereinfachen.

Verallgemeinerungen dürfen **niemals** Selbstzweck sein.

Lieber ein klares, kleines Domänenmodell als vorzeitige Modularisierung ohne fachlichen Nutzen.

---

## Best Practice Challenge

Der Agent ist verpflichtet, die eigene Lösung kontinuierlich mit anerkannten Best Practices zu vergleichen (DDD, hexagonale Architektur, Aggregate-Grenzen, CQRS wo sinnvoll).

Er darf bestehende Entscheidungen jederzeit hinterfragen, sofern dadurch die Architektur fachlich verbessert wird.

---

## Ubiquitous Language (verbindlich)

Die Engine spricht generische Begriffe. Begriffe der ersten Anwendung sind **Konfigurationsinstanzen**, keine Engine-Invarianten.

| Engine-Begriff | Bedeutung | Erste Anwendung (Ergometer) |
|----------------|-----------|---------------------------|
| **Prüfobjekt** | Das zu prüfende Objekt | Ergometer |
| **Prüfobjekt-Kennung** | Eindeutige Identifikation des konkreten Prüfobjekts | Geräteseriennummer |
| **Produktvariante** | Konfiguration einer prüfbaren Variante; verknüpft Stammdaten und Prüfprozedur | Artikelnummer (mit Grundmodell/Kunde/Ausstattung) |
| **Basisprodukt** | Übergeordnete Produktfamilie mit Sollwerten und Standardinformationen | Grundmodell (erste 6 Stellen der Artikelnummer) |
| **Prüfprozedur** | Definiert den Prüfablauf für eine Produktvariante | (gleich) |
| **Prüfschritt** | Einzelner Schritt in einer Prozedur oder Bibliothek | (gleich) |
| **Prüflauf** | Laufzeitinstanz einer Prüfung | (gleich) |
| **Routine** | Automatisierbare Aktionsfolge innerhalb eines Schritts | (gleich) |
| **Externes Kommando** | Konfigurierbares Kommando an ein externes System | COM-Kommando |
| **Komponente** | Austauschbares Teil mit optionaler Seriennummer | Platine |
| **Prüfprotokoll** | Unveränderlicher Nachweis eines abgeschlossenen Prüflaufs | PDF-Protokoll |

**Abgrenzung:** „Prüfung" bezeichnet den Vorgang; „Prüflauf" ist die persistierte Laufzeitinstanz mit Zustand und Ergebnissen.

---

## Ports und Adapter (verbindlich)

| Schicht | Benennung | Sprache | Beispiel |
|---------|-----------|---------|----------|
| **Domain** | Entitäten, Value Objects, Domain Services | Fachdomäne | `ExternesKommando`, `Prueflauf` |
| **Ports** | Interfaces / Protocols in `ports/` | Fachdomäne | `ExternesKommandoPort` |
| **Adapter** | Implementierungen in `adapters/` | Technologie/Protokoll | `com/`, `postgresql/`, `pdf/` |

**Regeln:**

- Ports sprechen **ausschließlich** Domänensprache — niemals COM, CAN, REST, PDF oder PostgreSQL.
- Adapter benennen die **technische Implementierung** — niemals den Port-Namen als Ordner.
- **Ein Port, viele Adapter:** `ExternesKommandoPort` wird von `com/`, `can/`, `rest/`, `simulation/` implementiert.
- Die Adapter-Auswahl erfolgt über Konfiguration (`infra/config/`), nicht über Domain-if/else.
- Test-Doubles (Mock, Simulation) sind Adapter und gehören unter `adapters/simulation/` oder `tests/adapters/`.

**Anti-Pattern (verboten):** `adapters/externes_kommando/` — vermischt Port-Sprache mit Adapter-Schicht und erschwert mehrere Implementierungen.

---

## 1. Produktvision

- **PWE ist eine konfigurierbare Prüf-Workflow-Engine** — keine gerätespezifische Endprüf-Software.
- **Ergometer-Endprüfung** ist die erste konkrete Anwendung und wird ausschließlich über **Stammdaten und Konfiguration** abgebildet.
- **Konfigurierbarkeit steht über Spezialisierung:** Neue Prüfobjekttypen, Prozeduren und Schnittstellen sollen ohne Programmcode-Änderung am Engine-Kern möglich sein.

---

## 2. Architektur-Grundsätze

| Grundsatz | Bedeutung |
|-----------|-----------|
| **Engine-Kern generisch** | Domain-Code modelliert Prüfprozesse, Prüfläufe, Schritte, Routinen und Protokolle — nicht Ergometer, Platinen oder COM-Protokolle. |
| **Erste Anwendung = Konfiguration** | Artikelnummern, Grundmodelle, Platinen, Sollwerte, externe Kommandos und Protokollinhalte sind **Katalogdaten**. |
| **Design Time / Run Time** | Katalog definiert (Design Time); Prüfausführung führt aus (Run Time); Protokoll friert Ergebnisse ein. |
| **DDD + Hexagonal** | Bounded Contexts mit klaren Grenzen; externe Systeme nur über Ports/Adapter. |
| **TDD** | Tests vor oder parallel zur Implementierung; Domain-Logik ohne Infrastruktur testbar. |
| **Unveränderlichkeit** | Abgeschlossene Prüfläufe und Prüfprotokolle dürfen nicht nachträglich geändert werden. |

---

## 3. Verboten in der Fachlogik (Domain/Application)

- Gerätespezifische oder ergometerspezifische **if/else-Logik** im Domain-Kern.
- COM-, Seriell-, HTTP- oder PDF-Details in Domain-Modulen.
- Bounded Context „Gerät" oder vergleichbare technische Kontexte in der Domain-Schicht.
- ORM- oder SQL-Abhängigkeiten in der Domain-Schicht.
- Duplizierung von Fachregeln in Frontend oder API.

**Erlaubt:** Konfigurierbare Aktionstypen (z. B. „externes Kommando senden"), deren **Definition** im Katalog und deren **Ausführung** über Ports/Adapter erfolgt.

---

## 4. Systemgrenzen

- **Einzugsbereich:** Konfiguration und Durchführung von Endprüfungen, Protokollierung, Archivierung, Auswertung.
- **Schnittstellen:** Externe Prüfobjekte über Adapter (COM in der ersten Anwendung), Drucker, externe Arbeitsanweisungen als Referenzen.
- **Nicht-Ziele:** ERP-Integration, gerätespezifische Fachlogik im Code, grafischer Routine-Editor (v1), CSV/Excel-Export (v1), vollständige Auditierung externer Kommunikation (v1).

---

## 5. Bounded Contexts (verbindlich)

| Context | Phase | Kurzbeschreibung |
|---------|-------|------------------|
| **Katalog** | Design Time | Stammdaten und Prüfkonfiguration |
| **Prüfausführung** | Run Time | Prüfläufe, Schritte, Routine-Orchestrierung |
| **Protokoll** | Post-Run Time | Unveränderliches Archiv und Protokollerzeugung |
| **Identity** | Querschnitt | Benutzer, Rollen, Berechtigungen |
| **Auswertung** | Read Model | Dashboard und Statistiken (CQRS-Seite) |

Gerätekommunikation ist **kein** Bounded Context — sie wird über den Port `ExternesKommandoPort` und technische Adapter (z. B. `adapters/com/`) angebunden.

---

## 6. Validierungsprinzipien

- Eingaben werden gegen konfigurierte Regeln geprüft (Definition im Katalog, Auswertung in Prüfausführung).
- Fehler dem Nutzer verständlich mitteilen; technische Details loggen.
- Keine stillen Korrekturen ohne Rückmeldung.

---

## 7. Verweise

- Fachliche Anforderungen: `docs/pflichtenheft.md`
- Architektur: `docs/architecture.md`
- Projektstruktur: `docs/projectstructure.md`
- Datenmodell-Leitlinien: `docs/datenbankmodell.md`
- Projektkontext: `.goldstandard/context.txt`
