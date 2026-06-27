# ADR-0004: ProtokollSnapshot Mindestinhalt V1

## Status

Accepted

## Kontext

Domain Model §12: Mindestumfang des ProtokollSnapshot vs. reine Versionsreferenz unklar. Beeinflusst Protokoll-Aggregate und Langzeitarchiv.

## Entscheidung

ProtokollSnapshot V1 **materialisiert** folgende Mindestinformation (unveränderlich nach Erstellung):

| Inhalt | Begründung |
|--------|------------|
| Referenz `ProduktdefinitionsVersion` | Audit: gegen welche Vorgabe geprüft wurde |
| Referenz `Prüflauf` | Zuordnung |
| Prüfobjekt-Kennung, Produktkodierung | Identifikation (erste Anwendung: Seriennummer, Artikelnummer) |
| Prüfer, Start-/Abschlusszeitpunkt | Audit |
| Gesamtstatus (gültig/ungültig) | Qualitätshistorie |
| Pro Schritt: ProzedurSchritt-Referenz, Beurteilung, Pflicht-Flag | Nachvollziehbarkeit ohne erneutes JOIN über Version |
| Referenzen auf Nachweise (IDs), nicht Binärdaten | Fotos bleiben im Dateispeicher; Snapshot verweist |

**Nicht** in V1 in den Snapshot kopieren: vollständige Bilddaten, komplette Rohantworten (bleiben als Nachweise am Prüflauf).

PDF-Erzeugung liest Snapshot + Nachweise über Ports.

## Konsequenzen

- ProtokollSnapshot ist audit-fähig auch wenn Katalog-Version später noch existiert
- Speicher: Snapshot bleibt schlank; Medien extern

## Alternativen

- Nur Versionsreferenz: verworfen — unzureichend für Langzeitarchiv/Audit
- Vollständige Denormalisierung aller Nachweis-Payloads: verworfen — Duplikation, Medien-Problem
