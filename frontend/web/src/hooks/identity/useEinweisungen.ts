import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createEinweisung,
  listEinweisungen,
  widerrufenEinweisung,
} from "@/adapters/api/identityQualification";
import type { EinweisungAnlegenRequest } from "@/adapters/api/schemas/identity";
import { identityEinweisungenKey } from "@/lib/identityQueryKeys";

export function useEinweisungenQuery(benutzerId: string, versionId?: string) {
  return useQuery({
    queryKey: identityEinweisungenKey(benutzerId, versionId),
    queryFn: () => listEinweisungen(benutzerId, versionId || undefined),
    enabled: Boolean(benutzerId),
  });
}

export function useCreateEinweisungMutation(benutzerId: string, versionId?: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: EinweisungAnlegenRequest) => createEinweisung(body),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: identityEinweisungenKey(benutzerId, versionId),
      });
      queryClient.invalidateQueries({
        queryKey: ["identity", "einweisungen", benutzerId],
      });
    },
  });
}

export function useWiderrufenEinweisungMutation(benutzerId: string, versionId?: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (einweisungId: string) => widerrufenEinweisung(einweisungId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: identityEinweisungenKey(benutzerId, versionId),
      });
      queryClient.invalidateQueries({
        queryKey: ["identity", "einweisungen", benutzerId],
      });
    },
  });
}
