import { ApiError } from "@/adapters/api/client";

const CONFLICT_MESSAGES: Record<string, string> = {
  kommando_in_verwendung:
    "Das Kommando wird noch von einem offenen Entwurf oder einer Routine verwendet und kann nicht gelöscht werden.",
  routine_in_verwendung:
    "Die Routine wird noch von einem offenen Entwurf verwendet und kann nicht gelöscht werden.",
  vorlage_in_verwendung:
    "Die Vorlage wird noch von einem offenen Entwurf verwendet und kann nicht gelöscht werden.",
};

const DOMAIN_MESSAGES: Record<string, string> = {
  entwurf_nicht_gefunden: "Entwurf nicht gefunden — bitte die Produktdefinitions-ID prüfen.",
  prozedur_schritt_nicht_gefunden: "Der Schritt ist nicht mehr vorhanden.",
  vorlage_nicht_gefunden: "Die gewählte Vorlage wurde nicht gefunden — bitte eine andere Vorlage wählen.",
  automatisierung_doppelt_zugewiesen:
    "Automatisierung zuerst entfernen, bevor eine andere zugewiesen wird.",
  schritt_id_bereits_vorhanden: "Diese Schritt-ID ist im Entwurf bereits vergeben.",
  ungueltige_schritt_reihenfolge: "Die Reihenfolge ist ungültig — bitte die Seite neu laden.",
  externes_kommando_nicht_gefunden: "Das referenzierte Kommando wurde nicht gefunden.",
  routine_nicht_gefunden: "Die referenzierte Routine wurde nicht gefunden.",
  validation: "Die Eingaben sind unvollständig oder ungültig.",
  invariant_verletzt: "Die Aktion ist im aktuellen Zustand nicht zulässig.",
};

export function katalogConflictMessage(error: unknown): string | null {
  if (!(error instanceof ApiError) || error.status !== 409) return null;
  if (error.code && CONFLICT_MESSAGES[error.code]) {
    return CONFLICT_MESSAGES[error.code];
  }
  return error.message;
}

export function katalogDomainMessage(error: unknown): string | null {
  if (!(error instanceof ApiError)) return null;
  if (error.code && DOMAIN_MESSAGES[error.code]) {
    return DOMAIN_MESSAGES[error.code];
  }
  if (error.status === 422 && error.code === "validation") {
    return DOMAIN_MESSAGES.validation ?? null;
  }
  return null;
}

export function katalogErrorMessage(error: unknown): string {
  return (
    katalogDomainMessage(error) ??
    katalogConflictMessage(error) ??
    (error instanceof Error ? error.message : "Unbekannter Fehler")
  );
}
