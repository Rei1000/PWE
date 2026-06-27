# 02 – Agent Write Pflichtenheft

## Pflicht: Agent Task Frame

Vor Ausführung dieses Prompts MUSS der Agent den vollständigen Arbeitsrahmen anwenden:

prompts/agent/00-agent-task-frame.md

Dieser Prompt darf NICHT ausgeführt werden, wenn der Task Frame nicht vorher vollständig abgearbeitet wurde.

---


## Ziel

Dieser Prompt überführt die Ergebnisse der GPT-Phase in ein konkretes Pflichtenheft im Repository.

---

## Anweisung an den Agenten

Die GPT-Phase hat eine strukturierte Pflichtenheft-Vorbereitung geliefert.

Du sollst jetzt:

- diese Inhalte übernehmen
- in die Datei `docs/pflichtenheft.md` einarbeiten
- den Goldstandard einhalten

---

## Deine Aufgabe

1. sicherstellen, dass du dich auf dem richtigen Feature-Branch befindest
2. Datei öffnen oder erstellen:

docs/pflichtenheft.md

3. Inhalte aus der GPT-Phase strukturiert einfügen

---

## Regeln

- keine Inhalte erfinden
- keine Struktur verändern ohne Grund
- keine technischen Details hinzufügen
- keine Architektur beschreiben
- nur fachliche Inhalte übernehmen

---

## Erwarteter Output

Am Ende musst du liefern:

- geänderte Datei: docs/pflichtenheft.md
- kurze Beschreibung der übernommenen Inhalte
- Bestätigung, dass keine anderen Dateien verändert wurden

---

## Nächster Schritt

Danach folgt:

`prompts/agent/03-agent-architecture-setup.md`

---

## Verwendung

Diesen Prompt erst verwenden, wenn die GPT-Pflichtenheft-Vorbereitung vollständig vorliegt.
