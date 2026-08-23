/** Spiegelt Backend-Regeln (ADR-0022) — nur für Client-Komfortprüfung. */

export const MAX_FOTO_GROESSE_BYTES = 5 * 1024 * 1024;

export const ERLAUBTE_FOTO_MIME_TYPES = ["image/jpeg", "image/png"] as const;

export type ErlaubterFotoMimeType = (typeof ERLAUBTE_FOTO_MIME_TYPES)[number];

export function validateFotoDatei(file: File): string | null {
  if (file.size <= 0) {
    return "Die Datei ist leer.";
  }
  if (file.size > MAX_FOTO_GROESSE_BYTES) {
    return "Die Datei ist zu groß (max. 5 MiB).";
  }
  if (file.type && !ERLAUBTE_FOTO_MIME_TYPES.includes(file.type as ErlaubterFotoMimeType)) {
    return "Nur JPEG- und PNG-Dateien sind erlaubt.";
  }
  return null;
}
