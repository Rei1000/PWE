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

### Variante A — lokal ohne Docker (In-Memory)

```bash
# Backend-API (In-Memory, kein PostgreSQL nötig)
cd backend && pip install ".[dev,persistence,pdf,api]"
uvicorn api.app:create_app --factory --reload --port 8000

# Optional: COM-Adapter (serieller Port, erfordert pyserial)
# pip install ".[dev,persistence,pdf,api,com]"
# EXTERNES_KOMMANDO_ADAPTER=com SERIELL_PORT=/dev/ttyUSB0 uvicorn api.app:create_app --factory --reload --port 8000

# Frontend (separates Terminal)
cd frontend/web && npm install && npm run dev
```

### Variante B — Docker (API + PostgreSQL)

```bash
docker compose up --build
# Frontend separat: cd frontend/web && npm run dev
```

Details: [`README-docker.md`](README-docker.md)

### Demo-/Labor-Automatisierung (Gate 6.3c)

Reproduzierbarer Setup **nur über öffentliche HTTP-API** — kein `/dev`-Endpoint, kein Ersatz für Katalog-Admin (Gate 8.2).

```bash
# 1) API mit explizitem Demo-Simulationsmodus
cd backend && pip install ".[dev,persistence,pdf,api]"
PWE_DEMO_MODE=true EXTERNES_KOMMANDO_ADAPTER=simulation \
  uvicorn api.app:create_app --factory --reload --port 8000

# 2) Demo-Seed (nicht idempotent — jeder Lauf erzeugt neue Katalogobjekte)
python3 scripts/seed_demo_automatisierung.py --api-base http://127.0.0.1:8000

# 3) Frontend
cd frontend/web && npm run dev
# ausgegebene URL öffnen, z. B. http://localhost:5173/prueflaeufe/<id>

# 4) Komponente „komponente-a“ erfassen → Automatisierung ausführen
```

Ohne `PWE_DEMO_MODE=true` bleibt die Simulation leer (kein verstecktes Demo-Verhalten).
