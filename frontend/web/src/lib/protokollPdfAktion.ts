/** PDF-Ausgabeaktionen für die AbschlussPage (Gate 8.4) — kein window.print(). */

export type OpenProtokollPdfResult =
  | { ok: true }
  | { ok: false; reason: "popup_blocked" };

/**
 * Öffnet das Protokoll-PDF im nativen Browser-Viewer (neuer Tab).
 * Revoke verzögert, damit der Viewer die Blob-URL noch laden kann.
 */
export function openProtokollPdfInViewer(blob: Blob): OpenProtokollPdfResult {
  const url = URL.createObjectURL(blob);
  const opened = window.open(url, "_blank", "noopener,noreferrer");
  if (!opened) {
    URL.revokeObjectURL(url);
    return { ok: false, reason: "popup_blocked" };
  }
  window.setTimeout(() => {
    URL.revokeObjectURL(url);
  }, 60_000);
  return { ok: true };
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
