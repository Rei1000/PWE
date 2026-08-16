import { useMutation, useQueryClient } from "@tanstack/react-query";

import { automatisierungAusfuehren } from "@/adapters/api/prueflaeufe";
import { prueflaufQueryKey } from "@/lib/queryClient";

/**
 * Gate 6.3b — Automatisierung ausführen (ADR-0016).
 *
 * - `retry: false`: Geräteaktionen sind nicht idempotent; kein Auto-Retry.
 * - HTTP 200 inkl. `fehlgeschlagen=true` ist Erfolg der Mutation (kein ApiError).
 * - Nach HTTP 200: Prüflauf-Read-Model invalidieren.
 * - Bei unklarem Netzwerkfehler: ebenfalls invalidieren (Geräteaktion könnte
 *   trotz verlorener Antwort gelaufen sein) — ohne erneute Ausführung.
 */
export function useAutomatisierungAusfuehren(prueflaufId: string, schrittId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => automatisierungAusfuehren(prueflaufId, schrittId),
    retry: false,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: prueflaufQueryKey(prueflaufId) });
    },
    onError: () => {
      // Unklarer Transport/Netzwerkfehler: Read Model aktualisieren, nicht erneut starten.
      void queryClient.invalidateQueries({ queryKey: prueflaufQueryKey(prueflaufId) });
    },
  });
}
