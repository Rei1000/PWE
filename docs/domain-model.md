# Domänenmodell – PWE

Dieses Dokument beschreibt die **Fachdomäne** der Prüf-Workflow-Engine (PWE).

Es ist unabhängig von Programmiersprache, Datenbank, API oder technischer Architektur verständlich.

Project DNA und Einstieg: `.goldstandard/context.txt`. Anforderungen: `docs/pflichtenheft.md`.

---

## 1. Ziel der Domäne

PWE modelliert **konfigurierbare Endprüfungen** als durchgängigen Qualitätsprozess.

Die Domäne beantwortet folgende Fragen:

- **Wie** darf ein Produkt geprüft werden? (Design Time)
- **Wie** wird ein konkretes Prüfobjekt geprüft? (Run Time)
- **Was** ist der unveränderliche Nachweis einer abgeschlossenen Prüfung? (Post-Run Time)

PWE ist **keine** Ergometer-Software und **keine** Fertigungssteuerung. Die Ergometer-Endprüfung ist die erste Anwendung der Engine. Begriffe wie Artikelnummer, Platine oder COM-Kommando beschreiben **Konfiguration der ersten Anwendung**, nicht invariante Engine-Konzepte.

PWE beginnt fachlich beim **Qualitätsprozess**. Produktionsprozesse (Kundenauftrag, Produktlaufkarte) liefern Eingangsinformationen, gehören aber nicht zum Kern der Domäne.

---

## 2. Fachliche Grundprinzipien

| Prinzip | Bedeutung |
|---------|-----------|
| **Engine First** | Der Kern ist generisch. Spezialisierung erfolgt durch Konfiguration, nicht durch gerätespezifische Fachlogik. |
| **Vollständige Produktdefinition** | Der Administrator pflegt immer eine **vollständige** Beschreibung, wie ein Produkt geprüft werden soll — nicht lose Einzelobjekte ohne Gesamtkontext. |
| **Veröffentlichte Vorgabe** | Neue Prüfläufe starten ausschließlich gegen eine **freigegebene, unveränderliche** ProduktdefinitionsVersion. |
| **Trennung Soll / Ist / Beurteilung** | Sollvorgaben gehören zur Produktdefinition. Routinen beschaffen Ist-Werte. Die Beurteilung vergleicht beides. |
| **Trennung Option / Routine** | Optionen beschreiben **Ausstattung**. Routinen beschreiben **Prüf- oder Automatisierungsvorgehen**. |
| **Nachweis statt Annahme** | Jede relevante Feststellung wird durch einen **Nachweis** dokumentiert. |
| **Audit** | Automatisch erzeugte Nachweise sind unveränderlich; Ergänzungen erfolgen als **neue** Nachweise mit Bezug. |
| **Historie** | Abgeschlossene Prüfläufe und Protokolle sind unveränderlich — auch wenn die Vorgabe später geändert wurde. |
| **Ungültigkeit dokumentieren** | Ungültige Prüfläufe werden gespeichert und können ein Protokoll erzeugen. |

---

## 3. Ubiquitous Language

### Engine-Begriffe (domänenweit)

| Begriff | Bedeutung |
|---------|-----------|
| **Prüf-Workflow-Engine** | PWE als konfigurierbare Plattform für Endprüfungen |
| **Prüfobjekt** | Das konkret zu prüfende Exemplar (physisches Gerät) |
| **Prüfobjekt-Kennung** | Eindeutige Identifikation des Prüfobjekts |
| **Produktkodierung** | Externes Kodierungssystem zur Auflösung einer Produktdefinition (z. B. Artikelnummer) |
| **Basisprodukt** | Produktfamilie mit Standardinformationen |
| **Option** | Ausstattungsmerkmal eines Produkts (nicht gleichbedeutend mit Prüfschritten) |
| **Kundenprofil** | Wiederverwendbarer Kundensatz: Sprache, Firmwarevorgaben, Sollvorgaben, kundenabhängige Prüfregeln |
| **Produktdefinition** | Vollständige Beschreibung, wie ein Produkt geprüft werden soll (Entwurf, änderbar) |
| **ProduktdefinitionsVersion** | Veröffentlichte, unveränderliche Prüfvorgabe |
| **Prüfprozedur** | Geordnete Folge von ProzedurSchritten |
| **ProzedurSchritt** | Konkrete Verwendung einer PrüfschrittVorlage in einer Prozedur |
| **PrüfschrittVorlage** | Wiederverwendbare Schrittdefinition (Bibliothek) |
| **Routine** | Automatisierbare Aktionsfolge |
| **Externes Kommando** | Konfigurierbares Kommando an ein externes System |
| **Sollvorgabe** | Erwarteter Wert, Bereich oder Regel |
| **Sollbestückung** | Erwartete Komponenten eines Produkts |
| **Aktivierungsregel** | Bedingung, unter der ein ProzedurSchritt relevant ist |
| **Prüflauf** | Laufzeitinstanz einer Prüfung |
| **PrüfschrittDurchführung** | Ausführung eines ProzedurSchritts innerhalb eines Prüflaufs |
| **Nachweis** | Dokumentation, dass etwas beobachtet, erfasst oder ausgeführt wurde |
| **Beurteilung** | Fachliche Bewertung eines Prüfschritts (bestanden / nicht bestanden / mit Kommentar) |
| **ProtokollSnapshot** | Unveränderlicher Abschlussnachweis eines Prüflaufs |

### Erste Anwendung (Ergometer) — Konfigurationsinstanzen

| Engine-Begriff | Erste Anwendung |
|----------------|-----------------|
| Produktkodierung | Artikelnummer |
| Basisprodukt | Grundmodell (erste sechs Stellen) |
| Kundenprofil | OEM-Schlüssel (Oxx) oder Default-Profil |
| Prüfobjekt | Ergometer |
| Prüfobjekt-Kennung | Geräteseriennummer |
| Komponente | Platine (Mainboard, BD-Platine, …) |
| Externes Kommando | COM-Kommando |
| Externe Eingangsinformation | Produktlaufkarte |

### Abgrenzungen

- **Prüfung** = Vorgang; **Prüflauf** = persistierte Instanz mit Zustand und Ergebnissen.
- **PrüfschrittVorlage** = Definition; **ProzedurSchritt** = Verwendung in Prozedur; **PrüfschrittDurchführung** = Laufzeit.
- **Nachweis** = Evidenz; **Beurteilung** = Urteil über Evidenz im Kontext der Sollvorgaben.
- **ProtokollSnapshot** = Gesamtnachweis des Laufabschlusses; **Nachweis** = Beleg auf Schrittebene.

---

## 4. Zentrale Domänenobjekte

### 4.1 Basisprodukt

| | |
|---|---|
| **Zweck** | Beschreibt eine Produktfamilie unabhängig von Kunde und Optionen. |
| **Verantwortung** | Standard-Sollvorgaben, Standard-Komponenten, typische Prozedur-Basis. |
| **Lebenszyklus** | Wird vom Administrator angelegt und gepflegt; änderbar im Entwurf. |
| **Beziehungen** | Wird von Produktdefinitionen referenziert; fließt in veröffentlichte Versionen ein. |
| **Invarianten** | Gehört zur Katalog-Domäne; Änderungen am Basisprodukt erfordern Neuerstellung/Veröffentlichung betroffener Produktdefinitionen. |

---

### 4.2 Option

| | |
|---|---|
| **Zweck** | Beschreibt ein Ausstattungsmerkmal (z. B. Blutdruck, WLAN). |
| **Verantwortung** | Kennzeichnet **was** am Produkt vorhanden ist — nicht **wie** es geprüft wird. |
| **Lebenszyklus** | Katalogobjekt; wiederverwendbar über Produktdefinitionen. |
| **Beziehungen** | Produktdefinition wählt Optionen; Aktivierungsregeln können Optionen referenzieren. |
| **Invarianten** | Option allein definiert keine Prüfschritte. |

---

### 4.3 Kundenprofil

| | |
|---|---|
| **Zweck** | Bündelt kundenspezifische Vorgaben und Regeln. |
| **Verantwortung** | Sprache, Firmwarevorgaben, Sollvorgaben, Konfiguration, kundenabhängige Prüfregeln. |
| **Lebenszyklus** | Wiederverwendbares Katalogobjekt; mehrere Produktdefinitionen dürfen dasselbe Profil nutzen. |
| **Beziehungen** | Produktdefinition referenziert ein Kundenprofil; bei Veröffentlichung materialisiert in der Version. |
| **Invarianten** | Fehlt ein OEM-Schlüssel (Oxx) in der Produktkodierung, gilt das Default-Kundenprofil. |

---

### 4.4 Produktdefinition (Entwurf)

| | |
|---|---|
| **Zweck** | Arbeitsfähige, vollständige Beschreibung der Prüfvorgabe für ein Produkt — noch nicht für neue Prüfläufe freigegeben. |
| **Verantwortung** | Zusammensetzung aus Basisprodukt, Optionen, Kundenprofil, Sollbestückung, Sollvorgaben, Firmwarevorgaben, Prüfprozedur, Aktivierungsregeln. |
| **Lebenszyklus** | **Entwurf** — änderbar, bis der Administrator veröffentlicht. |
| **Beziehungen** | Wird über Produktkodierung aufgelöst; hat null oder mehr ProduktdefinitionsVersionen; genau eine **aktive** Version für neue Läufe. |
| **Invarianten** | Administrator arbeitet fachlich immer an der **vollständigen** Produktdefinition — nicht an isolierten Fragmenten ohne Gesamtkontext. |

---

### 4.5 ProduktdefinitionsVersion

| | |
|---|---|
| **Zweck** | Freigegebene, unveränderliche Prüfvorgabe für ein Produkt. |
| **Verantwortung** | Vollständige materialisierte Prüfvorgabe zum Veröffentlichungszeitpunkt. |
| **Lebenszyklus** | Entsteht beim **Veröffentlichen**; danach **unveränderlich**; kann deaktiviert, aber nicht gelöscht werden, solange Prüfläufe referenzieren. |
| **Beziehungen** | Wird von Prüfläufen referenziert; enthält materialisierte Prozedur, Sollvorgaben, Sollbestückung, Aktivierungsregeln u. a. |
| **Invarianten** | Pro Produktdefinition existiert für neue Prüfläufe **genau eine aktive** Version (V1). Referenzen auf Bibliotheksobjekte dürfen zusätzlich dokumentiert werden; Audit hat Vorrang vor maximaler Wiederverwendung. |

---

### 4.6 Produktkodierung

| | |
|---|---|
| **Zweck** | Externes Schlüsselsystem zur Identifikation und Auflösung einer Produktdefinition. |
| **Verantwortung** | Kodierung interpretieren → passende Produktdefinition / aktive Version finden. |
| **Lebenszyklus** | Konfiguriert; Regeln zur Interpretation sind Teil der ersten Anwendung. |
| **Beziehungen** | Führt zu Produktdefinition; ist **kein** Domänenkernobjekt auf Augenhöhe mit Prüflauf. |
| **Invarianten** | Kodierung ist nicht dasselbe wie Produktdefinition. |

---

### 4.7 Prüfprozedur

| | |
|---|---|
| **Zweck** | Definiert den geordneten Prüfablauf als Folge von ProzedurSchritten. |
| **Verantwortung** | Struktur und Reihenfolge der Prüfung. |
| **Lebenszyklus** | Im Entwurf änderbar; in veröffentlichter Version materialisiert und eingefroren. |
| **Beziehungen** | Gehört zur Produktdefinition; enthält ProzedurSchritte; referenziert PrüfschrittVorlagen. |
| **Invarianten** | Pro ProduktdefinitionsVersion ist genau eine materialisierte Prozedur maßgeblich. |

---

### 4.8 ProzedurSchritt

| | |
|---|---|
| **Zweck** | Konkrete Verwendung einer PrüfschrittVorlage innerhalb einer Prozedur. |
| **Verantwortung** | Reihenfolge, Pflichtstatus, Aktivierungsregel, optionale Routine, schrittspezifische Konfiguration. |
| **Lebenszyklus** | Teil der Prozedur im Entwurf; materialisiert in der Version. |
| **Beziehungen** | Referenziert PrüfschrittVorlage; kann Routine referenzieren; wird zur Laufzeit als PrüfschrittDurchführung instanziiert. |
| **Invarianten** | Dieselbe Vorlage kann in einer Prozedur mehrfach vorkommen — ProzedurSchritte sind eigenständig identifizierbar. |

---

### 4.9 PrüfschrittVorlage

| | |
|---|---|
| **Zweck** | Wiederverwendbare Schrittdefinition in der globalen Bibliothek. |
| **Verantwortung** | Beschreibung, Eingabefelder, Hinweise, Warn- und Sicherheitshinweise, Arbeitsanweisungs-Referenz. |
| **Lebenszyklus** | Katalogobjekt; im Entwurf pflegbar; in Version materialisiert. |
| **Beziehungen** | Wird von ProzedurSchritten referenziert; kann optional Routine vorschlagen. |
| **Invarianten** | Vorlage allein hat keine Reihenfolge oder Pflichtstatus — das leistet der ProzedurSchritt. |

---

### 4.10 Routine

| | |
|---|---|
| **Zweck** | Beschreibt, **wie** etwas automatisiert geprüft oder ausgeführt wird. |
| **Verantwortung** | Geordnete Aktionsfolge (externes Kommando, warten, Messwert, Sollvergleich, Bestätigung, Foto, …). |
| **Lebenszyklus** | Katalogobjekt; im Entwurf pflegbar; in Version materialisiert. |
| **Beziehungen** | Wird von ProzedurSchritt referenziert; nutzt Externe Kommandos. |
| **Invarianten** | Unabhängig von Optionen; kann kundenspezifisch konfiguriert sein; erzeugt **Ist-Werte**, keine Sollvorgaben. |

---

### 4.11 Externes Kommando

| | |
|---|---|
| **Zweck** | Konfigurierbare Definition eines Kommandos an ein externes System. |
| **Verantwortung** | Kann Werte lesen oder setzen; liefert eine Rohantwort. |
| **Lebenszyklus** | Zentral im Katalog verwaltet; in Version materialisiert. |
| **Beziehungen** | Wird in Routinen verwendet; technische Übertragung (z. B. COM) ist **nicht** Domänenbestandteil. |
| **Invarianten** | Rohantwort wird grundsätzlich als Nachweis gespeichert. |

---

### 4.12 Sollvorgabe

| | |
|---|---|
| **Zweck** | Beschreibt, was erwartet wird (Wert, Bereich, Liste, Regel). |
| **Verantwortung** | Grundlage für Soll-Ist-Vergleich in der Beurteilung. |
| **Lebenszyklus** | Teil der Produktdefinition / Version; im Entwurf änderbar. |
| **Beziehungen** | Kann aus Basisprodukt, Kundenprofil und produktspezifischen Overrides zusammengesetzt sein; materialisiert in der Version. |
| **Invarianten** | Gehört **nicht** zur Routine; Gültigkeitsbereich kann produktweit, komponenten- oder schrittspezifisch sein. |

---

### 4.13 Sollbestückung

| | |
|---|---|
| **Zweck** | Beschreibt, welche Komponenten am Produkt erwartet werden. |
| **Verantwortung** | Erwartungsliste (z. B. Mainboard, Display, BD-Platine, Bremse). |
| **Lebenszyklus** | Teil der Produktdefinition / Version. |
| **Beziehungen** | Prüflauf stellt **Istbestückung** fest und vergleicht mit Sollbestückung. |
| **Invarianten** | Komponentenwechsel werden dokumentiert; neue Seriennummern müssen erfasst werden. |

---

### 4.14 Aktivierungsregel

| | |
|---|---|
| **Zweck** | Steuert, ob ein ProzedurSchritt für ein konkretes Produkt relevant ist. |
| **Verantwortung** | Bedingte Aktivierung (z. B. „nur wenn Option Blutdruck vorhanden"). |
| **Lebenszyklus** | Am ProzedurSchritt definiert; materialisiert in der Version. |
| **Beziehungen** | Referenziert Optionen oder andere Merkmale der Produktdefinition. |
| **Invarianten** | Inaktive Schritte dürfen den Gesamtstatus nicht verfälschen; Überspringen nur gemäß Konfiguration und mit Dokumentation. |

---

### 4.15 Prüflauf

| | |
|---|---|
| **Zweck** | Laufzeitinstanz einer konkreten Prüfung an einem Prüfobjekt. |
| **Verantwortung** | Führt Prüfung durch, sammelt Nachweise, wendet Beurteilungen an, bestimmt Gesamtstatus. |
| **Lebenszyklus** | Gestartet → ggf. unterbrochen/fortgesetzt → abgeschlossen (gültig oder ungültig). |
| **Beziehungen** | Referenziert **genau eine** ProduktdefinitionsVersion (unveränderlich); enthält PrüfschrittDurchführungen; erzeugt ProtokollSnapshot. |
| **Invarianten** | Versionsreferenz darf sich **niemals** ändern; Wiederholungsprüfung nutzt standardmäßig die **aktuell freigegebene** Version; vorherige Läufe bleiben nachvollziehbar. |

---

### 4.16 PrüfschrittDurchführung

| | |
|---|---|
| **Zweck** | Dokumentiert die Ausführung eines ProzedurSchritts innerhalb eines Prüflaufs. |
| **Verantwortung** | Sammelt Nachweise; trägt Beurteilung; bildet Pflichtschritt-Status ab. |
| **Lebenszyklus** | Entsteht beim Bearbeiten des Schritts; kann bei Routine-Wiederholung nach Nachbesserung weitere Nachweise akkumulieren. |
| **Beziehungen** | Gehört zu Prüflauf; bezieht sich auf materialisierten ProzedurSchritt; enthält Nachweise. |
| **Invarianten** | Beurteilung bewertet Nachweise im Kontext der materialisierten Sollvorgaben. |

---

### 4.17 Nachweis

| | |
|---|---|
| **Zweck** | Beleg, dass etwas beobachtet, erfasst oder ausgeführt wurde. |
| **Verantwortung** | Audit-fähige Dokumentation auf Schrittebene. |
| **Lebenszyklus** | Wird erzeugt; automatische Nachweise sind unveränderlich; Ergänzungen als **neuer** Nachweis mit Bezug. |
| **Beziehungen** | Gehört zu PrüfschrittDurchführung. |
| **Invarianten** | Arten u. a.: Messwert, Foto, Kommentar, manuelle Eingabe, Rohantwort, extrahierter Wert, Komponentenerfassung. |

**Arten (Auszug):**

| Art | Beschreibung |
|-----|--------------|
| Messwert | Erfasster numerischer oder typisierter Wert |
| Foto | Bilddokumentation |
| Kommentar | Textuelle Erläuterung |
| Manuelle Eingabe | Prüfer-Eingabe aus definiertem Feld |
| Rohantwort | Unveränderliche Antwort eines externen Kommandos |
| Extrahierter Wert | Aus Rohantwort abgeleiteter Wert |
| Ergänzung | Ergänzender Nachweis zu einem automatischen Nachweis |
| Komponentenerfassung | Erfasste Ist-Komponente inkl. Seriennummer |

---

### 4.18 Beurteilung

| | |
|---|---|
| **Zweck** | Fachliche Bewertung eines Prüfschritts. |
| **Verantwortung** | Vergleicht Ist (Nachweise) mit Soll (materialisierte Sollvorgaben). |
| **Lebenszyklus** | Wird beim Abschluss des Schritts festgelegt; nachträgliche Änderung nur solange Prüflauf nicht abgeschlossen. |
| **Beziehungen** | Gehört zur PrüfschrittDurchführung. |
| **Invarianten** | Werte: bestanden, nicht bestanden, bestanden mit Kommentar; nicht bestandene Pflichtschritte können den gesamten Prüflauf ungültig machen. |

---

### 4.19 ProtokollSnapshot

| | |
|---|---|
| **Zweck** | Unveränderlicher Gesamtnachweis eines abgeschlossenen Prüflaufs. |
| **Verantwortung** | Archiviert Ergebnis, Nachweise, Versionbezug und Anzeigeinformationen. |
| **Lebenszyklus** | Entsteht beim Abschluss; danach unveränderlich. |
| **Beziehungen** | Gehört zu Prüflauf; referenziert ProduktdefinitionsVersion. |
| **Invarianten** | Wird auch für **ungültige** Prüfläufe erzeugt; ersetzt nicht Einzelnachweise, sondern bündelt den Abschluss. |

---

### 4.20 Benutzer und Prüferpräferenz

| | |
|---|---|
| **Zweck** | Identität und Berechtigung; persönliche Schrittreihenfolge. |
| **Verantwortung** | Rollen Admin/User; individuelle UI-Reihenfolge ohne Änderung der Prozedur. |
| **Lebenszyklus** | Persistent; unabhängig von Prüfläufen. |
| **Beziehungen** | Prüflauf dokumentiert Prüfer; Präferenz beeinflusst Darstellung, nicht Sollvorgaben. |
| **Invarianten** | Nur Admins verwalten Katalog und Produktdefinitionen. |

---

### 4.21 Produktlaufkarte (extern)

| | |
|---|---|
| **Zweck** | Eingangsinformation aus der Produktion. |
| **Verantwortung** | Begleitet physisches Gerät; kann beim Prüfstart erfasst werden. |
| **Lebenszyklus** | Extern; PWE speichert Referenz oder Kennung. |
| **Beziehungen** | Optionaler Bezug zum Prüflauf. |
| **Invarianten** | Gehört **nicht** zur Produktdefinition; Fertigungssteuerung ist außerhalb von PWE. |

---

## 5. Design Time

Objekte zur **Konfiguration** (Katalog):

| Objekt | Zustand |
|--------|---------|
| Basisprodukt | änderbar |
| Option | änderbar |
| Kundenprofil | änderbar |
| Produktdefinition | **Entwurf**, änderbar |
| Prüfprozedur (im Entwurf) | änderbar |
| ProzedurSchritt | änderbar |
| PrüfschrittVorlage | änderbar (Bibliothek) |
| Routine | änderbar (Bibliothek) |
| Externes Kommando | änderbar (Bibliothek) |
| Sollvorgabe, Sollbestückung, Aktivierungsregel | Teil des Entwurfs |
| Produktkodierung | konfiguriert |

**Veröffentlichungsakt:** Entwurf → **ProduktdefinitionsVersion** (unveränderlich, ggf. als neue aktive Version).

---

## 6. Run Time

Objekte während einer **Prüfung**:

| Objekt | Entstehung |
|--------|------------|
| Prüflauf | Start (bindet ProduktdefinitionsVersion) |
| Prüfobjekt-Kennung | Eingabe beim Start |
| PrüfschrittDurchführung | Beim Bearbeiten aktiver ProzedurSchritte |
| Nachweis | Bei Eingabe, Routine, Kommando, Foto, … |
| Beurteilung | Beim Schrittabschluss |
| Istbestückung | Erfassung tatsächlicher Komponenten |
| Produktlaufkarte-Referenz | Optional beim Start |

Der Prüflauf arbeitet **ausschließlich** gegen die referenzierte ProduktdefinitionsVersion — nicht gegen den live Entwurf.

---

## 7. Post-Run Time

Dauerhaft erhaltene Objekte:

| Objekt | Merkmal |
|--------|---------|
| ProduktdefinitionsVersion | unveränderlich; referenzierbar |
| Prüflauf | unveränderlich nach Abschluss |
| Nachweise | unveränderlich (automatische; Ergänzungen separat) |
| ProtokollSnapshot | unveränderlich |
| Historie pro Prüfobjekt-Kennung | aus abgeschlossenen Prüfläufen |

Entwürfe und Bibliotheksobjekte können sich ändern — abgeschlossene Läufe bleiben davon unberührt.

---

## 8. Fachliche Invarianten

### Produktdefinition und Version

1. Eine Produktdefinition im Entwurf ist vollständig und beschreibt die gesamte Prüfvorgabe.
2. Neue Prüfläufe referenzieren **ausschließlich** eine veröffentlichte ProduktdefinitionsVersion.
3. Pro Produktdefinition gibt es für neue Läufe **genau eine aktive** Version (V1).
4. Veröffentlichte Versionen sind unveränderlich.
5. Ältere Versionen bleiben referenzierbar und dürfen deaktiviert, aber nicht gelöscht werden, solange Prüfläufe existieren.

### Prüflauf

6. Die Versionsreferenz eines Prüflaufs ändert sich **niemals**.
7. Abgeschlossene Prüfläufe sind unveränderlich.
8. Ungültige Prüfläufe dürfen gespeichert und protokolliert werden.
9. Wiederholungsprüfungen starten standardmäßig mit der **aktuell freigegebenen** Version.

### Schritte und Pflicht

10. Pflichtschritte müssen erfolgreich abgeschlossen sein, damit der Prüflauf gültig ist.
11. Nicht bestandene Pflichtschritte machen den gesamten Prüflauf ungültig.
12. Überspringen ist nur erlaubt, wenn konfiguriert und dokumentiert (Kommentar).
13. Aktivierungsregeln bestimmen, welche ProzedurSchritte relevant sind.

### Nachweis und Audit

14. Automatisch erzeugte Nachweise dürfen nicht verändert werden.
15. Ergänzungen erfolgen als neue Nachweise mit Bezug — nicht als Mutation.
16. Rohantworten externer Kommandos werden grundsätzlich gespeichert.

### Soll und Ist

17. Sollvorgaben gehören zur materialisierten ProduktdefinitionsVersion.
18. Routinen erzeugen Ist-Werte, keine Sollvorgaben.
19. Beurteilung vergleicht Ist mit Soll.

### Komponenten

20. Sollbestückung ist Teil der Version; Istbestückung Teil des Prüflaufs.
21. Bauteilwechsel werden dokumentiert; neue Seriennummern müssen erfasst werden.

---

## 9. Fachliche Lebenszyklen

### Produktdefinition

```
Anlegen (Entwurf) → Bearbeiten → Veröffentlichen → ProduktdefinitionsVersion (aktiv)
                      ↑                                    │
                      └──────── neuer Entwurf ←───────────┘ (neue Version bei erneutem Veröffentlichen)
Alte Versionen: deaktiviert, aber referenzierbar
```

### Prüflauf

```
Start (Version binden) → Schritte bearbeiten → ggf. unterbrechen → fortsetzen
        → abschließen → gültig ODER ungültig → ProtokollSnapshot
```

### PrüfschrittDurchführung

```
Aktiv (ProzedurSchritt erfüllt Aktivierungsregel) → Nachweise sammeln
        → ggf. Routine wiederholen (Nachbesserung) → Beurteilung → abgeschlossen
```

### Nachweis (automatisch)

```
Erzeugt → unveränderlich → optional Ergänzungs-Nachweis mit Bezug
```

---

## 10. Versionierung

### Grundsatz (V1)

- **Entwurf** = mutable Produktdefinition
- **Veröffentlichte Version** = immutable, vollständige materialisierte Prüfvorgabe
- Prüflauf referenziert Version — **keine** ad-hoc Kopie pro Lauf

### Veröffentlichungsakt

Beim Veröffentlichen wird die effektive Prüfvorgabe **materialisiert**:

- Basisprodukt, Optionen, Kundenprofil (aufgelöst)
- Sollvorgaben, Sollbestückung, Firmwarevorgaben
- Prüfprozedur inkl. ProzedurSchritte, Aktivierungsregeln
- Routinen und Externe Kommandos (Inhalt, nicht nur lose IDs)

Referenzen auf Bibliotheksobjekte dürfen **zusätzlich** dokumentiert werden.

### Wann entsteht eine neue Version?

Beim expliziten **Veröffentlichen** nach Änderung am Entwurf — unabhängig davon, ob Sollwert, Firmware, Schritt, Routine oder Reihenfolge geändert wurde.

### Wiederholungsprüfung

Standard: **aktuelle freigegebene Version**. Frühere Läufe dokumentieren ihre jeweilige Version.

---

## 11. Audit- und Nachweisprinzip

### Audit

- Jeder abgeschlossene Prüflauf ist **nachvollziehbar** gegen eine identifizierbare ProduktdefinitionsVersion.
- Nachweise sind die **primären Belege** auf Schrittebene.
- ProtokollSnapshot ist der **Gesamtbeleg** auf Laufebene.
- Ungültige Läufe sind Teil der Qualitätshistorie — kein Löschen aus dem Audit.

### Nachweisprinzip

| Regel | Beschreibung |
|-------|--------------|
| **Vollständigkeit** | Relevante Feststellungen werden dokumentiert, nicht still angenommen. |
| **Unveränderlichkeit** | Automatische Nachweise werden nicht überschrieben. |
| **Ergänzbarkeit** | Kommentare und Ergänzungen sind neue Nachweise mit Bezug. |
| **Rohdaten** | Externe Kommandos hinterlassen Rohantwort-Nachweise. |
| **Trennung** | Nachweis (Was wurde beobachtet?) ≠ Beurteilung (Ist es in Ordnung?) |

---

## 12. Offene fachliche Punkte

| Thema | Status |
|-------|--------|
| Parallele Bearbeitung (PC + Smartphone) | Synchronisationsmodell fachlich noch nicht final |
| Routine-Wiederholung nach Nachbesserung | Ein Durchführungsobjekt mit mehreren Nachweis-Wellen vs. explizite Versuche |
| Schrittspezifische Sollvorgaben | Gültigkeitsbereich in V1 materialisiert — Override-Kette Basisprodukt → Kundenprofil → Produktdefinition noch detaillieren |
| ProtokollSnapshot-Inhalt | Mindestumfang für Langzeitarchiv vs. reine Versionsreferenz |
| Prüfgegenstand außerhalb „Produkt" | Für spätere Domänen (Prüfstand, Industrie) ggf. übergeordneter Begriff neben Produktdefinition |
| Persönliche Schrittreihenfolge | Rein Darstellung oder fachlich relevant für Protokoll |
| Aktive Schritte bei geänderter Istbestückung | Verhalten wenn Komponente fehlt/zusätzlich vorhanden |

---

## Anhang: Fachliches Strukturbild

```
[Katalog — Design Time]
  Basisprodukt, Option, Kundenprofil
  Produktdefinition (Entwurf)
       │ Veröffentlichen
       ▼
  ProduktdefinitionsVersion (immutable, materialisiert)
       │ enthält u. a.
       ├── Sollvorgaben, Sollbestückung, Firmwarevorgaben
       └── Prüfprozedur → ProzedurSchritt → PrüfschrittVorlage / Routine / Aktivierungsregel

[Prüfausführung — Run Time]
  Prüflauf ──referenziert──► ProduktdefinitionsVersion
     └── PrüfschrittDurchführung
            ├── Nachweise (Messwert, Rohantwort, Foto, …)
            └── Beurteilung

[Protokoll — Post-Run Time]
  ProtokollSnapshot (auch bei ungültigem Lauf)
```
