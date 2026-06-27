# ADR-0008: PrueflaufAbschlussView — Integration Protokoll ↔ Prüfausführung

## Status

Accepted

## Kontext

Bounded Context Protokoll darf nicht vom Aggregate `Prueflauf` abhängen. `ProtokollSnapshot.aus_prueflauf()` verletzte die Context-Grenze.

## Entscheidung

**Published Language / Abschluss-View** in der Prüfausführung:

- `PrueflaufAbschlussView` und `SchrittAbschlussView` in `domain/pruefausfuehrung/abschluss_view.py`
- Immutable DTOs, erzeugt durch `Prueflauf.to_abschluss_view(pflicht_map)` **nach** Abschluss
- Protokoll-Context importiert **nur** `abschluss_view`, nicht `Prueflauf`
- `ProtokollSnapshot.aus_abschluss(view)` erzeugt den Snapshot

Kein Domain Event in V1 — View reicht für synchronen Slice; Events bei Persistenz/Event-Bus später prüfen.

## Konsequenzen

- Klare Integrationsgrenze zwischen Contexts
- Application orchestriert: abschliessen → to_abschluss_view → ProtokollSnapshot

## Alternativen

- Domain Event `PrueflaufAbgeschlossen`: V2 bei async/Integration
- View in Application-Layer: verworfen — View ist fachliches Übergabeobjekt, gehört zur Prüfausführungsseite
