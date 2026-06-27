# ADR-0003: Routine-Wiederholung — Nachweis-Wellen

## Status

Accepted

## Kontext

Domain Model §12: Nach Nachbesserung kann eine Routine wiederholt werden. Offen: ein `PrüfschrittDurchführung` mit mehreren Nachweis-Wellen vs. explizite Versuchs-Entitäten.

## Entscheidung

**Ein** `PrüfschrittDurchführung`-Objekt pro ProzedurSchritt und Prüflauf.

Routine-Wiederholungen **akkumulieren Nachweise** in chronologischer Reihenfolge (Wellen). Jede Welle kann automatische und manuelle Nachweise enthalten.

- Keine separate Entität „Versuch" oder „Durchführungsversuch"
- Beurteilung bewertet **alle** Nachweise der Durchführung im Kontext der materialisierten Sollvorgaben
- Automatische Nachweise bleiben unveränderlich; neue Welle = neue Nachweise

Siehe Domain Model §4.16, §9.

## Konsequenzen

- Einfacheres Aggregate `Prueflauf` / `PruefschrittDurchfuehrung`
- ProtokollSnapshot kann Nachweise chronologisch darstellen
- UI kann Wellen visuell gruppieren (Darstellung, nicht separate Domain-Entität)

## Alternativen

- Explizite Versuchs-Entitäten: verworfen — mehr Komplexität ohne fachlichen Mehrwert in V1
- Neue PrüfschrittDurchführung pro Wiederholung: verworfen — verwässert „ein Schritt pro ProzedurSchritt"
