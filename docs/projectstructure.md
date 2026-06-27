# Projektstruktur – PWE (Initial)

Ordnerstruktur orientiert sich an **`docs/architecture.md`**; Fachbegriffe gemäß **`docs/domain-model.md`**.

---

## 1. Zielbild

Die Projektstruktur bildet die Bounded Contexts ab und trennt Domain, Application, Ports, Adapter und API. In dieser Phase: Struktur und Platzhalter — keine Fachlogik.

**Leitgedanke:** Ordner benennen **Engine-Fachbereiche** (Katalog, Prüfausführung, …), nicht technische Integrationen oder die erste Anwendung (Ergometer).

---

## 2. Ableitung aus Architektur und Domain Model

| Bounded Context | Phase | Domain | Application |
|-----------------|-------|--------|-------------|
| **Katalog** | Design Time | `domain/katalog/` | `application/katalog/` |
| **Prüfausführung** | Run Time | `domain/pruefausfuehrung/` | `application/pruefausfuehrung/` |
| **Protokoll** | Post-Run Time | `domain/protokoll/` | `application/protokoll/` |
| **Identity** | Querschnitt | `domain/identity/` | `application/identity/` |
| **Auswertung** | Read Model | — | `application/auswertung/` |

Fachliche Objekte im Katalog (Orientierung): Produktdefinition, ProduktdefinitionsVersion, Basisprodukt, Option, Kundenprofil, Prüfprozedur, ProzedurSchritt, PrüfschrittVorlage, Routine, Externes Kommando.

Fachliche Objekte in der Prüfausführung: Prüflauf, PrüfschrittDurchführung, Nachweis, Beurteilung.

---

## 3. Top-Level-Struktur

```text
PWE/
├── backend/
├── frontend/
├── infra/
├── docs/                 # domain-model.md, pflichtenheft, architecture, …
├── prompts/agent/
├── cli/
├── .goldstandard/
└── docker-compose.yml
```

---

## 4. Backend-Struktur

```text
backend/
├── src/
│   ├── domain/
│   │   ├── katalog/              # Produktdefinition, Version, Bibliothek
│   │   ├── pruefausfuehrung/     # Prüflauf, PrüfschrittDurchführung, Nachweis
│   │   ├── protokoll/            # ProtokollSnapshot
│   │   └── identity/
│   ├── application/
│   ├── ports/
│   ├── adapters/
│   │   ├── persistence/postgresql/
│   │   ├── com/
│   │   ├── pdf/
│   │   ├── print/
│   │   └── storage/
│   └── api/
└── tests/
```

---

## 5. Frontend-Struktur

```text
frontend/
├── web/
└── mobile/
```

---

## 6. Verantwortlichkeitstrennung

- `domain/katalog` — Konfigurations-Fachlogik; keine Protokoll- oder DB-Details.
- `domain/pruefausfuehrung` — Prüflauf, Nachweise, Beurteilungen; externe Kommandos nur über Ports.
- `adapters/com/` — technische Implementierung von `ExternesKommandoPort`.
- Ergometer-Begriffe nur in Konfigurationsdaten, nicht in Modulnamen.

---

## 7. Offene Strukturpunkte

- Interne Aufteilung von `domain/katalog/` bei wachsender Komplexität.
- Mobile-Technologie (responsive Web vs. native/hybrid).
