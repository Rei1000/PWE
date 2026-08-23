# Projektstruktur – PWE

Ordnerstruktur orientiert sich an **`docs/architecture.md`**; Fachbegriffe gemäß **`docs/domain-model.md`**.

**Stand:** Gate 8.2–8.4 ✅ (Katalog-Admin, Foto/Storage, Browser-PDF); Gate **8.1a** ✅; **8.1b** ✅; **8.1c1** Identity-Admin-Backend ✅; Gate 8.1c gesamt 🔄 (nächster Slice **8.1c2** UI). ADRs [0023](adr/0023-identity-bounded-context.md)–[0027](adr/0027-authenticated-pruefer-id.md). PostgreSQL-Schema ausschließlich via Alembic. Auswertung bleibt Platzhalter.

---

## 1. Zielbild

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

Fachliche Objekte in Identity (Orientierung, ADR-0023): Benutzer, Systemrollen, Berechtigungsprofil, Einweisungsnachweis, Identity-Audit-Eintrag; Profil↔Produktdefinition und Einweisung↔Version nur über IDs.

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
├── alembic.ini                   # Alembic (Gate 7.5) — einziger Schema-Pfad
├── alembic/                      # Migrationen; Runtime erzeugt kein Schema
│   └── versions/
├── src/
│   ├── domain/
│   │   ├── katalog/              # Produktdefinition, Version, Bibliothek
│   │   ├── pruefausfuehrung/     # Prüflauf, PrüfschrittDurchführung, Nachweis
│   │   ├── protokoll/            # ProtokollSnapshot
│   │   └── identity/             # Benutzer, Profile, Einweisungen, Audit (8.1a–8.1c1 ✅)
│   ├── application/
│   │   ├── katalog/
│   │   ├── pruefausfuehrung/
│   │   ├── protokoll/
│   │   ├── identity/             # Login (8.1a); Qualification (8.1b); Admin Backend (8.1c1)
│   │   └── auswertung/           # Platzhalter Gate 9
│   ├── ports/
│   ├── adapters/
│   │   ├── persistence/postgresql/
│   │   ├── com/
│   │   ├── pdf/
│   │   ├── print/
│   │   └── storage/
│   └── api/
│       ├── routes/
│       │   ├── identity_admin.py       # Benutzerverwaltung, Audit (8.1c1)
│       │   └── identity_qualification.py  # Profile, Einweisungen (8.1b/8.1c1)
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
- `domain/identity` — Benutzer, Rollen, Profile, Einweisungen, Identity-Audit; keine Katalog-Fachobjekte (nur IDs).
- `application/identity` — Login/Session (8.1a); Profil/Einweisung/Startregel (8.1b); Benutzerverwaltung, Passwort, Profil-Lifecycle, Audit (8.1c1).
- `adapters/com/` — technische Implementierung von `ExternesKommandoPort`.
- `adapters/storage/` — `DateiSpeicherPort`-Implementierungen (Gate 8.3a).
- Ergometer-Begriffe nur in Konfigurationsdaten, nicht in Modulnamen.

---

## 7. Offene Strukturpunkte

- Interne Aufteilung von `domain/katalog/` bei wachsender Komplexität.
- Mobile-Technologie (responsive Web vs. native/hybrid).
- Identity-Administrations-**UI** und Audit-Dashboard unter Gate **8.1c2** (Backend 8.1c1 ✅).
