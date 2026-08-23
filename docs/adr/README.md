# Architecture Decision Records (ADR)

Langfristig relevante Architekturentscheidungen. Fachdomäne: `docs/domain-model.md`.

| ADR | Titel |
|-----|-------|
| [0001](0001-v1-scope-deferrals.md) | V1-Umfang und bewusste Zurückstellungen |
| [0002](0002-backend-stack.md) | Backend-Technologiestack |
| [0003](0003-routine-nachweis-wellen.md) | Routine-Wiederholung: Nachweis-Wellen |
| [0004](0004-protokollsnapshot-mindestinhalt.md) | ProtokollSnapshot Mindestinhalt V1 |
| [0005](0005-sollvorgaben-materialisierung.md) | Sollvorgaben: Materialisierung bei Veröffentlichung |
| [0006](0006-istbestueckung-abweichung.md) | Istbestückung: Abweichungen (minimal im Slice) |
| [0007](0007-beurteilung-sollvergleich-v1.md) | Beurteilung: Soll/Ist-Vergleich V1 |
| [0008](0008-prueflauf-abschluss-view.md) | PrueflaufAbschlussView — Protokoll-Integration |
| [0009](0009-frontend-stack.md) | Frontend-Technologiestack (Driving Adapter) |
| [0010](0010-prueflauf-abschluss-transaktion.md) | Atomische Persistierung beim Prüflauf-Abschluss |
| [0011](0011-api-postgresql-unit-of-work.md) | Request-scoped Unit of Work für API ↔ PostgreSQL |
| [0012](0012-katalog-bibliothek-externes-kommando.md) | Bibliotheks-Modul im Katalog (ExternesKommando, Facade) |
| [0013](0013-com-adapter-wiring-fehlerabbildung.md) | COM-Adapter-Wiring, PySerialTransport, Fehlerabbildung |
| [0014](0014-routine-katalog-materialisierung.md) | Routine — Katalogmodell und einheitliche Materialisierung (Variante D) |
| [0015](0015-routine-ausfuehren-application-runner.md) | RoutineAusfuehren — Application Runner (Gate 7.3e) |
| [0016](0016-automatisierung-http-api.md) | Automatisierung am ProzedurSchritt — HTTP-API (Gate 7.3f) |
| [0017](0017-katalog-setup-http-automatisierung.md) | Katalog-Setup-HTTP für Automatisierung (Gate 6.3a) |
| [0018](0018-legacy-automatisierung-exit.md) | Legacy-Automatisierung Exit — API Exit (7.4a) / Write Exit (7.4b) |
| [0019](0019-bibliothek-http-crud.md) | Bibliothek-HTTP CRUD — Kommandos, Routinen, Automatisierung (Gate 8.2a) |
| [0020](0020-pruefschritt-vorlage-materialisierung.md) | PrüfschrittVorlage — Bibliothek und Materialisierung (Gate 8.2b1) |
| [0021](0021-entwurfsbearbeitung-http.md) | Erweiterte Entwurfsbearbeitung HTTP (Gate 8.2b2) |
| [0022](0022-foto-nachweis-dateispeicher.md) | Foto-Nachweis und DateiSpeicherPort (Gate 8.3a) |
| [0023](0023-identity-bounded-context.md) | Identity Bounded Context (Gate 8.1) |
| [0024](0024-authentication-v1.md) | Authentication V1 — Session-Cookie (Gate 8.1) |
| [0025](0025-authorization.md) | Authorization — Rollen, Profile, Einweisung (Gate 8.1) |
| [0026](0026-qualification-model.md) | Qualification Model (Gate 8.1) |
| [0027](0027-authenticated-pruefer-id.md) | Authentifizierter Benutzer statt freier pruefer_id (Gate 8.1) |
