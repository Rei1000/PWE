import { ApiError } from "@/adapters/api/client";

const PRUEFLAUF_MESSAGES: Record<string, string> = {
  ungueltiger_dateityp: "Der Dateityp wird nicht unterstützt — bitte JPEG oder PNG wählen.",
  datei_zu_gross: "Die Datei ist zu groß (max. 5 MiB).",
  datei_speicherung_fehlgeschlagen: "Die Datei konnte nicht gespeichert werden.",
  datei_nicht_gefunden: "Die Foto-Datei wurde nicht gefunden.",
  nachweis_kein_foto: "Der Nachweis ist kein Foto-Nachweis.",
  nachweis_nicht_gefunden: "Der Nachweis wurde nicht gefunden.",
  prueflauf_nicht_gefunden: "Der Prüflauf wurde nicht gefunden.",
  foto_nur_per_multipart: "Foto-Nachweise werden ausschließlich über den Foto-Upload erfasst.",
  invariant_verletzt: "Die Aktion ist im aktuellen Zustand nicht zulässig.",
};

export function prueflaufErrorMessage(error: unknown): string | null {
  if (!(error instanceof ApiError)) {
    return null;
  }
  if (error.code && PRUEFLAUF_MESSAGES[error.code]) {
    return PRUEFLAUF_MESSAGES[error.code];
  }
  if (error.status === 404) {
    return PRUEFLAUF_MESSAGES.nachweis_nicht_gefunden ?? error.message;
  }
  if (error.status === 413) {
    return PRUEFLAUF_MESSAGES.datei_zu_gross ?? error.message;
  }
  if (error.status === 415) {
    return PRUEFLAUF_MESSAGES.ungueltiger_dateityp ?? error.message;
  }
  if (error.status === 503) {
    return PRUEFLAUF_MESSAGES.datei_speicherung_fehlgeschlagen ?? error.message;
  }
  return null;
}
