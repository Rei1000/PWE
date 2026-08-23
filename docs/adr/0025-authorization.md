# ADR-0025: Authorization (Gate 8.1)

## Status

Angenommen (Gate 8.1 — Architektur)

## Kontext

Identity ([ADR-0023](0023-identity-bounded-context.md)) muss administrative Rechte von fachlicher Qualifikation trennen. Bisherige Dokumente kennen grob Admin/User; Gate 8.1 führt vier Systemrollen und drei Autorisierungs-Ebenen ein.

Authentifizierung: [ADR-0024](0024-authentication-v1.md). Qualifikation: [ADR-0026](0026-qualification-model.md).

## Entscheidung

### Drei Ebenen

| Ebene | Steuert |
|-------|---------|
| **1. Systemrolle** | Administrative Fähigkeiten (Katalog, Publish, Benutzer, Einweisen, …) |
| **2. Berechtigungsprofil** | Welche **Produktdefinitionen** (Stamm) grundsätzlich genutzt werden dürfen |
| **3. Einweisung** | Ob eine konkrete **ProduktdefinitionsVersion** geprüft werden darf |

**Rollen allein reichen nicht:** Sie erklären nicht Produktlinien-Zuschnitt und QM-Einweisungsnachweis.

**Administratorrechte ersetzen keine fachliche Qualifikation.** Wer prüft, braucht Rolle **Prüfer** plus Profil plus gültige Einweisung ([ADR-0026](0026-qualification-model.md)).

### Systemrollen und Mehrfachrollen

Rollen: **Administrator**, **QM**, **Abteilungsleiter**, **Prüfer**.

**Mehrfachrollen sind erlaubt.** Effektive administrative Rechte = **Vereinigung** der Rollen. Das Qualifikations-Gate bleibt **konjunktiv** (alle Startbedingungen).

### Benutzerstatus

Neu · Aktiv · Gesperrt · Archiviert — Archivieren statt Löschen. Login und fachliches Prüfen nur bei **Aktiv**.

### Rollenmatrix (V1)

| Fähigkeit | Admin | QM | Abt.-Leiter | Prüfer |
|-----------|:-----:|:--:|:-----------:|:------:|
| System / Benutzer verwalten (anlegen, Status, Rollen vergeben, Passwort setzen) | ✅ | ❌ | ❌ | ❌ |
| Berechtigungsprofile CRUD | ✅ | ✅ | ❌ | ❌ |
| Profil ↔ Produktdefinition zuordnen | ✅ | ✅ | ❌ | ❌ |
| Profile Mitarbeitern zuweisen | ✅ | ❌ | ✅ | ❌ |
| Einweisungen dokumentieren / widerrufen | ✅ | ❌ | ✅ | ❌ |
| Bibliothek CRUD | ✅ | ✅ | ✅ | ❌ |
| Entwurf anlegen / bearbeiten | ✅ | ✅ | ✅ | ❌ |
| Version veröffentlichen | ✅ | ✅ | ❌ | ❌ |
| Publish-Flag „Einweisung übernehmen“ | ✅ | ✅ | ❌ | ❌ |
| Run-Time: Start / Nachweise / Foto / Abschluss (Schreiben) | — | — | — | ✅* |
| Run-Time: Prüflauf / Protokoll / PDF / Foto lesen | ✅† | ✅† | ✅† | ✅† |

\*Schreiben und Start nur wenn Startregel erfüllt ([ADR-0026](0026-qualification-model.md)): Status Aktiv, Rolle **Prüfer**, passendes Profil, gültige Einweisung, aktive veröffentlichte Version. Mutationen am laufenden Prüflauf zusätzlich nur durch den Eigentümer (`pruefer_id`).

†**Read broadly:** jede aktive authentifizierte Session — **ohne** Ownership-, Profil- oder Einweisungsprüfung. Prüfergebnisse sind Qualitätsnachweise für den organisationsweiten Informationsfluss, keine personenbezogenen Geheimdaten. Feinere Leserechte (Werk, Mandant, …) bleiben später möglich.

**Admin, QM und Abteilungsleiter** können selbst prüfen, **wenn** sie zusätzlich die Rolle **Prüfer** sowie Profil und Einweisung besitzen. Ohne Prüfer-Rolle: kein fachliches Prüfen.

### Write narrowly / Read broadly (V1)

| Zugriff | Policy |
|---------|--------|
| **Start** | Qualifikation (AND) |
| **Schreiben** am Prüflauf | AuthN + Ownership (`aktueller Benutzer == pruefer_id`) |
| **Lesen** (Prüflauf, Protokoll, PDF, Foto-Download) | AuthN (Status Aktiv) — bewusst **ohne** Ownership |

### Verbindliche Regeln (Kurz)

- Admin verwaltet System und Benutzer.
- QM darf veröffentlichen (und Profile verwalten).
- Abteilungsleiter darf Entwürfe bearbeiten, **nicht** veröffentlichen.
- Abteilungsleiter und Admin dokumentieren Einweisungen.
- Prüfer führt Run-Time aus (unter Qualifikation).
- Nur die Prüfer-Rolle ermöglicht fachliches Prüfen (ggf. in Kombination mit anderen Rollen).

### Durchsetzung

| Schicht | Rolle |
|---------|--------|
| Domain / Application | verbindliche Policies und Use-Case-Gates |
| API | AuthN + Autorisierung — **Security Boundary** |
| Frontend | Menüs/Route-Guards nur **UX**, niemals alleinige Security Boundary |

### Slice-Zuordnung

| Slice | Autorisierung |
|-------|----------------|
| **8.1a** | Rollen am Benutzer; Middleware authentifiziert; grobe Guards möglich; volle Katalog-Matrix und Qualifikation noch nicht zwingend vollständig enforced |
| **8.1b** | Profil + Einweisung + Startregel enforced |
| **8.1c** | Verwaltungs-UI und Audit für Zuweisungen |

## Konsequenzen

- Policies und Tests müssen Mehrfachrollen abdecken.
- Katalog- und Prüflauf-APIs werden schrittweise geschützt (8.1a → 8.1b).

## Alternativen

- Nur zwei Rollen Admin/User: verworfen — QM/Abteilungsleiter und Qualifikation fehlen.
- Permission-Tabelle pro Endpoint als Domain-Modell: verworfen — Over-Engineering für V1.
