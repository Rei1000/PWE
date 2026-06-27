# Pflichtenheft – PWE

## 0. Engine-Charakter

PWE ist eine **konfigurierbare Prüf-Workflow-Engine** — keine Spezialsoftware für ein einzelnes Gerät.

- Der **Engine-Kern** umfasst: Prüfprozeduren, Prüfschritte, Routinen, Prüfläufe, Eingabefelder, Pflichtschritte, Protokolle und Archivierung.
- Die **Ergometer-Endprüfung** ist die erste konkrete Anwendung dieser Engine.
- Begriffe wie Artikelnummer, Grundmodell, Platinen oder COM-Kommandos beschreiben die **Konfiguration der ersten Anwendung** — in der Engine heißen die Entsprechungen Produktvariante, Basisprodukt, Komponente und Externes Kommando (siehe `docs/projektrules.md`).
- Neue Prüfobjekte oder Gerätetypen werden durch **Konfiguration und Adapter**, nicht durch gerätespezifischen Programmcode unterstützt.

---

## 1. Ziel

- **Produktname:** PWE (Prüf-Workflow-Engine)
- **Geschäftsziel:** Entwicklung einer konfigurierbaren Prüfplattform, welche Endprüfungen standardisiert, den Prüfer durch den gesamten Prüfablauf führt, manuelle Dokumentation reduziert, automatisierte Kommunikation mit externen Prüfobjekten ermöglicht und vollständige Prüfprotokolle erzeugt.
- **Erfolgskriterien (fachlich):**
  - Prüfprozesse sind vollständig über Stammdaten und Konfiguration modellierbar.
  - Neue Prüfobjektvarianten können ohne Programmcode-Änderungen am Engine-Kern unterstützt werden.
  - Prüfer werden durch den gesamten Prüfablauf geführt und erhalten vollständige Protokolle.
  - Unterbrochene und Wiederholungsprüfungen sind fachlich sauber abbildbar.
  - Abgeschlossene Prüfungen sind unveränderlich archiviert.

---

## 2. Systemkontext

- **Überblick:** PWE ist eine konfigurierbare Plattform zur Durchführung und Dokumentation von Endprüfungen. Die erste konkrete Anwendung ist die Endprüfung von Ergometern.
- **Zentraler Schlüssel (erste Anwendung):** Die Artikelnummer (Engine-Begriff: **Produktvariante**) steuert die Zuordnung von Grundmodell, Kunde, Ausstattung und Prüfprozedur.
- **Benutzer und Systeme in der Umgebung:**
  - Prüfer (PC-Arbeitsplatz)
  - Prüfer (Smartphone, parallele Nutzung im lokalen Netzwerk)
  - Administratoren (Stammdaten, Konfiguration)
  - Externes Prüfobjekt (in der ersten Anwendung: Ergometer über COM-Schnittstelle)
  - Drucker (Protokollausgabe)
- **Externe Referenzen:** Arbeitsanweisungen werden als externe Referenzen hinterlegt, nicht im System selbst erstellt.
- **Systemgrenze:** Der fachliche Kern ist die Prüf-Workflow-Engine; die Ergometerprüfung ist eine Konfiguration, kein Architekturmittelpunkt.

---

## 3. Nutzergruppen

| Gruppe | Bedürfnisse | Berechtigungen (grob) |
|--------|-------------|------------------------|
| Admin | Stammdaten, Prüfschritte, Routinen, Prüfprozeduren, externe Kommandos, Systemeinstellungen verwalten | Vollzugriff auf Konfiguration und Verwaltung |
| User (Prüfer) | Prüfung durchführen, fortsetzen, wiederholen; persönliche Reihenfolge der Prüfschritte anpassen | Prüfungsdurchführung, Historie durchsuchen, eigene Schrittreihenfolge |

---

## 4. Hauptfunktionen

### 4.1 Prüfungsdurchführung

1. Prüfung starten über Produktvariante und Prüfobjekt-Kennung (in der ersten Anwendung: Artikelnummer und Geräteseriennummer).
2. Automatische Zuordnung der passenden Prüfprozedur.
3. Speicherung unvollständiger Prüfungen und Fortsetzen unterbrochener Prüfungen.
4. Wiederholungsprüfungen mit optionaler Übernahme vorheriger Prüfdaten.
5. Parallele Bearbeitung am PC und Smartphone (QR-Code-Kopplung).
6. Fotodokumentation, Barcode- und QR-Code-Erfassung.
7. Seriennummern manuell erfassen oder über konfigurierte Schnittstellen automatisch auslesen.
8. Abschlussbestätigung mit Optionen: Speichern, Speichern und Drucken.

### 4.2 Konfiguration und Stammdaten (Katalog)

1. Verwaltung von Grundmodellen, Artikelnummern, Kunden, Ausstattungen, Platinen, Sollwerten und Arbeitsplätzen.
2. Verwaltung globaler Prüfschritt-Bibliothek.
3. Erstellung und Verwaltung von Prüfprozeduren (inkl. Kopieren).
4. Wiederverwendung von Prüfschritten.
5. Verwaltung externer Kommandos (in der ersten Anwendung: COM-Kommandos) und automatisierter Routinen.
6. Verknüpfung von Arbeitsanweisungen, Warn- und Sicherheitshinweisen zu Prüfschritten.

### 4.3 Prüfschritte und Eingaben

1. Prüfschritte mit mehreren Eingabefeldern.
2. Eingabefeldtypen: Text, Zahl, Auswahl, Checkbox, Datum, Seriennummer, Barcode/QR.
3. Validierung von Eingabefeldern.
4. Konfigurierbare Pflichtschritte; Überspringen nur mit Kommentar, sofern erlaubt.
5. Prüfschrittstatus: bestanden, nicht bestanden, bestanden mit Kommentar.

### 4.4 Automatisierung und externe Schnittstellen

1. Konfigurierbare Kommunikation mit externen Prüfobjekten (in der ersten Anwendung: COM zum Lesen und Schreiben von Geräteparametern).
2. Soll-Ist-Vergleich ausgelesener Werte.
3. Routinen mit konfigurierbaren Aktionen: externes Kommando senden/lesen, warten, Messwert speichern, Sollwert vergleichen, Benutzerbestätigung, Kommentar, Foto, Fehlerbedingung.
4. Routinen können nach Nachbesserung wiederholt werden.

### 4.5 Protokoll, Archiv und Auswertung

1. Automatische PDF-Erstellung mit konfigurierbaren Inhalten (in der ersten Anwendung u. a.: Zusammenfassung, Prüfer, Datum, Artikelnummer, Geräteseriennummer, Prüfschritte, Kommentare, Fotos, Geräteeinstellungen, Firmwareversionen, Platinen-Seriennummern).
2. PDF-Dateiname basiert auf der Prüfobjekt-Kennung (in der ersten Anwendung: Geräteseriennummer); Fotos komprimiert im PDF.
3. Archivierung aller Prüfläufe; Historie pro Prüfobjekt; Suche nach Prüfobjekt-Kennung.
4. Dashboard mit häufigsten Durchfallgründen, Abbruchgründen und Bauteilwechseln; Filter nach Zeitraum, Grundmodell, Kunde und Artikelnummer.

---

## 5. Fachliche Regeln und Leitlinien

- **FR-001 (Produktvariante; erste Anwendung: Artikelnummer):** Erste sechs Stellen definieren das Basisprodukt (Grundmodell); der restliche Teil definiert Kunde und Ausstattung. Jeder Produktvariante ist genau eine aktive Prüfprozedur zugeordnet.
- **FR-002 (Konfigurierbarkeit):** Erweiterbarkeit ohne Programmcode-Änderungen am Engine-Kern durch Konfiguration; Konfigurierbarkeit steht über Spezialisierung.
- **FR-003 (Pflichtschritte):** Pflichtschritte müssen erfolgreich abgeschlossen werden. Nicht bestandene Pflichtschritte machen den gesamten Prüflauf ungültig. Ungültige Prüfungen dürfen gespeichert und dokumentiert werden.
- **FR-004 (Unveränderlichkeit):** Bereits abgeschlossene Prüfungen dürfen nicht geändert werden. Neue Prüfungen erzeugen einen neuen Prüflauf; frühere Prüfläufe bleiben vollständig erhalten.
- **FR-005 (Benutzerrechte):** Benutzer dürfen ausschließlich ihre persönliche Reihenfolge der Prüfschritte verändern. Administratoren verwalten Stammdaten, Prüfschritte, Routinen und Prüfprozeduren.
- **FR-006 (Dokumentation):** Kommentare werden vollständig protokolliert. Bauteilwechsel werden über Kommentare dokumentiert; bei Ersatz mit Seriennummer muss die neue Seriennummer erfasst werden.
- **FR-007 (Protokollsprache):** Protokollsprache richtet sich nach dem Kunden der Artikelnummer; Bedienoberfläche zunächst Deutsch.
- **FR-008 (Basisprodukt; erste Anwendung: Grundmodell):** Basisprodukte besitzen eigene Sollwerte, Komponenten und Standardinformationen.
- **FR-009 (Prüfstruktur):** Prüfprozeduren bestehen aus wiederverwendbaren Prüfschritten; Prüfschritte können optional Routinen enthalten; Routinen bestehen aus konfigurierbaren Aktionen; externe Kommandos werden zentral verwaltet.

---

## 6. Nicht-funktionale Anforderungen

- **Einsatz:** Anwendung zunächst lokal einsetzbar; mehrere Arbeitsplätze perspektivisch möglich.
- **Datenbank:** PostgreSQL von Beginn an.
- **Mehrsprachigkeit:** Architektur für spätere Mehrsprachigkeit vorbereiten.
- **Netzwerk:** Smartphone und PC arbeiten im selben lokalen Netzwerk; Smartphone-Sitzung bleibt aktiv und wird nach 30 Minuten Inaktivität getrennt.
- **Archivierung:** Fotos dauerhaft archivieren; Historisierung abgeschlossener Prüfläufe; abgeschlossene Protokolle bleiben unveränderlich.
- **Arbeitsplatz:** Standard-Schnittstelle (in der ersten Anwendung: COM-Port) und Drucker je Arbeitsplatz konfigurierbar; globaler Speicherpfad für Protokolle.
- **PDF:** Layout mit konfigurierbarem Logo sowie Kopf- und Fußbereich.

---

## 7. Offene Punkte und Unsicherheiten

- Automatische Erkennung eines Arbeitsplatzes noch nicht definiert.
- Unterstützung von Bildern innerhalb von Arbeitsanweisungen wird später betrachtet.
- Exportfunktionen (CSV/Excel) sind nicht Bestandteil der ersten Version.
- Vollständige Auditierung der externen Kommunikation ist zunächst nicht vorgesehen.
- Unterstützung weiterer Prüfobjekttypen erfolgt in späteren Projektphasen.
- Grafischer Routine-Editor ist nicht Bestandteil der ersten Version.

---

## 8. Abgrenzungen

- Keine Produktcode-Implementierung in diesem Dokument.
- Keine detaillierte technische Architektur (siehe `architecture.md`).
- Kein grafischer Routine-Editor in der ersten Version.
- Keine CSV-/Excel-Exportfunktionen in der ersten Version.
- Keine vollständige Auditierung der externen Kommunikation in der ersten Version.
- Keine gerätespezifische Fachlogik im Engine-Kern — Ergometer-Aspekte ausschließlich über Konfiguration.
