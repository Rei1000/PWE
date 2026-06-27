# Projektstruktur – PWE (Initial)

## 1. Zielbild

Die Projektstruktur bildet die Bounded Contexts aus `docs/architecture.md` ab und trennt Domain, Application, Ports, Adapter und API. In dieser Phase werden Struktur und Platzhalter angelegt; keine Fachlogik implementiert.

**Leitgedanke:** Ordner benennen **Engine-Fachbereiche** (Katalog, Prüfausführung, …), nicht technische Integrationen (COM, Gerät) und nicht die erste Anwendung (Ergometer).

Die verbindliche Begriffswelt ist in `docs/projektrules.md` dokumentiert.

Technologie-Orientierung (aus Projektkontext): Python-Backend, PostgreSQL, lokale PC-/Smartphone-Oberflächen.

---

## 2. Ableitung aus Architektur und Pflichtenheft

| Bounded Context | Phase | Domain | Application | Adapter |
|-----------------|-------|--------|-------------|---------|
| **Katalog** | Design Time | `domain/katalog/` | `application/katalog/` | `adapters/persistence/postgresql/` |
| **Prüfausführung** | Run Time | `domain/pruefausfuehrung/` | `application/pruefausfuehrung/` | — |
| **Protokoll** | Post-Run Time | `domain/protokoll/` | `application/protokoll/` | `adapters/pdf/`, `adapters/storage/` |
| **Identity** | Querschnitt | `domain/identity/` | `application/identity/` | `adapters/persistence/postgresql/` |
| **Auswertung** | Read Model | — | `application/auswertung/` | `adapters/persistence/postgresql/` |
| Externes Kommando | `ExternesKommandoPort` | — | — | `adapters/com/` (weitere: `can/`, `rest/`, `simulation/`, …) |
| Arbeitsplatz-Konfiguration | — | — | — | `infra/config/` |

---

## 3. Top-Level-Struktur

```text
PWE/
├── backend/              # Python-Kern (Domain, Application, Ports, Adapter, API)
├── frontend/             # PC- und Mobile-Oberflächen
├── infra/                # Docker, Deployment, DB-Migrationen, Arbeitsplatz-Config
├── docs/                 # Pflichtenheft, Architektur, Projektstruktur
├── prompts/agent/        # Agent-Workflow-Prompts
├── cli/                  # Hilfsskripte für Entwicklung und Betrieb
├── .goldstandard/        # Verbindlicher Projektkontext
└── docker-compose.yml    # Lokale Entwicklungsumgebung
```

---

## 4. Backend-Struktur

```text
backend/
├── src/
│   ├── domain/
│   │   ├── katalog/              # Produktvarianten, Prozeduren, Schrittvorlagen, Routinen
│   │   ├── pruefausfuehrung/     # Prüflauf, Schrittausführung, Routine-Orchestrierung
│   │   ├── protokoll/            # ProtokollSnapshot, Archiv-Invarianten
│   │   └── identity/             # Benutzer, Rollen, Schrittreihenfolge
│   ├── application/
│   │   ├── katalog/
│   │   ├── pruefausfuehrung/
│   │   ├── protokoll/
│   │   ├── identity/
│   │   └── auswertung/           # Dashboard, Statistiken (Read Models)
│   ├── ports/                    # Fachliche Verträge (Domänensprache)
│   ├── adapters/                 # Technische Implementierungen (Protokoll/Technologie)
│   │   ├── persistence/
│   │   │   └── postgresql/       # Repository-Implementierungen
│   │   ├── com/                  # ExternesKommandoPort (v1)
│   │   ├── pdf/                  # ProtokollErzeugungPort
│   │   ├── print/                # DruckPort
│   │   └── storage/              # DateiSpeicherPort
│   └── api/                      # HTTP/WebSocket, kein Fachwissen
└── tests/
    ├── domain/
    ├── application/
    └── adapters/
```

**Hinweis zu `domain/katalog/`:** Interne Unterteilung in `stammdaten/` und `konfiguration/` ist zulässig, wenn die Komplexität wächst. Bis dahin reicht eine flache Struktur unter `katalog/`.

---

## 5. Frontend-Struktur

```text
frontend/
├── web/                  # PC-Oberfläche (Prüfung, Verwaltung, Dashboard)
│   ├── src/
│   └── tests/
└── mobile/               # Smartphone-Oberfläche (QR-Kopplung, Scan, Foto)
    ├── src/
    └── tests/
```

---

## 6. Infrastruktur

```text
infra/
├── docker/               # Dockerfiles
├── db/                   # Migrationen, Seeds (Platzhalter)
└── config/               # Arbeitsplatz-Konfiguration (Schnittstellen, Drucker, Pfade)
```

---

## 7. Verantwortlichkeitstrennung

- `domain/katalog` enthält Konfigurations-Fachlogik, keine Protokoll- oder DB-Details.
- `domain/pruefausfuehrung` orchestriert Routinen fachlich; externe Kommandos nur über `ExternesKommandoPort`.
- `adapters/com/` implementiert den Port technisch — weitere Protokolle als sibling-Ordner (`can/`, `rest/`, `simulation/`).
- `ports/` spricht Domänensprache; `adapters/` benennt Technologien.
- `application` koordiniert Use Cases über Context-Grenzen hinweg.
- `frontend` repliziert keine serverseitigen Fachregeln.
- Ergometer-spezifische Begriffe erscheinen nur in Konfigurationsdaten und im Pflichtenheft, nicht in Modulnamen.

---

## 8. Offene Strukturpunkte

- Interne Aufteilung von `domain/katalog/` bei wachsender Komplexität.
- Mobile-Technologie (responsive Web vs. native/hybrid).
- Weitere Adapter neben `com/` (z. B. `can/`, `rest/`, `simulation/`) ohne Domain- oder Port-Änderung.
- Migrations-Tooling für PostgreSQL.
