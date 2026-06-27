# ADR-0007: Beurteilung — Soll/Ist-Vergleich V1

## Status

Accepted

## Kontext

Domain Model §4.18: Beurteilung vergleicht Ist (Nachweise) mit Soll (materialisierte Sollvorgaben). Der Vertical Slice setzte Beurteilungen zunächst extern — das widerspricht der Fachdomäne.

## Entscheidung

Beurteilungen werden in V1 **ausschließlich** durch Domain-Logik aus Nachweisen und materialisierten Sollvorgaben abgeleitet:

- **`BeurteilungService`** in `domain/pruefausfuehrung/` führt den Vergleich durch
- **`Prueflauf.beurteilen_schritt(schritt_id, sollvorgaben)`** ist der einzige Weg zur Beurteilung
- Kein Application/UI-setzbares `BeurteilungErgebnis` ohne Nachweis-/Sollbezug

**V1-Umfang des Vergleichs:**

- Numerische Sollvorgaben `{ "feld": { "min": n, "max": m } }` gegen `NachweisArt.MESSWERT` mit gleichem Feld in `payload`
- Fehlender Messwert-Nachweis → `nicht_bestanden`
- Außerhalb min/max → `nicht_bestanden`
- Alle Regeln erfüllt → `bestanden`
- Leere Sollvorgaben: mindestens ein Nachweis vorhanden → `bestanden`, sonst `nicht_bestanden`

**Nicht in V1:** komplexe Regelausdrücke, `bestanden_mit_kommentar` durch Service (bleibt später), manuelle Override-Beurteilung.

Beurteilung darf **geändert** werden, solange der Prüflauf nicht abgeschlossen ist (Domain Model §4.18) — erneuter Aufruf von `beurteilen_schritt` ersetzt die Beurteilung.

## Konsequenzen

- Application lädt Sollvorgaben aus materialisierter Version, ruft Domain auf
- Tests prüfen fachliche Ableitung, nicht manuelles Setzen

## Alternativen

- Beurteilung manuell durch Prüfer in V1: verworfen — widerspricht Domain Model
- Vollständiger Regel-Engine: V2
