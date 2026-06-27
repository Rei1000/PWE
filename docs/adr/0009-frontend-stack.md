# ADR-0009: Frontend-Technologiestack

## Status

Accepted

## Kontext

Gate 6 (Bedienbarkeit) beginnt mit dem Frontend als **Driving Adapter** gegen die bestehende HTTP-API. Vor Bootstrap muss der Stack verbindlich sein — analog zu [ADR-0002](0002-backend-stack.md) für das Backend.

Architekturprinzipien (unverändert):

- **Domain First** — Fachregeln ausschließlich im Backend (Domain/Application).
- **Engine First** — UI ist keine zweite Engine; keine Duplikation von Beurteilungs-, Versions- oder Protokoll-Logik.
- **Hexagonale Architektur** — Frontend kommuniziert **nur** über die API; kein direkter Zugriff auf Persistenz oder Adapter.

## Entscheidung

| Bereich | Wahl | Rolle im Adapter |
|---------|------|------------------|
| UI-Bibliothek | **React** | Komponenten für Prüferführung (mehrstufiger Flow) |
| Sprache | **TypeScript** | Typisierung an der API-Grenze |
| Build / Dev | **Vite** | SPA für PC-Arbeitsplatz ([ADR-0001](0001-v1-scope-deferrals.md): kein SSR nötig) |
| Styling | **Tailwind CSS** | Utility-first für funktionale Prüfer-UI |
| Komponenten | **shadcn/ui** | Formulare, Dialoge, Status — ohne eigenes Design-System |
| Navigation | **React Router** | Explizite Routen (Start → Prüflauf → Abschluss) |
| Server-State | **TanStack Query** | HTTP-Cache, Mutations, Fehler `{detail, code}` |
| Formulare | **React Hook Form** | Nachweise, Komponenten-Eingaben |
| Validierung (Transport) | **Zod** | **Nur** Request-/Form-Validierung — **keine** Domain-Regeln |
| Icons | **Lucide React** | Schrittstatus, Aktionen |

Code unter `frontend/web/` gemäß `docs/projectstructure.md`.

### Architektur-Grenzen (verbindlich)

| Erlaubt im Frontend | Verboten im Frontend |
|---------------------|----------------------|
| Darstellung, Navigation, Formular-UX | Beurteilungslogik, Soll/Ist-Vergleich |
| Persönliche Schrittreihenfolge (Darstellung, ADR-0001) | Versionsmaterialisierung, Protokoll-Invarianten |
| API-Client, DTO-Mapping, Zod für Transport | Duplizierte Fachregeln aus `domain/` |
| Optimistic UI, Lade-/Fehlerzustände | Direkte COM/DB/PDF-Aufrufe |

Zod-Schemas spiegeln API-DTOs — sie ersetzen **nicht** Domain-Validierung im Backend.

## Begründung (Passung zur Architektur)

1. **React + Router + Query** modellieren den Prüflauf als zustandsgetriebenen Server-State-Flow — passend zu „Frontend = Adapter“, nicht „Frontend = Engine“.
2. **TypeScript + Zod (Transport)** sichern den Contract zur API ab, ohne Pydantic/Domain in die UI zu ziehen.
3. **Vite SPA** genügt für V1 PC-only; geringere Komplexität als SSR-Frameworks.
4. **shadcn/ui + Tailwind** beschleunigen formslastige Prüferoberflächen ohne Marketing-UI-Overhead.

## Konsequenzen

- Neuer ADR-Eintrag in `docs/adr/README.md`.
- CI aktiviert Frontend-Lint sobald `frontend/web/package.json` existiert.
- Mittelfristig: OpenAPI-Types aus FastAPI (`/openapi.json`) — optional, reduziert DTO-Drift.
- Kein `frontend/mobile/` in Gate 6 (Smartphone V2+, ADR-0001).

## Alternativen

- **Next.js:** verworfen — SSR/SEO für interne Prüfer-App unnötig.
- **Vue / Svelte:** verworfen — kein fachlicher Vorteil; React-Stack explizit gewünscht.
- **Domain-Logik in Zod:** verworfen — widerspricht Domain First und projektrules.
