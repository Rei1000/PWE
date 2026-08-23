# ADR-0027: Authentifizierter Benutzer statt freier pruefer_id (Gate 8.1)

## Status

Angenommen (Gate 8.1 — Architektur)

## Kontext

Heute akzeptiert `POST /prueflaeufe` ein freies `pruefer_id` im Request-Body. Der Wert landet unverändert in Prüflauf, ProtokollSnapshot und PDF. Es gibt keinen Benutzerstamm und keine Garantie, dass die ID eine reale Person bezeichnet.

Authentifizierung: [ADR-0024](0024-authentication-v1.md). Identity: [ADR-0023](0023-identity-bounded-context.md).

## Entscheidung

### Neue Prüfläufe

- `pruefer_id` wird **ausschließlich** aus dem **authentifizierten Session-Benutzer** abgeleitet (`BenutzerId`).
- Ein vom Client geliefertes freies `pruefer_id` darf **nicht** mehr als vertrauenswürdige Quelle übernommen werden (keine Client-Impersonation).
- Der **Start-Request-Contract** wird entsprechend geändert (Feld entfernen oder serverseitig ignorieren und bei Sendung ablehnen — konkrete Variante im Implementierungs-Slice 8.1a; Architekturpflicht: **kein Trust in Client-`pruefer_id`**).

### Historische Daten

- Bestehende Prüfläufe und Snapshots mit freien Prüfer-Strings bleiben **unverändert lesbar**.
- **Keine** Massenmigration historischer Prüferstrings auf Benutzer-IDs.
- **Keine** harte Foreign-Key-Pflicht von historischen Prüfläufen auf die Benutzer-Tabelle.
- PDF und Snapshot bleiben historisch stabil (gespeicherter Wert wird weiter ausgegeben).

### Weitere Flächen

| Fläche | Verhalten |
|--------|-----------|
| Foto / Download | weiterhin prüflaufgebunden; zusätzlich AuthN (Rollen/Qualifikation gemäß Slice) |
| Demo-/Seed | müssen **später** echte Benutzer + Login nutzen (Anpassung mit 8.1a/Folgeslices) |

### Slice-Zuordnung

Binding `pruefer_id` ← Session: **Gate 8.1a**. Qualifikations-403 am Start: **Gate 8.1b**.

## Konsequenzen

- Breaking Change für API-Clients und Demo-Scripts beim Cutover von 8.1a.
- Read-Pfade für Altbestände benötigen keinen Identity-Lookup.
- Security: Impersonation über Body-`pruefer_id` entfällt.

## Alternativen

- `pruefer_id` weiter aus Body, nur „eingeloggt“-Check: verworfen (Impersonation).
- Historische Daten umschreiben: verworfen (unnötiges Migrationsrisiko, PDF/Snapshot-Stabilität).

## Adversarial (kurz)

- Client sendet fremde Benutzer-ID im Body: darf Start nicht steuern.
- Session eines Admins ohne Prüfer-Rolle: kein fachliches Prüfen ohne Qualifikation ([ADR-0025](0025-authorization.md), [ADR-0026](0026-qualification-model.md)).
