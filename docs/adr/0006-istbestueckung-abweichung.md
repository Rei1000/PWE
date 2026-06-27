# ADR-0006: Istbestückung — Abweichungen von Sollbestückung

## Status

Accepted

## Kontext

Domain Model §12: Verhalten bei fehlender oder zusätzlicher Komponente gegenüber materialisierter Sollbestückung unklar.

## Entscheidung

| Situation | Verhalten V1 |
|-----------|--------------|
| Komponente **fehlt** (laut Sollbestückung erwartet) | Als **Nachweis** (`Komponentenerfassung` negativ/fehlend) dokumentieren; betroffene ProzedurSchritte mit Aktivierungsregel auf diese Komponente/Option werden **nicht aktiv** oder als „nicht anwendbar" übersprungen (konfigurierbar am Schritt: Pflicht vs. optional) |
| **Zusätzliche** Komponente | Nachweis dokumentieren; aktiviert **keine** zusätzlichen Schritte automatisch — Aktivierung nur über materialisierte Aktivierungsregeln |
| Pflicht-Komponente fehlt bei Pflichtschritt | Beurteilung „nicht bestanden" → kann Prüflauf **ungültig** machen (Domain Model Invariante) |

Istbestückung ist Teil des Prüflaufs (Run Time), Sollbestückung der Version (Design Time).

**Slice V1 (minimal):** `erfasse_komponente()`, `fehlende_sollbestueckung()`, Ungültigkeit bei fehlender Sollbestückung beim Abschluss. Aktivierungsregeln für Schritte folgen später.

## Konsequenzen

- Kein automatisches Neuberechnen der Version bei Ist-Abweichung
- Aktivierungsregeln bleiben authoritative für Schritt-Sichtbarkeit

## Alternativen

- Laufzeit-Neuberechnung der Prozedur aus Istbestückung: verworfen — widerspricht Versionsimmutability
- Ignorieren fehlender Komponenten: verworfen — Audit-Lücke
