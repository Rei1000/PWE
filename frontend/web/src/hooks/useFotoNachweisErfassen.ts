import { useMutation, useQueryClient } from "@tanstack/react-query";

import { erfasseFotoNachweis } from "@/adapters/api/prueflaeufe";
import { prueflaufQueryKey } from "@/lib/queryClient";

/**
 * Foto-Nachweis-Upload (Gate 8.3b).
 * Invalidiert das Prüflauf-Read-Model nach Erfolg — kein Auto-Retry.
 */
export function useFotoNachweisErfassen(prueflaufId: string, schrittId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => erfasseFotoNachweis(prueflaufId, schrittId, file),
    retry: false,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: prueflaufQueryKey(prueflaufId) });
    },
  });
}
