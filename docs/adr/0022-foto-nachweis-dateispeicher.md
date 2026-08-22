# ADR-0022: Foto-Nachweis und DateiSpeicherPort (Gate 8.3a)

## Status

Angenommen (Gate 8.3a)

## Kontext

`NachweisArt.FOTO` existiert in Domain und API, aber ohne Binärspeicher. Der generische JSON-Nachweis-Endpunkt akzeptiert `art: "foto"` mit beliebigem Payload — ohne echte Datei. ADR-0004 legt fest: Fotos bleiben im Dateispeicher; `ProtokollSnapshot` referenziert Nachweis-IDs, nicht Binärdaten.

Gate 8.1 (Identity/Auth) ist deferred. Gate 8.3b (Frontend Foto-Upload) benötigt einen stabilen Backend-Contract inkl. Download.

**Abgrenzung:** „Storage Exit“ für Legacy-`externes_kommando` (ADR-0018) ist ein völlig anderes Thema — keine Vermischung.

## Entscheidung

### Fachmodell

- **Foto ist ein Nachweis** (`NachweisArt.FOTO`) — kein eigenes Aggregate `Datei`/`Foto`.
- Binärdatei liegt **außerhalb** des Prüflauf-JSON (PostgreSQL-Payload).
- Foto-Nachweis-Payload enthält einen typisierten **`DateiVerweis`** (Value Object): `datei_id`, `mime_type`, `groesse_bytes`, optional `dateiname`.
- Kein Hash in Gate 8.3a (SHA-256 bleibt P1).
- Keine Binärdaten, Storage-Pfade, URLs oder Infrastruktur-Keys im Payload.

### Storage

- **`DateiSpeicherPort`** (Infrastrukturport): `speichern`, `lesen`, `loeschen`.
- V1-Adapter: **lokales Dateisystem** (`adapters/storage/lokal.py`).
- S3/Object Storage ist **später** als austauschbarer Adapter vorgesehen — nicht in Gate 8.3a.
- Konfiguration: `PWE_DATEI_STORAGE_PFAD` (Docker: Volume, z. B. `/var/pwe/dateien`).
- **Write-once:** bestehende `datei_id` wird nicht überschrieben; Kollision → klarer Fehler.
- Storage-Key = serverseitige `datei_id` (UUID); **niemals** Originaldateiname im Pfad.
- `loeschen` ist **idempotent** (fehlende Datei = kein Fehler) — ausschließlich für Compensation.

### Transaktion und Compensation

- Upload (Dateispeicher) und Prüflauf-Persistenz (PostgreSQL/In-Memory) sind **keine gemeinsame ACID-Transaktion**.
- Reihenfolge: alle lokal prüfbaren Vorbedingungen → `speichern` → Nachweis anlegen → `prueflauf_repo.save`.
- Bei Fehler nach erfolgreichem `speichern`: **Best-Effort** `loeschen(datei_id)`.
- Cleanup-Fehler werden geloggt; der **ursprüngliche Fehler bleibt dominant** — keine „Rollback erfolgreich“-Behauptung.

### API

| Methode | Pfad | Zweck |
|---------|------|-------|
| POST | `/prueflaeufe/{id}/schritte/{schritt_id}/nachweise/foto` | Multipart-Upload, erzeugt Foto-Nachweis |
| GET | `/prueflaeufe/{id}/nachweise/{nachweis_id}/datei` | Kontextgebundener Download |

- **Kein** globaler `GET /dateien/{datei_id}` ohne Prüflauf-/Nachweis-Kontext.
- Der generische JSON-Endpunkt `POST .../nachweise` darf **`NachweisArt.FOTO` nicht mehr** als frei konstruierten Foto-Nachweis erzeugen (HTTP 409, `foto_nur_per_multipart`).
- Andere Nachweisarten am JSON-Endpunkt bleiben unverändert.

### Fachliche Kontextvalidierung (Download)

Vor `lesen` prüft der Use Case: Prüflauf existiert, Nachweis gehört zum Prüflauf, Nachweis ist `FOTO`, Payload enthält gültigen `DateiVerweis`, Datei existiert im Storage.

Das ist **keine Authentifizierung** und keine Rollenprüfung (Gate 8.1). Dateien sind nur über die Application/API erreichbar, nicht direkt über das Storage-Verzeichnis.

### Dateitypen und Limits (V1)

| Regel | Wert |
|-------|------|
| MIME | `image/jpeg`, `image/png` |
| Max. Größe | 5 MiB (5 242 880 Bytes) |
| Magic-Byte-Check | Ja (JPEG/PNG), keine Imaging-Library |
| HEIC | Nein |
| PDF-Einbettung | Nein (Gate 8.3a) |

### Persistenz / Alembic

- **Keine** `datei`-Tabelle, kein BYTEA, keine Alembic-Migration.
- Datei-Metadaten liegen im bestehenden Nachweis-Payload des Prüflaufs.

### Nicht in Gate 8.3a

- `FotoNachweisEntfernen` / öffentlicher Delete-Endpunkt
- Auth (Gate 8.1)
- Frontend (Gate 8.3b)
- PDF-Foto-Einbettung
- HEIC-Konvertierung
- S3/Object Storage
- Storage Exit `externes_kommando`
- Retention / GC / automatische Bereinigung nach Abschluss

Nach Prüflauf-Abschluss bleiben Dateien persistent; bestehende Prüflauf-Immutability gilt unverändert.

## Konsequenzen

- Gate 8.3b kann Multipart-Upload und Inline-Download nutzen.
- Docker benötigt separates Volume für Dateidaten (Backup: DB + Datei-Volume gemeinsam).
- Tests: In-Memory-Adapter für Application; Contract-Tests für lokales FS.
- Neues ADR verbindlich für Implementierung und Review.

## Alternativen

- PostgreSQL BYTEA: verworfen — Medien extern (ADR-0004), Backup-Komplexität.
- Zwei-Schritt-Upload (Datei zuerst, dann JSON-Nachweis): verworfen — Orphan-Risiko.
- Freier JSON-Foto-Nachweis parallel: verworfen — Fake-Dateireferenzen, zwei Produktionswege.
