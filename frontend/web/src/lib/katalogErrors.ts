import { ApiError } from "@/adapters/api/client";

const CONFLICT_MESSAGES: Record<string, string> = {
  kommando_in_verwendung:
    "Das Kommando wird noch von einem offenen Entwurf oder einer Routine verwendet und kann nicht gelöscht werden.",
  routine_in_verwendung:
    "Die Routine wird noch von einem offenen Entwurf verwendet und kann nicht gelöscht werden.",
  vorlage_in_verwendung:
    "Die Vorlage wird noch von einem offenen Entwurf verwendet und kann nicht gelöscht werden.",
};

export function katalogConflictMessage(error: unknown): string | null {
  if (!(error instanceof ApiError) || error.status !== 409) return null;
  if (error.code && CONFLICT_MESSAGES[error.code]) {
    return CONFLICT_MESSAGES[error.code];
  }
  return error.message;
}
