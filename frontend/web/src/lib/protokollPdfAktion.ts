/** PDF-Ausgabeaktionen für die AbschlussPage (Gate 8.4) — kein window.print(). */

/**
 * Öffnet das Protokoll-PDF im nativen Browser-Viewer (neuer Tab).
 * Nutzt Anchor+click statt window.open — unabhängig vom noopener-Rückgabewert.
 * Revoke verzögert, damit der Viewer die Blob-URL noch laden kann.
 */
export function openProtokollPdfInViewer(blob: Blob): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.target = "_blank";
  anchor.rel = "noopener noreferrer";
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  window.setTimeout(() => {
    URL.revokeObjectURL(url);
  }, 60_000);
}

/** Erzwingt Datei-Download — bestehendes Speichern-Verhalten. */
export function downloadProtokollPdfBlob(blob: Blob, dateiname: string): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = dateiname;
  anchor.click();
  URL.revokeObjectURL(url);
}
