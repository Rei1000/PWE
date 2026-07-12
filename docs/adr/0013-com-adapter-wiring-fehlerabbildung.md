# ADR-0013: COM-Adapter-Wiring und Fehlerabbildung (Gate 7.3c)

## Status

Akzeptiert (Gate 7.3c)

## Kontext

Gate 7.3b stellt die HTTP-Ausführung materialisierter Kommandos bereit. Der Standardadapter ist `SimuliertesExternesKommandoPort`. Für Ergometer-Arbeitsplätze muss der bestehende `ComExternesKommandoPort` produktionsfähig werden: serieller Transport, Timeout, Transportfehler — ohne Domain- oder API-Leaks.

Domain Model §4.11: technische Übertragung ist **nicht** Domänenbestandteil. Rohantworten werden als Nachweise gespeichert, wenn die Ausführung fachlich erfolgreich war.

## Entscheidung

### Adapterwahl nur in der Composition Root

- Zentrale Factory: `api/kommando_wiring.py` → `create_kommando_port()`
- Konfiguration über Umgebungsvariablen:
  - `EXTERNES_KOMMANDO_ADAPTER=simulation|com` (Default: `simulation`)
  - bei `com`: `SERIELL_PORT`, `SERIELL_BAUDRATE`, `SERIELL_TIMEOUT_MS`
- Ungültige oder unvollständige Konfiguration → `KommandoAdapterConfigurationError` **beim Anwendungsstart**
- Kein stiller Fallback auf Simulation bei fehlerhafter COM-Konfiguration
- Keine request-gesteuerte Adapterwahl

### Schichtung

```
ExternesKommandoPort
  ← SimuliertesExternesKommandoPort (Default Dev/CI)
  ← ComExternesKommandoPort
        ← SeriellerTransport (Protocol)
              ← InMemorySeriellerTransport (Tests)
              ← PySerialTransport (Produktion, optional [com])
```

`ExternesKommandoPort` und Application bleiben unverändert.

### PySerial als technische Infrastruktur

- `pyserial` nur über optionales Backend-Extra `[com]`
- Lazy Import in `PySerialTransport`; Kern und CI ohne `[com]` bleiben lauffähig
- Keine Hardwaretests in CI

### Transport-Lifecycle (V1)

**Pro Kommando: Port öffnen → senden/empfangen → schließen** (in `finally`).

Begründung: einfachste robuste Variante ohne Connection-Pool, Hotplug oder geteilte Verbindungen zwischen Requests.

### Fehlerabbildung

Technische Fehler (Timeout, Verbindung, I/O, Decode, Parser) werden **im COM-Adapter** auf `ExternesKommandoAntwort(erfolgreich=False)` abgebildet — keine Exceptions in Domain/Application.

| Fall | `rohdaten` | `erfolgreich` |
|------|------------|---------------|
| Transport/Decode-Fehler | `""` | `False` |
| Geräte-`ERR …` | empfangene Geräteantwort | `False` |
| Parserfehler bei empfangenen Daten | empfangene Rohdaten | `False` |
| Erfolg | Geräteantwort | `True` |

Application mappt `erfolgreich=False` → `ExternesKommandoAdapterFehler` → HTTP 409, Code `externes_kommando_adapter_fehler`.

Technische Details nur ins Log — nicht in Nachweise oder öffentliche API-Antworten.

### Audit-Regel für Rohantwort-Nachweise (Domain §4.11, Invariante 16)

| Situation | Rohantwort-Nachweis | HTTP |
|-----------|---------------------|------|
| Transport/Decode ohne verwertbare Gerätedaten | **keiner** | 409 (Exception → Rollback) |
| Geräte-`ERR …` oder Parserfehler **mit** empfangenen Rohdaten | **ja** (unveränderlich, `erfolgreich=false` im Payload) | 409 **ohne** Exception — Request commit ([ADR-0011](../adr/0011-api-postgresql-unit-of-work.md)) |
| Erfolg | ROHANTWORT + EXTRAHIERTER_WERT | 201 |

**Trennung:** „Kommando fehlgeschlagen" ≠ „keine Evidenz". Fehlgeschlagene Ausführung mit Geräteantwort ist **beobachtete Evidenz** (Nachweis), getrennt von Beurteilung.

Application liefert `ExternesKommandoAusfuehrungErgebnis(nachweise, fehlgeschlagen)`. Die API mappt `fehlgeschlagen=True` auf HTTP 409 **mit** `nachweise` im Body — kein Domain-Exception-Wurf, damit die Request-Transaktion committed.

`ExternesKommandoAntwort.erfolgreich` plus `rohdaten` reicht — keine zusätzliche Fehlerklassifikation in der Domain.

### Kein automatischer Retry

- Kein Retry im Transport, COM-Adapter oder Application Use Case
- Jeder API-Aufruf = genau eine Kommandoausführung
- Wiederholungen später explizit über Routinen (Gate 7.3) oder erneuten API-Aufruf

## Konsequenzen

### Positiv

- Produktions-COM-Pfad ohne Domain-Änderung
- Simulation bleibt CI-Default
- Five-Year: weitere Transports implementieren `SeriellerTransport` oder eigenen Port

### Negativ / Grenzen

- Kein Connection-Pooling (V1); bei Bedarf späterer Slice
- Keine Hardwaretests — manuelle Arbeitsplatz-Verifikation bleibt nötig
- Parser V1 (`key=value`) bleibt im Adapter, nicht im Katalog

## Referenzen

- `docs/domain-model.md` §4.11
- Gate 7.3c in `docs/roadmap.md`
- `docs/technical-domain/pruefausfuehrung.md`
