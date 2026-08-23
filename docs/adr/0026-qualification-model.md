# ADR-0026: Qualification Model (Gate 8.1)

## Status

Angenommen (Gate 8.1 — Architektur)

## Kontext

Fachliches Prüfen erfordert neben Systemrollen einen Nachweis der Einweisung auf die konkrete Prüfversion. Profile bündeln Produktlinien-Zugang. Identity besitzt die Zuordnungen ([ADR-0023](0023-identity-bounded-context.md)); Autorisierungs-Ebenen: [ADR-0025](0025-authorization.md).

## Entscheidung

### Bindungen

```
Berechtigungsprofil  ←n:m→  Produktdefinition          (Stamm, nicht Version)
Einweisungsnachweis  ────→  ProduktdefinitionsVersion  (veröffentlicht)
```

**Profil → Produktdefinition:** beschreibt, welche Produktlinien grundsätzlich erlaubt sind; bleibt über Releases stabil.

**Einweisung → ProduktdefinitionsVersion:** Version ist unveränderlich und Run-Time-Referenz des Prüflaufs; Audit und Re-Qualifikation erfordern Versionsbezug.

### Einweisungsnachweis (Mindestinhalt)

- Benutzer
- ProduktdefinitionsVersion (`version_id`)
- Eingewiesen durch
- Datum
- Optional: gültig bis
- Status
- Bemerkung

### Startregel

Ein Prüflauf darf nur gestartet werden, wenn **alle** gelten:

1. Benutzerstatus **Aktiv**
2. Rollenmenge enthält **Prüfer**
3. Mindestens ein Berechtigungsprofil des Benutzers ist der **Produktdefinition** der Zielversion zugeordnet
4. Es existiert eine **gültige** Einweisung für genau diese **`version_id`** (nicht widerrufen, nicht abgelaufen)
5. Gestartet wird die **aktive veröffentlichte** Version zur Produktkodierung (bestehende Katalog-Regel)

Administrator-/QM-/Abteilungsleiter-Rechte ersetzen keine der Punkte 3–4.

### Gültigkeit und Widerruf

- Gültige Einweisung: Status gültig und optional `gültig bis` nicht überschritten.
- **Widerruf:** Status widerrufen → **neue Starts** mit dieser Version für den Benutzer sind blockiert.
- **Laufende Prüfläufe** werden bei nachträglichem Widerruf **nicht rückwirkend fachlich verändert** (kein Mid-Run-Kill der Domänendaten). Fortsetzen unterliegt weiterhin AuthN und „Benutzer = Prüflauf-`pruefer_id`“ (sobald enforced).

### Benutzerstatus

- **Gesperrt / Archiviert / Neu:** kein Login bzw. kein Prüfen ([ADR-0024](0024-authentication-v1.md), [ADR-0025](0025-authorization.md)).
- Sessions bei Sperre/Archivierung invalidieren.

### Publish und neue Version

| Regel | Festlegung |
|-------|------------|
| Default | **Keine** automatische Übernahme von Einweisungen auf die neue Version |
| Optional | QM/Admin-Flag **„Einweisung übernehmen“**: gültige Einweisungen der **Vorgängerversion** werden **auditierbar** als neue Nachweise auf die **neue** `version_id` übertragen |
| Historie | Einweisungen der alten Version bleiben für die alte Version bestehen; steuern nicht den Start der neuen aktiven Version |

### Slice-Zuordnung

Enforcement der Startregel und Publish-Übernahme: **Gate 8.1b** (Qualification Engine). Verwaltung UI: **8.1c**.

## Konsequenzen

- Katalog bleibt Owner von Publish; Identity führt Einweisungs-Persistenz und Übernahme-Orchestrierung in Application aus.
- Operative Last bei strengem Default ist beabsichtigt (QM entscheidet Übernahme bewusst).

## Alternativen

- Einweisung nur an Produktdefinition: verworfen — zu schwach für Versionsänderungen.
- Profil an Version: verworfen — Pflegeexplosion.
- Immer automatische Übernahme: verworfen — Sicherheits- und QM-Risiko.

## Adversarial (kurz)

- Start auf historischer Version trotz neuer aktiver Version: durch Regel „aktive Version“ verhindert.
- Admin startet ohne Einweisung: durch Startregel und [ADR-0025](0025-authorization.md) verboten.
- Stille Massen-Übernahme: Default aus; nur explizites Flag.
