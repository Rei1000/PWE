# ADR-0010: Atomische Persistierung beim Prüflauf-Abschluss

## Status

Angenommen (Gate 7.0)

## Kontext

Beim Abschluss werden `Prueflauf` und `ProtokollSnapshot` persistiert. Bisher rief der Use Case zwei Repository-`save()`-Methoden nacheinander auf. PostgreSQL-Adapter committen pro Aufruf — ein Teilerfolg ist möglich.

Alternativen:

1. **Unit of Work** für alle Use Cases und Repositories
2. **Transaktionaler Application-Port** nur für den Abschluss
3. **Orchestrierung in der API** (zwei Calls)

## Entscheidung

**Option 2:** Neuer Port `PrueflaufAbschlussPersistenz` mit `speichern(prueflauf, snapshot)`.

- In-Memory: beide Saves synchron (bereits atomar im Prozess)
- PostgreSQL: eine Session, beide Writes, ein `commit` / `rollback`

## Begründung

- Gate 7.0 braucht nur Abschluss-Atomizität — minimaler Scope
- Gate 7.1 (API ↔ PostgreSQL Wiring) kann später auf **Unit of Work** erweitern, ohne Abschluss-Port zu brechen
- Application bleibt frei von SQLAlchemy-Session-Details

## Konsequenzen

- `PruefungAbschliessen` nutzt `PrueflaufAbschlussPersistenz` statt `ProtokollRepository.save()` direkt
- PostgreSQL-Repositories unterstützen `commit=False` für Teiloperationen innerhalb der Abschluss-Transaktion
- Weitere Use Cases committen weiterhin pro Repository-Save (bis UoW in 7.1)
