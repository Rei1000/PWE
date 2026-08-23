# ADR-0024: Authentication V1 (Gate 8.1)

## Status

Angenommen (Gate 8.1 — Architektur)

## Kontext

Gate 8.1a benötigt Authentifizierung für die First-Party-PC-Web-App (Browser), betrieben typischerweise hinter Docker am Labor-/Arbeitsplatz ([ADR-0001](0001-v1-scope-deferrals.md)). Späterer Mehrbenutzerbetrieb und ggf. Mobile (Gate 9.2) dürfen die V1-Wahl nicht unnötig erschweren, müssen sie aber nicht vorwegnehmen.

Identity-Context: [ADR-0023](0023-identity-bounded-context.md).

## Entscheidung

### Mechanismus V1

**Serverseitige Session** mit Cookie:

| Eigenschaft | Festlegung |
|-------------|------------|
| Speicherung der Session | Server (Store hinter Port; konkrete Speicherform = Adapter) |
| Cookie | **HttpOnly**, **Secure**, **SameSite** (Strict oder Lax — Implementierung wählt konservativ passend zum Deployment) |
| JWT in V1 | **Nein** |
| Token in LocalStorage | **Nein** |
| Basic Auth als Primärverfahren | **Nein** |

**Begründung:** passt zu einer Sitzung am PC-Arbeitsplatz, klare Logout-/Sperr-Semantik, First-Party-Browser hinter Docker-Proxy, geringere XSS-Exposition als LocalStorage-Tokens. JWT Access/Refresh bleibt für spätere API-Clients/Mobile einer eigenen Entscheidung vorbehalten.

### Login / Logout

- **Login:** Benutzerkennung + Passwort; Session nur bei Status **Aktiv** ([ADR-0025](0025-authorization.md) / Benutzerstatus).
- **Logout:** Session serverseitig invalidieren und Cookie entfernen.
- Nach erfolgreichem Login: **neue Session-ID** (Schutz vor Session Fixation).

### Session-Invalidierung

Sessions werden invalidiert zumindest bei:

- Logout
- Wechsel in Status **Gesperrt** oder **Archiviert**
- Passwort-Änderung (durch Benutzer oder Administrator), soweit in dem Slice umgesetzt

### Statusprüfung

Jeder authentifizierte Request prüft: Session gültig **und** Benutzer weiterhin **Aktiv**. Andernfalls 401 und Session verwerfen.

### Passwort-Hashing

- Speicherung nur als Hash; nie Klartext.
- **Argon2id bevorzugt**; bcrypt nur falls Argon2id betrieblich nicht verfügbar (dann im Implementierungs-Slice begründet).
- Parameter (Zeit/Speicher/Parallelität) sind Konfiguration — nicht Gegenstand dieser ADR.

### Session-Lebensdauer

- **Idle-Timeout** und **absolute Max-Lifetime** sind vorgesehen und **konfigurierbar**.
- Konkrete Minuten/Stunden werden hier **nicht** festgeschrieben (keine fachliche Vorgabe zum Zeitpunkt dieser ADR).

### CSRF

Cookie-basierte Auth erfordert einen **CSRF-Schutz** für state-changing Browser-Requests (SameSite allein gilt nicht als vollständiger Ersatz in allen Deployment-Szenarien). Konkretes Verfahren (z. B. Double-Submit/CSRF-Token) ist Implementierungsdetail von Gate 8.1a — Architekturpflicht: **vorhanden und dokumentiert im Slice**.

## Nicht in dieser ADR

- OIDC/LDAP/MFA
- Refresh-Token-Rotation / JWT
- E-Mail-Passwort-Reset-Flows
- Exakte Timeout-Zahlen

## Konsequenzen

- API-Middleware liefert `AktuellerBenutzer` aus der Session ([ADR-0027](0027-authenticated-pruefer-id.md)).
- Frontend sendet Cookies mit (`credentials`); kein Bearer-JWT in V1.
- Gate 8.1a implementiert AuthN; Qualifikations-Enforcement folgt 8.1b ([ADR-0026](0026-qualification-model.md)).

## Alternativen

- JWT in LocalStorage: verworfen (XSS).
- Nur JWT ohne Server-Revocation: verworfen (Sperren/Logout unsicher).
- Basic Auth: verworfen (kein passendes SPA-/Logout-Modell).
