# PWE Web (Frontend)

Driving Adapter für die PWE-HTTP-API. Stack: [ADR-0009](../../docs/adr/0009-frontend-stack.md).

## Voraussetzungen

- Node.js 20+
- Backend-API lokal auf Port 8000

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

Öffnen: http://localhost:5173 — Health-Check gegen `GET /health`.

## Skripte

| Befehl | Zweck |
|--------|-------|
| `npm run dev` | Vite Dev-Server mit API-Proxy |
| `npm run build` | Produktions-Build |
| `npm run lint` | ESLint |
| `npm run test` | Vitest (Transport-Schemas) |

## Architektur

- `src/adapters/api/` — einziger Backend-Zugang (fetch + Zod-Transportvalidierung)
- Keine Fachlogik, keine Domain-Regeln im Frontend
