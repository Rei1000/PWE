# ADR-0005: Sollvorgaben — Materialisierung bei Veröffentlichung

## Status

Accepted

## Kontext

Domain Model §12: Override-Kette Basisprodukt → Kundenprofil → Produktdefinition bei Schrittsollvorgaben noch offen.

## Entscheidung

Sollvorgaben werden **ausschließlich bei Veröffentlichung** aufgelöst und in `ProduktdefinitionsVersion` **materialisiert**.

Auflösungsreihenfolge (späterer Wert überschreibt):

1. Basisprodukt (Defaults)
2. Kundenprofil
3. Produktdefinition / ProzedurSchritt-spezifische Vorgaben

**Run Time:** Prüfausführung liest **nur** materialisierte Sollvorgaben aus der referenzierten Version — **keine** Live-Auflösung der Kette.

Materialisierte Struktur pro ProzedurSchritt: Map/Snapshot `(sollvorgabe_id → effektiver_wert/regel)`.

## Konsequenzen

- Beurteilung vergleicht Nachweise gegen feste Versionssnapshot-Daten
- Änderungen am Basisprodukt betreffen laufende Prüfläufe nicht
- Katalog-Aggregate müssen Veröffentlichungsakt implementieren

## Alternativen

- Live-Auflösung zur Laufzeit: verworfen — bricht Immutability der Versionsreferenz, Audit-Risiko
- Nur Produktdefinition ohne Kette: verworfen — widerspricht Domain Model (Basisprodukt, Kundenprofil)
