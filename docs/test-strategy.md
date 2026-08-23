# Teststrategie — PWE

Operationalisierung von TDD (projektrules). Stack: ADR-0002.

## Schichten

| Schicht | Was testen | Werkzeug | Abhängigkeiten |
|---------|------------|----------|----------------|
| **Domain** | Aggregate-Invarianten, Wertobjekte | pytest, rein | keine |
| **Application** | Use-Case-Orchestrierung | pytest + In-Memory-Repos | Domain, Ports |
| **Adapter** | Mapping, SQL, COM-Simulation, PySerialTransport (Mock) | pytest | extern |
| **API** | HTTP-Contract | pytest + httpx | Application |
| **Frontend** | Transport-Schemas, API-Client, Automatisierungs-Mutation/UI | vitest, Testing Library | adapters/api, components |

## Regeln

- Domain-Tests **ohne** Datenbank, COM, Dateisystem.
- Ein **Vertical-Slice-Test** pro Kern-Use-Case in `tests/application/`.
- In-Memory-Repos in `adapters/persistence/in_memory.py` — nicht in Tests duplizieren.
- PostgreSQL-Adapter in `adapters/persistence/postgresql/` — Mapping-Tests ohne DB; Repository-Tests mit `DATABASE_URL` (CI: Postgres-Service).
- **Alembic** (Gate 7.5 ✅): Upgrade/Downgrade/Re-Upgrade; Runtime ohne Migration schlägt fehl — `tests/adapters/test_alembic_bootstrap.py`, Session-Migrate in `tests/conftest.py`, isolierte Schemas via `ALEMBIC_SCHEMA`.
- **OpenAPI-Contract-Tests** (Gate 7.3f / 7.4a): Zielendpoint ADR-0016; Legacy-Pfad abwesend — `tests/api/test_api_openapi_automatisierung.py`.
- **Write Exit** (Gate 7.4b): Publish ohne Legacy-Snapshot; Altbestände lesbar — `tests/application/test_write_exit_materialisierung.py`, PostgreSQL in `test_postgresql_routine_materialisierung.py`.
- **Monitoring-Baseline** (Gate 7.4c): fachliche Beobachtung `fehlgeschlagen` — `tests/api/test_automatisierung_beobachtung.py`.
- **Katalog-Setup-API-Tests** (Gate 6.3a): HTTP-E2E Setup + Automatisierung, OpenAPI — `tests/api/test_api_katalog_automatisierung_setup.py`, `test_api_openapi_katalog_automatisierung_setup.py`, PostgreSQL in `test_api_postgresql_katalog_automatisierung_setup.py`.
- **Frontend-Automatisierung** (Gate 6.3b): Zod-Response inkl. `fehlgeschlagen=true`, Adapter-Zielendpoint, Mutation `retry: false`, Komponenten — `frontend/web/tests/api/automatisierung.test.ts`, `tests/hooks/`, `tests/components/`.
- **Demo-Seed** (Gate 6.3c): `PWE_DEMO_MODE`-Wiring, HTTP-E2E Demo-Flow, Script-Client-Tests — `tests/api/test_demo_mode_wiring.py`, `test_api_demo_seed_e2e.py`, `tests/scripts/test_seed_demo_automatisierung.py`; PostgreSQL in `test_api_postgresql_demo_seed.py`.
- **Bibliothek-HTTP CRUD** (Gate 8.2a): Application `test_katalog_bibliothek_crud.py`; API `test_api_katalog_bibliothek_crud.py`; OpenAPI `test_api_openapi_katalog_bibliothek_crud.py`; PostgreSQL `test_api_postgresql_katalog_bibliothek_crud.py`; Contract-Tests erweitert in `test_bibliothek_repository_contract.py`.
- **PrüfschrittVorlage** (Gate 8.2b1): Domain `test_pruefschritt_vorlage.py`; Application `test_katalog_pruefschritt_vorlage_crud.py`; API `test_api_katalog_pruefschritt_vorlage_crud.py`; OpenAPI `test_api_openapi_katalog_pruefschritt_vorlage_crud.py`; PostgreSQL `test_api_postgresql_katalog_pruefschritt_vorlage_crud.py`; Routine-HTTP-E2E-Regression `test_api_katalog_routine_http_e2e.py`; Contract-Tests in `test_bibliothek_repository_contract.py`; Alembic `0002` in `test_alembic_bootstrap.py`.
- **Entwurfsbearbeitung HTTP** (Gate 8.2b2): Domain `test_produktdefinition_entwurf_bearbeitung.py`; Application `test_katalog_entwurf_bearbeitung.py`; API `test_api_katalog_entwurf_bearbeitung.py`; OpenAPI `test_api_openapi_katalog_entwurf_bearbeitung.py`; PostgreSQL `test_api_postgresql_katalog_entwurf_bearbeitung.py` — kein Alembic, kein Schema-Wechsel.
- **Katalog-Admin Bibliothek UI** (Gate 8.2c1): Frontend Adapter `tests/api/bibliothek.test.ts`, `client-put-delete.test.ts`, Flow `katalog-bibliothek-flow.test.ts`; Hooks `useKommandos.test.ts`; Komponenten/Pages — kein Backend-Diff.
- **Entwurfseditor UI** (Gate 8.2c2): Frontend Adapter `tests/api/entwurf.test.ts`, Flow `katalog-entwurf-flow.test.ts`; Hooks `useEntwurf.test.ts`; Lib `entwurf-editor.test.ts`, `entwurf-recents.test.ts`; Komponenten `sollvorgaben-editor.test.tsx`, `entwurf-automatisierung.test.tsx`; Pages `entwurf-neu.test.tsx` — kein Backend-Diff.
- **Foto-Nachweis / DateiSpeicher** (Gate 8.3a): Domain `test_datei_verweis.py`; Adapter `test_datei_speicher_contract.py`; Application `test_foto_nachweis_erfassen.py`, `test_nachweis_datei_lesen.py`; API `test_api_foto_nachweis.py`; NachweisArt-Contract erweitert (`foto_nur_per_multipart`); PostgreSQL in `test_api_foto_nachweis.py` — kein Alembic.
- **Frontend Foto-Upload/-Anzeige** (Gate 8.3b): Multipart-Adapter und Blob-Download `frontend/web/tests/api/foto-nachweis.test.ts`; Hook `tests/hooks/useFotoNachweisErfassen.test.ts`; Upload-/Anzeige-Komponenten, Fehlerfälle (MIME/413), Blob-Anzeige und integrativer Upload-Flow `tests/components/foto-nachweis.test.tsx`; Client-Komfortprüfung `tests/lib/foto-konstanten.test.ts`; Fehler-Mapping `tests/lib/prueflauf-errors.test.ts` — kein Backend-Diff; Vitest-Stand **105** Tests (28 Dateien).
- **Frontend Protokoll öffnen / Browserdruck** (Gate 8.4): Browser-PDF-Öffnen, Blob-Handling (`URL.createObjectURL` / `revokeObjectURL`), Download-Regression und Fehlerfälle beim PDF-Laden — Helper `frontend/web/tests/lib/protokoll-pdf-aktion.test.ts`, AbschlussPage `tests/pages/abschluss.test.tsx` — kein Backend-Diff; Vitest-Stand **110** Tests (30 Dateien).
- **Qualification Engine** (Gate 8.1b ✅): Domain Startregel / Profil / Einweisung; Application Profil- und Einweisungs-Verwaltung + Publish-Übernahme; API `/identity/profile*`, `/identity/einweisungen*`, Start-403 `qualifikation_unzureichend`, Ownership an Prüflauf-Mutationen; Alembic `0004`; Tests `test_qualification_application.py`, `test_qualification_api.py`, Support `tests/support/qualification.py`.
- **Identity Admin Backend** (Gate 8.1c1 ✅): Domain Benutzer-Lifecycle, Letzter-Admin, Profil aktiv, Identity-Audit; Application `benutzer_verwaltung`, `passwort_verwaltung`, `profil_verwaltung`; API `test_identity_admin_api.py` (Force-Change, Lesematrix, Session-Invalidierung, Profil-Deaktivierung); PostgreSQL Letzter-Admin-Concurrency `test_postgresql_letzter_admin_concurrency.py`; Profil-Hard-Delete gesperrt `test_profil_hard_delete_gesperrt.py`; Alembic `0005`.
- **Identity Admin UI** (Gate 8.1c2 ✅): Frontend Verwaltungs-UI, Force-Change, Rollenmatrix — `frontend/web/tests/pages/identity/`, `tests/hooks/useAuth.test.tsx`, `tests/pages/passwort-aendern.test.tsx`, `tests/components/app-layout-nav.test.tsx`; kein Backend-Diff.
- **Stand nach Merge PR #55:** Backend **483**, PostgreSQL-Marker **43** (0 Skips), Frontend **127** (40 Dateien).

## V1-Pflicht vor Merge

```bash
cd backend && pip install -e ".[dev]" && pytest
```

## Nicht in V1

- E2E-Browser-Tests
- Lasttests
- Vollständige COM-Hardware-Tests (Arbeitsplatz mit physischem Gerät)
- Automatischer Retry im COM-Transport
