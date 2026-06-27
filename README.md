# PWE — Prüf-Workflow-Engine

## Kurzbeschreibung

PWE ist eine **konfigurierbare Prüf-Workflow-Engine** zur Durchführung und Dokumentation von Endprüfungen. Die erste Anwendung ist die Ergometer-Endprüfung — als **Konfiguration** der Engine, nicht als fachlicher Kern.

Prüfprozesse werden vollständig über **Produktdefinitionen** modelliert: Der Administrator pflegt vollständige Prüfvorgaben, veröffentlicht sie als **ProduktdefinitionsVersion**, und neue **Prüfläufe** referenzieren diese unveränderliche Version.

## Ziel

Standardisierte Endprüfungen: Prüferführung, Nachweise, Beurteilungen, ProtokollSnapshots — erweiterbar für weitere Gerätetypen ohne Engine-Änderung.

## Dokumentation

| Dokument | Inhalt |
|----------|--------|
| `.goldstandard/context.txt` | Project DNA (Einstieg für Agenten) |
| **`docs/domain-model.md`** | **Verbindliche Fachdomäne** (Referenz) |
| `docs/pflichtenheft.md` | Fachliche Anforderungen |
| `docs/architecture.md` | Technische Architektur |
| `docs/projectstructure.md` | Repository-Struktur |
| `docs/projektrules.md` | Projektregeln |
| **`docs/roadmap.md`** | **Projektfortschritt & nächste Slices** |

## Schnellstart (Entwicklung)

```bash
# Backend-API
cd backend && pip install ".[dev,persistence,pdf,api]"
uvicorn api.app:create_app --factory --reload --port 8000

# Frontend (separates Terminal)
cd frontend/web && npm install && npm run dev
```

Details: `frontend/web/README.md`
