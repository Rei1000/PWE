# Projektrichtlinien – PWE

Verbindliche Grundsätze für Entwicklung, Architektur und Agent-Arbeit in diesem Repository.

---

## Fachliche Referenz (verbindlich)

**`docs/domain-model.md`** ist die verbindliche Beschreibung der PWE-Fachdomäne.

Alle Projektdokumente, Architekturentscheidungen und Implementierungen müssen sich an diesem Dokument orientieren. Bei Widersprüchen gilt das Domain Model.

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

Die verbindliche Begriffswelt ist in **`docs/domain-model.md`** definiert. Kurzfassung:

| Engine-Begriff | Bedeutung | Erste Anwendung (Ergometer) |
|----------------|-----------|---------------------------|
| **Produktkodierung** | Kodierung zur Auflösung einer Produktdefinition | Artikelnummer |
| **Produktdefinition** | Vollständige Prüfvorgabe im Entwurf (änderbar) | — |
| **ProduktdefinitionsVersion** | Veröffentlichte, unveränderliche Prüfvorgabe | — |
| **Basisprodukt** | Produktfamilie mit Standardinformationen | Grundmodell |
| **Option** | Ausstattungsmerkmal | z. B. Blutdruck, WLAN |
| **Kundenprofil** | Kundenspezifische Vorgaben und Regeln | OEM-Schlüssel (Oxx) oder Default |
| **Prüfobjekt** | Konkret zu prüfendes Exemplar | Ergometer |
| **Prüfobjekt-Kennung** | Eindeutige Identifikation des Exemplars | Geräteseriennummer |
| **Prüfprozedur** | Geordnete Folge von ProzedurSchritten | — |
| **ProzedurSchritt** | Verwendung einer PrüfschrittVorlage in einer Prozedur | — |
| **PrüfschrittVorlage** | Wiederverwendbare Schrittdefinition (Bibliothek) | — |
| **PrüfschrittDurchführung** | Laufzeitausführung eines ProzedurSchritts | — |
| **Routine** | Automatisierbare Aktionsfolge | — |
| **Externes Kommando** | Konfigurierbares Kommando an ein externes System | COM-Kommando |
| **Sollvorgabe** | Erwarteter Wert, Bereich oder Regel | — |
| **Sollbestückung** | Erwartete Komponenten | z. B. Mainboard, BD-Platine |
| **Prüflauf** | Laufzeitinstanz einer Prüfung | — |
| **Nachweis** | Beleg auf Schrittebene | Messwert, Foto, Rohantwort, … |
| **Beurteilung** | Fachliche Bewertung eines Schritts | bestanden / nicht bestanden / mit Kommentar |
| **ProtokollSnapshot** | Unveränderlicher Abschlussnachweis eines Prüflaufs | PDF-Ausgabe |

**Abgrenzungen:**

- **Prüfung** = Vorgang; **Prüflauf** = persistierte Instanz.
- **PrüfschrittVorlage** → **ProzedurSchritt** → **PrüfschrittDurchführung** (Definition → Verwendung → Laufzeit).
- **Nachweis** ≠ **Beurteilung** (Evidenz vs. Urteil).
- **ProduktdefinitionsVersion** ≠ ad-hoc Snapshot pro Lauf — der Prüflauf **referenziert** die Version.

Veraltete Begriffe (**Produktvariante**, **Schrittstatus**, **Prüfschritt** ohne Kontext) sind nicht mehr zu verwenden.

---

## Ports und Adapter (verbindlich)

| Schicht | Benennung | Sprache | Beispiel |
|---------|-----------|---------|----------|
| **Domain** | Domänenobjekte | Fachdomäne | `Prueflauf`, `Nachweis` |
| **Ports** | Interfaces in `ports/` | Fachdomäne | `ExternesKommandoPort` |
| **Adapter** | Implementierungen in `adapters/` | Technologie/Protokoll | `com/`, `postgresql/`, `pdf/` |

**Regeln:**

- Ports sprechen **ausschließlich** Domänensprache — niemals COM, CAN, REST, PDF oder PostgreSQL.
- Adapter benennen die **technische Implementierung** — niemals den Port-Namen als Ordner.
- **Ein Port, viele Adapter:** `ExternesKommandoPort` wird von `com/`, `can/`, `rest/`, `simulation/` implementiert.
- Die Adapter-Auswahl erfolgt über Konfiguration (`infra/config/`), nicht über Domain-if/else.

---

## 1. Produktvision

- **PWE ist eine konfigurierbare Prüf-Workflow-Engine** — keine gerätespezifische Endprüf-Software.
- **Ergometer-Endprüfung** ist die erste konkrete Anwendung und wird ausschließlich über **Produktdefinitionen und Konfiguration** abgebildet.
- **Konfigurierbarkeit steht über Spezialisierung:** Neue Prüfobjekttypen, Prozeduren und Schnittstellen sollen ohne Programmcode-Änderung am Engine-Kern möglich sein.

---

## 2. Architektur-Grundsätze

| Grundsatz | Bedeutung |
|-----------|-----------|
| **Engine-Kern generisch** | Domain-Code modelliert Prüfprozesse, Prüfläufe, Schritte, Routinen, Nachweise und Protokolle — nicht Ergometer oder COM-Protokolle. |
| **Erste Anwendung = Konfiguration** | Artikelnummern, Platinen, externe Kommandos und Protokollinhalte sind **Katalogdaten**. |
| **Design Time / Run Time / Post-Run Time** | Katalog (Entwurf/Version) → Prüfausführung → ProtokollSnapshot. |
| **Veröffentlichte Vorgabe** | Neue Prüfläufe referenzieren ausschließlich eine **ProduktdefinitionsVersion**. |
| **DDD + Hexagonal** | Bounded Contexts mit klaren Grenzen; externe Systeme nur über Ports/Adapter. |
| **TDD** | Tests vor oder parallel zur Implementierung; Domain-Logik ohne Infrastruktur testbar. |
| **Unveränderlichkeit** | Abgeschlossene Prüfläufe und ProtokollSnapshots dürfen nicht nachträglich geändert werden. |

---

## 3. Verboten in der Fachlogik (Domain/Application)

- Gerätespezifische oder ergometerspezifische **if/else-Logik** im Domain-Kern.
- COM-, Seriell-, HTTP- oder PDF-Details in Domain-Modulen.
- Bounded Context „Gerät" oder vergleichbare technische Kontexte in der Domain-Schicht.
- ORM- oder SQL-Abhängigkeiten in der Domain-Schicht.
- Duplizierung von Fachregeln in Frontend oder API.

---

## 4. Systemgrenzen

- **Einzugsbereich:** Konfiguration und Durchführung von Endprüfungen, Protokollierung, Archivierung, Auswertung.
- **Schnittstellen:** Externe Prüfobjekte über Adapter (COM in der ersten Anwendung), Drucker, externe Arbeitsanweisungen, Produktlaufkarte als Eingangsinformation.
- **Nicht-Ziele:** Fertigungssteuerung, ERP-Integration, gerätespezifische Fachlogik im Code.

---

## 5. Bounded Contexts (verbindlich)

| Context | Phase | Kurzbeschreibung |
|---------|-------|------------------|
| **Katalog** | Design Time | Produktdefinition, Versionen, Bibliothek (Vorlagen, Routinen, Kommandos) |
| **Prüfausführung** | Run Time | Prüflauf, PrüfschrittDurchführung, Nachweise, Beurteilungen |
| **Protokoll** | Post-Run Time | ProtokollSnapshot |
| **Identity** | Querschnitt | Benutzer, Rollen, Berechtigungen |
| **Auswertung** | Read Model | Dashboard und Statistiken |

Gerätekommunikation ist **kein** Bounded Context — sie wird über `ExternesKommandoPort` und technische Adapter (z. B. `adapters/com/`) angebunden.

---

## 6. Validierungsprinzipien

- Eingaben werden gegen konfigurierte Regeln geprüft (Definition in Produktdefinition/Version, Auswertung in Prüfausführung).
- Fehler dem Nutzer verständlich mitteilen; technische Details loggen.
- Keine stillen Korrekturen ohne Rückmeldung.

---

## 7. Entwicklungsprozess (Roadmap-Slices)

Verbindlicher Ablauf für Implementierungsarbeit. Details zum Fortschritt: **`docs/roadmap.md`**.

### Führende Arbeitsgrundlage

- **`docs/roadmap.md`** bestimmt den **nächsten** Umsetzungsschritt.
- Vor jedem Slice: Roadmap **kritisch prüfen** — ist der geplante Schritt noch der richtige?
- Abweichungen nur **bewusst**, mit Begründung im Roadmap-Changelog.

### Slice-Regeln

| Regel | Bedeutung |
|-------|-----------|
| **Ein Slice pro Branch/PR** | Genau ein Roadmap-Punkt; kein Scope Creep |
| **Feature-Branch** | Nie direkt auf `main`; Branch z. B. `feat/<slice-name>` |
| **main lauffähig** | `main` bleibt nach jedem Merge merge-fähig und CI-grün |
| **Kein Vorziehen** | Spätere Roadmap-Gates nicht vorzeitig umsetzen |

### Ablauf pro Slice

1. `main` aktualisieren, Feature-Branch anlegen
2. Roadmap prüfen und ggf. begründet anpassen
3. **Nur** den aktuellen Slice implementieren (TDD wo sinnvoll)
4. Betroffene Dokumentation aktualisieren (Roadmap Pflicht)
5. **Architektur-Review** vor PR (siehe unten)
6. **Selbstkritik:** eigene Lösung bewusst widerlegen
7. **Nur P0-Blocker** vor PR beheben; P1/P2 dokumentieren
8. Commit → Push → Pull Request
9. Merge **erst** nach Review-Freigabe und grünem CI

### Architektur-Review vor Pull Request

Pflicht vor jedem PR; baut auf „Architecture Reflection“ (oben) auf. Prüfen:

- Domain Model, Architecture, Technical Domain, relevante ADRs
- Bounded Contexts, Aggregate-Grenzen, hexagonale Schichten
- Domain-Invarianten nicht in API/Frontend dupliziert
- Scope Creep und Five-Year-Tragfähigkeit

Ergebnis im PR oder Abschlussbericht festhalten.

### Git und Merge

- Commits fokussiert; keine Misch-Commits über Slice-Grenzen
- Squash-Merge bevorzugt, wenn sinnvoll
- Kein Merge bei rotem CI oder offenen P0-Punkten

### Unveränderte Architekturprinzipien

Domain First, Engine First, hexagonale Architektur und Frontend als Driving Adapter gelten in jedem Slice unverändert (siehe oben und `docs/architecture.md`).

---

## 8. Verweise

- **Fachdomäne (Referenz):** `docs/domain-model.md`
- Architekturentscheidungen: `docs/adr/`
- Technical Domain Design: `docs/technical-domain/`
- Fachliche Anforderungen: `docs/pflichtenheft.md`
- Architektur: `docs/architecture.md`
- Projektstruktur: `docs/projectstructure.md`
- Datenmodell-Leitlinien: `docs/datenbankmodell.md`
- Project DNA: `.goldstandard/context.txt`
