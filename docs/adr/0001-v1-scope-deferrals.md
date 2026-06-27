# ADR-0001: V1-Umfang und bewusste Zurückstellungen

## Status

Accepted

## Kontext

Das Pflichtenheft beschreibt PC- und Smartphone-Nutzung, Export, Mehrarbeitsplatz und weitere Features. Vor Technical Design und Implementierung muss der V1-Umfang begrenzt werden, um Architekturdrift zu vermeiden.

## Entscheidung

**V1 liefert:**

- Prüfung am **PC-Arbeitsplatz** (ein Prüfer, eine Sitzung)
- Vollständiger Prüflauf-Kern: Start → Schritte → Nachweise → Beurteilungen → ProtokollSnapshot
- Katalog: ProduktdefinitionsVersion materialisieren und referenzieren
- PostgreSQL-Persistenz (nach Domain-Slice)
- Externes Kommando über Adapter (Simulation in Tests, COM später)

**V1 liefert nicht (explizit V2+):**

- Parallele Bearbeitung PC + Smartphone (kein Sync-Modell in V1)
- QR-Code-Kopplung / Mobile-App
- CSV/Excel-Export
- Grafischer Routine-Editor
- Automatische Arbeitsplatz-Erkennung
- Mehrsprachige UI (UI Deutsch; Protokollsprache aus Kundenprofil bleibt vorbereitet)

**Persönliche Schrittreihenfolge (Domain Model §12):** Rein **UI-Darstellung** in V1. ProtokollSnapshot und Beurteilungen folgen der **materialisierten Prozedurreihenfolge**, nicht der individuellen Sortierung.

## Konsequenzen

- Kein Sync-ADR in V1 nötig
- API/Frontend V1: nur PC-Web
- Pflichtenheft-Features für Smartphone bleiben gültig, aber **priorisiert zurückgestellt**

## Alternativen

- Smartphone parallel in V1: verworfen — Sync-Modell ungeklärt, höchstes technisches Risiko
- Alles aus Pflichtenheft in V1: verworfen — unbounded scope
