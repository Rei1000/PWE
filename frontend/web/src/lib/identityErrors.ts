import { ApiError } from "@/adapters/api/client";

const MESSAGES: Record<string, string> = {
  letzter_administrator_verletzt:
    "Mindestens ein aktiver Administrator muss erhalten bleiben.",
  passwort_wechsel_erforderlich: "Bitte ändern Sie zuerst Ihr Passwort.",
  nicht_berechtigt: "Sie sind für diese Aktion nicht berechtigt.",
  einweisung_bereits_gueltig:
    "Für diesen Benutzer und diese Version existiert bereits eine gültige Einweisung.",
  invariant_verletzt: "Die Aktion ist im aktuellen Zustand nicht zulässig.",
  validation: "Die Eingaben sind unvollständig oder ungültig.",
};

export function identityErrorMessage(error: unknown): string | null {
  if (!(error instanceof ApiError)) return null;
  if (error.code && MESSAGES[error.code]) {
    return MESSAGES[error.code];
  }
  return error.message;
}
