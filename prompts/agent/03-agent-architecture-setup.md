# 03 – Agent Architecture Setup

## Pflicht: Agent Task Frame

Vor Ausführung dieses Prompts MUSS der Agent den vollständigen Arbeitsrahmen anwenden:

prompts/agent/00-agent-task-frame.md

Dieser Prompt darf NICHT ausgeführt werden, wenn der Task Frame nicht vorher vollständig abgearbeitet wurde.

---


## Ziel

Dieser Prompt dient dazu, nach dem Pflichtenheft die erste Version der Architektur im Repository aufzubauen.

---

## Anweisung an den Agenten

Die GPT-Phase ist abgeschlossen und das Pflichtenheft wurde bereits in `docs/pflichtenheft.md` überführt.

Du sollst jetzt die erste Architekturgrundlage im Repository aufbauen.

WICHTIG:
- Architektur basiert auf den bisherigen fachlichen Ergebnissen
- keine Implementierung
- keine unnötige technische Spezialisierung
- Fokus auf Struktur, Schichten und Verantwortlichkeiten

---

## Deine Aufgabe

1. sicherstellen, dass du dich auf dem richtigen Feature-Branch befindest
2. Datei öffnen oder erstellen:

docs/architecture.md

3. auf Basis von Pflichtenheft und GPT-Ergebnissen die erste Architekturstruktur ausarbeiten

Dabei mindestens beschreiben:

- Ziel der Architektur
- Systemkontext
- Schichtenmodell
- Verantwortlichkeiten je Schicht
- grundlegender Datenfluss
- wichtige Abgrenzungen

---

## Regeln

- keine Implementierung
- keine Details erfinden, die fachlich nicht geklärt sind
- keine unnötigen Technologien festschreiben
- DDD und hexagonale Architektur als Leitprinzipien berücksichtigen
- Fachlogik und Infrastruktur klar trennen

---

## Erwarteter Output

Am Ende musst du liefern:

- geänderte Datei: docs/architecture.md
- kurze Beschreibung der angelegten Architekturstruktur
- Bestätigung, dass keine anderen Dateien verändert wurden

---

## Nächster Schritt

Danach folgt:

`prompts/agent/04-agent-project-structure.md`

---

## Verwendung

Diesen Prompt erst verwenden, wenn `docs/pflichtenheft.md` bereits sinnvoll befüllt ist.
