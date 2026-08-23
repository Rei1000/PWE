# PWE Web (Frontend)

Driving Adapter für die PWE-HTTP-API. Stack: [ADR-0009](../../docs/adr/0009-frontend-stack.md).

## Voraussetzungen

- Node.js 20+
- Backend-API lokal auf Port 8000 (In-Memory oder via `docker compose up`, siehe [`README-docker.md`](../../README-docker.md))

## Entwicklung

```bash
# Terminal 1 — API
cd backend
pip install ".[dev,persistence,pdf,api]"
uvicorn api.app:create_app --factory --reload --host 127.0.0.1 --port 8000

# Terminal 2 — Frontend (Dev-Proxy /api → :8000)
cd frontend/web
npm install
npm run dev
```

Öffnen: http://localhost:5173

### Happy Path (Gate 6.2)

1. **Start** — Katalog seeden, Prüflauf starten
2. **Prüflauf** — Komponente erfassen, Nachweis, Beurteilung, Abschluss
3. **Abschluss** — PDF herunterladen

### Automatisierung (Gate 6.3b)

In der Prüflauf-Schrittkarte:

- Button nur bei `hat_automatisierung` / aktiv bei `kann_automatisierung_ausfuehren` (Backend-Read-Model)
- Zielendpoint: `POST .../automatisierung/ausfuehren` ([ADR-0016](../../docs/adr/0016-automatisierung-http-api.md))
- HTTP 200 mit `fehlgeschlagen=true` ist ein fachliches Ergebnis — kein API-Fehler
- Kein Auto-Retry; Hinweis auf neue Nachweis-Welle
- Kein Katalog-Setup in der Prüfer-UI; Automatisierung ausschließlich über ADR-0016 (`…/automatisierung/ausfuehren`, Gate 7.4a)
- Demo mit automatisierbarem Seed: Gate 6.3c

### Foto-Nachweis (Gate 8.3b)

In der bestehenden Prüflauf-Seite (`/prueflaeufe/:id`) — **keine** neue Route:

- Upload nur bei `kann_nachweis_erfassen` (Backend-Read-Model)
- JPEG/PNG, Vorschau vor Upload, expliziter Multipart-Upload (`POST …/nachweise/foto`)
- Inline-Anzeige gespeicherter Foto-Nachweise (`GET …/nachweise/{id}/datei`)
- Backend bleibt Source of Truth (Client nur MIME-/Größen-Komfortprüfung)
- Bewusst **nicht**: HEIC, Foto-Delete, Galerie, PDF-Einbettung

### Katalog-Admin Bibliothek (Gate 8.2c1)

Design-Time-Verwaltung der Bibliothek:

| Route | Inhalt |
|-------|--------|
| `/katalog` | Hub mit Links zu Kommandos, Routinen, Vorlagen, Entwürfe |
| `/katalog/kommandos` | Externe Kommandos CRUD |
| `/katalog/routinen` | Routinen-Liste; Editor unter `/katalog/routinen/neu` bzw. `/:routineId` |
| `/katalog/vorlagen` | PrüfschrittVorlagen CRUD (`bezeichnung`, `beschreibung`) |

- Kennzeichnung „Katalog-Setup / Laborbetrieb“ ohne Auth (ADR-0001)
- Routinen: geordnete `kommando_ids`, Hoch/Runter — kein Drag-and-Drop
- Keine Kommandoausführung in diesem Bereich

### Entwurfseditor (Gate 8.2c2)

Design-Time-Editor für Produktdefinitions-Entwürfe — **kein** Prüflaufstart, keine Run-Time-Ausführung:

| Route | Inhalt |
|-------|--------|
| `/katalog/entwuerfe/neu` | Entwurf anlegen (leer), Entwurf per ID öffnen, zuletzt bearbeitete Entwürfe |
| `/katalog/entwuerfe/:produktdefinitionId` | Schritte, Sollvorgaben, Automatisierung, Veröffentlichung |

- Wiederaufnahme per Produktdefinitions-ID + optionale localStorage-Historie (nur Metadaten, kein Entwurfs-LIST)
- Schritt-PUT ändert keine Automatisierung; Zuweisung über separaten Bereich (`PUT …/automatisierung`)
- Wechsel Kommando ↔ Routine: ConfirmDialog → explizit entfernen, dann neu zuweisen
- Sollvorgaben: einfacher Key/Min/Max-Editor (Transport-Dict, keine Domain-Materialisierung)
- Publish erzeugt neue Version (`version_id`); Entwurf bleibt bearbeitbar
- Hoch/Runter-Reihenfolge — kein Drag-and-Drop

## Skripte

| Befehl | Zweck |
|--------|-------|
| `npm run dev` | Vite Dev-Server mit API-Proxy |
| `npm run build` | Produktions-Build |
| `npm run lint` | ESLint |
| `npm run test` | Vitest (Schemas, Adapter, Komponenten) |

## Architektur

- `src/adapters/api/` — einziger Backend-Zugang (fetch + Zod-Transportvalidierung)
- `src/forms/` — UI-Formularschemas (keine Domain-Regeln)
- `src/pages/` — Präsentation; delegiert an Adapter via TanStack Query
- `src/components/SchrittAutomatisierung.tsx` / `AutomatisierungErgebnis.tsx` — Gate 6.3b
- `src/components/FotoNachweisUpload.tsx` / `FotoNachweisAnzeige.tsx` / `SchrittNachweise.tsx` — Gate 8.3b
- Keine Fachlogik, keine Domain-Regeln im Frontend
