# 01 – Agent Run Workflow

## Pflicht: Agent Task Frame

Vor Ausführung dieses Workflows MUSS der Agent den vollständigen Arbeitsrahmen anwenden:

`prompts/agent/00-agent-task-frame.md`

Dieser Workflow darf NICHT ausgeführt werden, wenn der Agent Task Frame nicht vorher vollständig abgearbeitet wurde.

---

## Ausführende Partei

Cursor-Agent / Code-Agent

---

## Ziel

Dieser Prompt ist der zentrale Einstiegspunkt für die Agent-Phase in einem neu erzeugten Projekt.

Er koordiniert die initiale Agent-Arbeit nach Abschluss der GPT-Phase.

Der Nutzer soll diesen Prompt im Zielprojekt verwenden, damit der Agent den vollständigen Startprozess strukturiert durchführt.

---

## Voraussetzung

Vor Ausführung dieses Workflows müssen vorhanden sein:

- `prompts/agent/00-agent-task-frame.md`
- `prompts/agent/01-agent-project-bootstrap.md`
- `prompts/agent/02-agent-write-pflichtenheft.md`
- `prompts/agent/03-agent-architecture-setup.md`
- `prompts/agent/04-agent-project-structure.md`

Wenn eine dieser Dateien fehlt, MUSS der Agent abbrechen und den Nutzer informieren.

---

## Kontext laden

Primär soll der Agent zuerst lesen:

`.goldstandard/context.txt`

Falls `.goldstandard/context.txt` nicht existiert, ist der im Prompt enthaltene Kontext zu verwenden.

Dieser Kontext ist die verbindliche fachliche Grundlage für alle folgenden Schritte.

Der Agent darf keine fachlichen Inhalte erfinden, die nicht aus diesem Kontext oder den Projektdokumenten hervorgehen.

---

## Ausführungsreihenfolge

Der Agent MUSS die folgenden Prompts in dieser Reihenfolge verwenden:

1. `prompts/agent/01-agent-project-bootstrap.md`
2. `prompts/agent/02-agent-write-pflichtenheft.md`
3. `prompts/agent/03-agent-architecture-setup.md`
4. `prompts/agent/04-agent-project-structure.md`

Die Reihenfolge darf nicht geändert werden.

---

## Arbeitsweise

Für jeden Schritt gilt:

1. jeweiligen Prompt lesen
2. Aufgabe gegen den verfügbaren Projektkontext prüfen
3. Agent Task Frame anwenden
4. notwendige Dateien bestimmen
5. Umsetzung durchführen
6. Tests bzw. Prüfungen ausführen, soweit für den Schritt sinnvoll
7. Ergebnis dokumentieren
8. erst danach zum nächsten Schritt wechseln

---

## Stop-Bedingungen

Der Agent MUSS abbrechen, wenn:

- kein verwertbarer Projektkontext vorliegt (weder Datei noch Prompt-Kontext)
- ein erforderlicher Agent-Prompt fehlt
- der Agent Task Frame nicht angewendet werden kann
- fachliche Informationen fehlen, die für den nächsten Schritt zwingend notwendig sind
- Tests oder Prüfungen fehlschlagen
- Änderungen außerhalb des erlaubten Scopes erforderlich wären

---

## Ergebnis

Am Ende dieses Workflows müssen mindestens geprüft oder erzeugt sein:

- `docs/pflichtenheft.md`
- `docs/architecture.md`
- `docs/projectstructure.md`
- ggf. notwendige Platzhalterstruktur
- Abschlussbericht mit:
  - ausgeführten Schritten
  - geänderten Dateien
  - offenen Punkten
  - Test-/Prüfergebnissen

---

## Wichtige Regel

Dieser Workflow ist kein Freibrief für unkontrollierte Implementierung.

Er dient nur dazu, die initiale Projektstruktur und Projektdokumentation aus dem GPT-Handover-Kontext aufzubauen.

Keine Fachlogik, kein Produktcode und keine Infrastrukturänderung dürfen ohne expliziten Auftrag über diesen Workflow hinaus umgesetzt werden.

---

## Abschluss

Wenn alle Schritte erfolgreich abgeschlossen sind, meldet der Agent:

- welche Prompts ausgeführt wurden
- welche Dateien geändert oder erstellt wurden
- welche offenen Punkte bestehen
- ob der nächste Schritt ein Commit/PR sein sollte
