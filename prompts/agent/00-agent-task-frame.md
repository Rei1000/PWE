# Agent Task Frame (Goldstandard Pflichtvorlage)

## Ziel

Dieses Dokument ist der verpflichtende Arbeitsrahmen für jede Agent-Aufgabe.

Der Agent darf KEINE Implementierung starten, bevor alle folgenden Schritte durchgeführt wurden.

---

## Pflichtformat der Antwort

Der Agent MUSS jede Aufgabe in folgender Struktur beantworten:

1. Projektregeln geprüft  
2. Aufgabenanalyse  
3. Architektur-Einordnung  
4. Teststrategie  
5. Implementierungsplan  
6. Durchführung  
7. Testergebnis  
8. Abschlussprüfung  

Fehlt einer dieser Punkte, gilt die Aufgabe als NICHT korrekt ausgeführt.

---

## 1. Projektregeln prüfen

Vor jeder Aufgabe MUSS der Agent folgende Dokumente berücksichtigen:

- projektrules.md
- cursor rules
- vorhandene Architektur-Dokumentation
- Pflichtenheft (falls vorhanden)

---

## 2. Aufgabenanalyse

Der Agent muss die Aufgabe zuerst einordnen:

- Handelt es sich um:
  - Feature
  - Bugfix
  - Refactoring
  - Infrastruktur

- Welche Teile des Systems sind betroffen?

---

## 3. Architektur-Einordnung

Der Agent muss festhalten:

- In welche Schicht gehört die Änderung?
  - UI
  - Application
  - Domain
  - Infrastruktur

- Ist die Änderung kompatibel mit:
  - DDD
  - Hexagonaler Architektur

---

## 4. Teststrategie (TDD – PFLICHT)

Vor jeder Implementierung MUSS der Agent:

- konkrete Testfälle definieren
- erwartetes Verhalten beschreiben
- Edge Cases identifizieren

Wenn sinnvoll:
- Tests ZUERST schreiben (TDD)

Der Agent darf NICHT implementieren, wenn:

- keine Testfälle definiert wurden
- keine Risiken benannt wurden

Ausnahme:
Nur wenn logisch BEGRÜNDET wird, warum Tests nicht notwendig sind.

---

## STOP-Bedingung

Wenn eine der folgenden Bedingungen nicht erfüllt ist, MUSS der Agent abbrechen:

- Projektregeln nicht geprüft  
- Architektur nicht eingeordnet  
- keine Teststrategie vorhanden  

In diesem Fall MUSS der Agent den Nutzer darauf hinweisen und DARF NICHT implementieren.

---

## 5. Implementierung

Erst jetzt darf der Agent:

- Code schreiben
- Struktur ändern

Dabei gilt:

- klare Trennung von Logik und IO
- keine versteckten Seiteneffekte
- keine unnötige Komplexität
- Implementierung muss der vorher definierten Teststrategie folgen

---

## 6. Tests ausführen

- Tests müssen ausgeführt werden  
- Tests müssen nachvollziehbar grün sein  
- Fehler müssen behoben werden  

Der Agent darf NICHT abschließen, wenn:

- Tests fehlen  
- Tests fehlschlagen  

---

## 7. Abschlussprüfung

Vor Abschluss MUSS geprüft werden:

- Entspricht die Änderung den Projektregeln?
- Ist die Architektur eingehalten?
- Ist der Code testbar?
- Sind keine unnötigen Änderungen enthalten?
- Stimmen Implementierung und Teststrategie überein?

---

## 8. Verboten

Der Agent darf NICHT:

- direkt implementieren ohne Analyse
- Regeln ignorieren
- Tests überspringen
- große Änderungen ohne Struktur machen
- nicht überprüften Code committen

---

## Ergebnis

Der Agent arbeitet strukturiert, regelkonform und reproduzierbar nach dem Goldstandard.

---

## Git-Abschlussprüfung

git status --short

Erwartung:

 M prompts/agent/00-agent-task-frame.md

Keine anderen Änderungen.

---

## Verboten

- kein git add .
- kein Commit
- kein Push

---

## Ergebnis

Eine verpflichtende Agent-Arbeitsvorlage für alle zukünftigen Aufgaben.
