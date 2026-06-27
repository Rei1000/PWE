# 04 – Agent Project Structure

## Pflicht: Agent Task Frame

Vor Ausführung dieses Prompts MUSS der Agent den vollständigen Arbeitsrahmen anwenden:

prompts/agent/00-agent-task-frame.md

Dieser Prompt darf NICHT ausgeführt werden, wenn der Task Frame nicht vorher vollständig abgearbeitet wurde.

---


## Ziel

Dieser Prompt dient dazu, aus Pflichtenheft und Architektur eine erste sinnvolle Projektstruktur im Repository abzuleiten.

---

## Anweisung an den Agenten

Pflichtenheft und Architektur wurden bereits vorbereitet.

Du sollst jetzt daraus die erste konkrete Projektstruktur ableiten und im Repository sauber dokumentieren oder anlegen.

WICHTIG:
- keine unnötigen Dateien
- keine Fachlogik-Implementierung
- nur Struktur und Platzhalter
- klare Trennung von Verantwortlichkeiten

---

## Deine Aufgabe

1. sicherstellen, dass du dich auf dem richtigen Feature-Branch befindest
2. bestehende Struktur prüfen
3. falls nötig Datei öffnen oder erstellen:

docs/projectstructure.md

4. daraus die erste konkrete Projektstruktur ableiten

Je nach Projektstand kann dies beinhalten:

- Struktur dokumentieren
- Ordner anlegen
- Platzhalterdateien anlegen

---

## Regeln

- keine Implementierung
- keine unnötige Tiefe
- keine Doppelstrukturen
- Struktur muss aus Architektur und Pflichtenheft folgen
- klare Trennung zwischen Domain, Application, Adapter, API und Frontend

---

## Erwarteter Output

Am Ende musst du liefern:

- geänderte oder angelegte Strukturdateien
- ggf. angelegte Ordner/Platzhalter
- kurze Beschreibung der gewählten Struktur
- Bestätigung, dass keine unnötigen Änderungen vorgenommen wurden

---

## Nächster Schritt

Nach diesem Schritt kann die eigentliche Umsetzungsphase beginnen.

---

## Verwendung

Diesen Prompt erst verwenden, wenn `docs/architecture.md` sinnvoll vorbereitet ist.
