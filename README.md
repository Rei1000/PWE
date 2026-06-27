# PWE — Prüf-Workflow-Engine

## Kurzbeschreibung

PWE ist eine **konfigurierbare Prüf-Workflow-Engine** zur Durchführung und Dokumentation von Endprüfungen. Die erste Anwendung ist die Ergometer-Endprüfung — als **Konfiguration** der Engine, nicht als fachlicher Kern.

Prüfprozesse werden vollständig über **Produktdefinitionen** modelliert: Der Administrator pflegt vollständige Prüfvorgaben, veröffentlicht sie als **ProduktdefinitionsVersion**, und neue **Prüfläufe** referenzieren diese unveränderliche Version.

## Ziel

Standardisierte Endprüfungen: Prüferführung, Nachweise, Beurteilungen, ProtokollSnapshots — erweiterbar für weitere Gerätetypen ohne Engine-Änderung.

## Dokumentation

| Dokument | Inhalt |
|----------|--------|
| **`docs/domain-model.md`** | **Verbindliche Fachdomäne** (Referenz) |
| `docs/pflichtenheft.md` | Fachliche Anforderungen |
| `docs/architecture.md` | Technische Architektur |
| `docs/projectstructure.md` | Repository-Struktur |
| `docs/projektrules.md` | Projektregeln |
| `.goldstandard/context.txt` | Project DNA (Einstieg für Agenten) |
