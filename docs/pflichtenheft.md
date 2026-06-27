# Pflichtenheft – PWE

Fachliche Anforderungen. Verbindliche Domänensprache: **`docs/domain-model.md`**.

---

## 0. Engine-Charakter

PWE ist eine **konfigurierbare Prüf-Workflow-Engine** — keine Spezialsoftware für ein einzelnes Gerät.

- Der **Engine-Kern** umfasst: Produktdefinitionen, Prüfprozeduren, PrüfschrittVorlagen, Routinen, Prüfläufe, Nachweise, Beurteilungen und ProtokollSnapshots.
- Die **Ergometer-Endprüfung** ist die erste konkrete Anwendung dieser Engine.
- Begriffe wie Artikelnummer, Grundmodell, Platinen oder COM-Kommandos beschreiben die **Konfiguration der ersten Anwendung** — in der Engine heißen die Entsprechungen Produktkodierung, Basisprodukt, Komponente und Externes Kommando.
- Neue Prüfobjekttypen werden durch **Konfiguration und Adapter**, nicht durch gerätespezifischen Programmcode unterstützt.

---

## 1. Ziel

- **Produktname:** PWE (Prüf-Workflow-Engine)
- **Geschäftsziel:** Entwicklung einer konfigurierbaren Prüfplattform, welche Endprüfungen standardisiert, den Prüfer durch den gesamten Prüfablauf führt, manuelle Dokumentation reduziert, automatisierte Kommunikation mit externen Prüfobjekten ermöglicht und vollständige **ProtokollSnapshots** erzeugt.
- **Erfolgskriterien (fachlich):**
  - Prüfprozesse sind vollständig über Produktdefinitionen und Konfiguration modellierbar.
  - Neue Prüfobjektvarianten können ohne Programmcode-Änderungen am Engine-Kern unterstützt werden.
  - Prüfer werden durch den gesamten Prüfablauf geführt und erhalten vollständige ProtokollSnapshots.
  - Unterbrochene und Wiederholungsprüfungen sind fachlich sauber abbildbar.
  - Abgeschlossene Prüfläufe sind unveränderlich archiviert.

---

## 2. Systemkontext

- **Überblick:** PWE ist eine konfigurierbare Plattform zur Durchführung und Dokumentation von Endprüfungen. Die erste konkrete Anwendung ist die Endprüfung von Ergometern.
- **Zentraler Schlüssel (erste Anwendung):** Die Artikelnummer (**Produktkodierung**) löst die passende **Produktdefinition** und deren aktive **ProduktdefinitionsVersion** auf.
- **Benutzer und Systeme in der Umgebung:**
  - Prüfer (PC-Arbeitsplatz)
  - Prüfer (Smartphone, parallele Nutzung im lokalen Netzwerk)
  - Administratoren (Produktdefinitionen, Katalog, Konfiguration)
  - Externes Prüfobjekt (in der ersten Anwendung: Ergometer über COM-Schnittstelle)
  - Drucker (Protokollausgabe)
  - Produktlaufkarte (Eingangsinformation aus der Produktion, optional)
- **Externe Referenzen:** Arbeitsanweisungen werden als externe Referenzen hinterlegt.
- **Systemgrenze:** PWE beginnt beim Qualitätsprozess; Fertigungssteuerung gehört nicht zum Kern.

---

## 3. Nutzergruppen

| Gruppe | Bedürfnisse | Berechtigungen (grob) |
|--------|-------------|------------------------|
| Admin | Produktdefinitionen, Katalog, PrüfschrittVorlagen, Routinen, Prüfprozeduren, externe Kommandos, Systemeinstellungen | Vollzugriff auf Konfiguration und Veröffentlichung |
| User (Prüfer) | Prüfung durchführen, fortsetzen, wiederholen; persönliche Reihenfolge der Schritte anpassen | Prüfungsdurchführung, Historie durchsuchen, eigene Schrittreihenfolge |

---

## 4. Hauptfunktionen

### 4.1 Prüfungsdurchführung

1. Prüfung starten über **Produktkodierung** und **Prüfobjekt-Kennung** (erste Anwendung: Artikelnummer und Geräteseriennummer); Bindung an die aktive **ProduktdefinitionsVersion**.
2. Automatische Zuordnung der materialisierten Prüfprozedur aus der Version.
3. Speicherung unvollständiger Prüfläufe und Fortsetzen unterbrochener Prüfungen.
4. Wiederholungsprüfungen — standardmäßig mit der **aktuell freigegebenen** ProduktdefinitionsVersion; optional Übernahme vorheriger Prüfdaten.
5. Parallele Bearbeitung am PC und Smartphone (QR-Code-Kopplung).
6. Fotodokumentation, Barcode- und QR-Code-Erfassung als **Nachweise**.
7. Seriennummern manuell erfassen oder über Routinen/Externe Kommandos auslesen.
8. Abschlussbestätigung mit **ProtokollSnapshot**; Optionen: Speichern, Speichern und Drucken.

### 4.2 Konfiguration (Katalog)

1. Verwaltung von Basisprodukten, Optionen, Kundenprofilen, Sollbestückungen, Sollvorgaben und Produktkodierungen.
2. Verwaltung der globalen **PrüfschrittVorlagen**-Bibliothek.
3. Erstellung und Verwaltung von **Produktdefinitionen** (Entwurf) und **Veröffentlichung** als ProduktdefinitionsVersion.
4. Erstellung und Verwaltung von Prüfprozeduren mit **ProzedurSchritten** (inkl. Kopieren).
5. Verwaltung externer Kommandos (erste Anwendung: COM) und Routinen.
6. **Aktivierungsregeln** an ProzedurSchritten (z. B. abhängig von Optionen).
7. Verknüpfung von Arbeitsanweisungen, Warn- und Sicherheitshinweisen zu PrüfschrittVorlagen.

### 4.3 PrüfschrittVorlagen und Eingaben

1. PrüfschrittVorlagen mit mehreren Eingabefeldern.
2. Eingabefeldtypen: Text, Zahl, Auswahl, Checkbox, Datum, Seriennummer, Barcode/QR.
3. Validierung von Eingabefeldern.
4. Konfigurierbare Pflichtschritte an ProzedurSchritten; Überspringen nur mit Kommentar-Nachweis, sofern erlaubt.
5. **Beurteilung** je PrüfschrittDurchführung: bestanden, nicht bestanden, bestanden mit Kommentar.

### 4.4 Automatisierung und externe Schnittstellen

1. Konfigurierbare Kommunikation mit externen Prüfobjekten über **Externe Kommandos** (erste Anwendung: COM).
2. **Routinen** erzeugen Ist-Werte; **Sollvorgaben** aus der ProduktdefinitionsVersion; **Beurteilung** vergleicht Soll und Ist.
3. Routinen mit konfigurierbaren Aktionen: externes Kommando senden/lesen, warten, Messwert speichern, Sollvergleich, Benutzerbestätigung, Kommentar, Foto, Fehlerbedingung.
4. Routinen können nach Nachbesserung wiederholt werden; neue **Nachweise** akkumulieren in der PrüfschrittDurchführung.
5. Rohantworten externer Kommandos werden grundsätzlich als Nachweise gespeichert.

### 4.5 Protokoll, Archiv und Auswertung

1. Automatische PDF-Erstellung aus **ProtokollSnapshot** (erste Anwendung: u. a. Zusammenfassung, Prüfer, Datum, Artikelnummer, Geräteseriennummer, Schritte, Nachweise, Fotos, Geräteeinstellungen, Firmware, Platinen-Seriennummern).
2. PDF-Dateiname basiert auf der Prüfobjekt-Kennung; Fotos komprimiert im PDF.
3. Archivierung aller Prüfläufe; Historie pro Prüfobjekt-Kennung.
4. Dashboard mit häufigsten Durchfallgründen, Abbruchgründen und Bauteilwechseln; Filter nach Zeitraum, Basisprodukt, Kundenprofil und Produktkodierung.

---

## 5. Fachliche Regeln und Leitlinien

- **FR-001 (Produktkodierung; erste Anwendung: Artikelnummer):** Erste sechs Stellen definieren das Basisprodukt; der restliche Teil definiert Optionen und Kundenprofil. Jede Produktdefinition hat genau eine **aktive** ProduktdefinitionsVersion für neue Prüfläufe.
- **FR-002 (Konfigurierbarkeit):** Erweiterbarkeit ohne Programmcode-Änderungen am Engine-Kern durch Konfiguration.
- **FR-003 (Pflichtschritte):** Pflicht-ProzedurSchritte müssen erfolgreich beurteilt werden. Nicht bestandene Pflichtschritte machen den Prüflauf ungültig. Ungültige Prüfläufe dürfen gespeichert und protokolliert werden.
- **FR-004 (Unveränderlichkeit):** Abgeschlossene Prüfläufe und ProtokollSnapshots sind unveränderlich. Neue Prüfungen erzeugen neuen Prüflauf.
- **FR-005 (Benutzerrechte):** Prüfer dürfen ausschließlich ihre persönliche Schrittreihenfolge ändern. Administratoren verwalten Katalog und Produktdefinitionen.
- **FR-006 (Dokumentation):** Kommentare und Bauteilwechsel werden als **Nachweise** protokolliert; neue Komponenten-Seriennummern müssen erfasst werden.
- **FR-007 (Protokollsprache):** Richtet sich nach dem Kundenprofil der Produktdefinition; Bedienoberfläche zunächst Deutsch.
- **FR-008 (Versionierung):** Neue Prüfläufe referenzieren ausschließlich eine veröffentlichte ProduktdefinitionsVersion; die Referenz ändert sich nie.
- **FR-009 (Prüfstruktur):** Prüfprozeduren bestehen aus ProzedurSchritten; ProzedurSchritte referenzieren PrüfschrittVorlagen; optional Routinen; externe Kommandos zentral verwaltet.
- **FR-010 (Audit):** Automatisch erzeugte Nachweise sind unveränderlich; Ergänzungen nur als neue Nachweise mit Bezug.

---

## 6. Nicht-funktionale Anforderungen

- **Einsatz:** Anwendung zunächst lokal einsetzbar; mehrere Arbeitsplätze perspektivisch möglich.
- **Datenbank:** PostgreSQL von Beginn an.
- **Mehrsprachigkeit:** Architektur für spätere Mehrsprachigkeit vorbereiten.
- **Netzwerk:** Smartphone und PC im selben lokalen Netzwerk; Smartphone-Sitzung nach 30 Minuten Inaktivität getrennt.
- **Archivierung:** Nachweise und Fotos dauerhaft archivieren; ProtokollSnapshots unveränderlich.
- **Arbeitsplatz:** Standard-Schnittstelle (erste Anwendung: COM-Port) und Drucker je Arbeitsplatz konfigurierbar.
- **PDF:** Layout mit konfigurierbarem Logo sowie Kopf- und Fußbereich.

---

## 7. Offene Punkte und Unsicherheiten

- Automatische Erkennung eines Arbeitsplatzes noch nicht definiert.
- Parallele Bearbeitung PC/Smartphone — Synchronisationsmodell fachlich offen.
- Exportfunktionen (CSV/Excel) nicht in der ersten Version.
- Grafischer Routine-Editor nicht in der ersten Version.

---

## 8. Abgrenzungen

- Keine Produktcode-Implementierung in diesem Dokument.
- Keine detaillierte technische Architektur (siehe `architecture.md`).
- Domänendetails: `docs/domain-model.md`.
- Keine gerätespezifische Fachlogik im Engine-Kern.
